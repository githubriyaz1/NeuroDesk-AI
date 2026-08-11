import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.core.knowledge.ranking import result_ranker
from app.core.knowledge.retrievers import (
    BaseRetriever,
    CSVRetriever,
    ExcelRetriever,
    FutureRetriever,
    ImageMetadataRetriever,
    MetadataRetriever,
    PDFRetriever,
    SearchRetriever,
)
from app.core.logging import logger
from app.schemas.knowledge import Citation, KnowledgeQueryResult, RetrievedDocument


class KnowledgePipeline:
    """Orchestrator for multi-retriever query preprocessing, parallel execution, ranking, and context packaging."""

    def __init__(self):
        self._retrievers: Dict[str, BaseRetriever] = {
            "pdf": PDFRetriever(),
            "csv": CSVRetriever(),
            "excel": ExcelRetriever(),
            "metadata": MetadataRetriever(),
            "search": SearchRetriever(),
            "image_metadata": ImageMetadataRetriever(),
            "future_extension": FutureRetriever(),
        }
        self.ranker = result_ranker

    def register_retriever(self, retriever: BaseRetriever) -> None:
        """Architecture Hook: Register new retrievers dynamically without modifying pipeline core."""
        self._retrievers[retriever.retriever_type] = retriever
        logger.info(f"Registered Knowledge Engine Retriever [{retriever.retriever_type}]")

    def preprocess_query(self, raw_query: str) -> str:
        """Cleans and normalizes query text for retriever execution."""
        clean = raw_query.strip()
        # Remove extra whitespace
        clean = " ".join(clean.split())
        return clean

    def select_retrievers(
        self,
        query: str,
        requested_types: Optional[List[str]] = None,
        attached_asset_types: Optional[List[str]] = None,
    ) -> Tuple[List[BaseRetriever], Any]:
        """Selects target retrievers based on IntentRouter confidence scoring and classification."""
        from app.core.routing.intent_router import intent_router
        decision = intent_router.route_query(query, requested_types, attached_asset_types)
        
        selected = [r for r_type, r in self._retrievers.items() if r_type in decision.target_retrievers]
        if not selected:
            selected = list(self._retrievers.values())
            
        return selected, decision

    async def execute_pipeline(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        min_confidence: float = 0.1,
        retriever_types: Optional[List[str]] = None,
        asset_ids: Optional[List[UUID]] = None,
        conversation_context: Optional[str] = None,
        db_session: Optional[Any] = None,
    ) -> KnowledgeQueryResult:
        start_time = time.time()
        clean_query = self.preprocess_query(query)

        attached_asset_types: List[str] = []
        if asset_ids and db_session:
            try:
                from app.models.asset import Asset
                from sqlalchemy import select
                res = await db_session.execute(
                    select(Asset.mime_type, Asset.extension, Asset.asset_type).where(
                        Asset.id.in_(asset_ids), Asset.is_deleted == False
                    )
                )
                for mime_type, ext, a_type in res.all():
                    if mime_type == "application/pdf" or (ext and ext.lower() == ".pdf") or a_type == "REPORT":
                        attached_asset_types.append("pdf")
                    elif mime_type in ["text/csv", "application/csv"] or (ext and ext.lower() == ".csv") or a_type == "SPREADSHEET":
                        attached_asset_types.append("csv")
                    elif (mime_type and "excel" in mime_type) or (ext and ext.lower() in [".xlsx", ".xls"]):
                        attached_asset_types.append("excel")
            except Exception as exc:
                logger.warning(f"Could not resolve attached asset types: {exc}")

        target_retrievers, decision = self.select_retrievers(clean_query, retriever_types, attached_asset_types)

        # 1. Parallel Retrieval via asyncio.gather
        tasks = [
            r.retrieve(
                query=clean_query,
                owner_id=owner_id,
                limit=limit,
                asset_ids=asset_ids,
                db_session=db_session,
            )
            for r in target_retrievers
        ]
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)

        raw_documents: List[RetrievedDocument] = []
        for r_type, res in zip([r.retriever_type for r in target_retrievers], results_nested):
            if isinstance(res, list):
                raw_documents.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"Retriever [{r_type}] failed during execution: {res}")

        # If a specific page number was targeted in PDF_PAGE intent, prioritize page-matched documents
        if decision.target_page is not None:
            page_docs = [d for d in raw_documents if d.page_number == decision.target_page]
            if page_docs:
                raw_documents = page_docs + [d for d in raw_documents if d.page_number != decision.target_page]

        # 2. Result Ranking & Deduplication
        ranked_docs = self.ranker.rank_and_deduplicate(
            documents=raw_documents,
            query=clean_query,
            conversation_context=conversation_context,
            min_confidence=min_confidence,
        )[:limit]

        # 3. Citation Generation
        citations: List[Citation] = [doc.to_citation() for doc in ranked_docs]

        # 4. Context Compression & Packaging
        packaged_context = self.ranker.compress_context(ranked_docs)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return KnowledgeQueryResult(
            query=clean_query,
            documents=ranked_docs,
            citations=citations,
            packaged_context=packaged_context,
            total_found=len(raw_documents),
            retrieval_latency_ms=latency_ms,
            retrievers_used=[r.retriever_type for r in target_retrievers],
        )


knowledge_pipeline = KnowledgePipeline()
