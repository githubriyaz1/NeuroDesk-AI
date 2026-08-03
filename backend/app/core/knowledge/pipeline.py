import asyncio
import time
from typing import Any, Dict, List, Optional
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

    def select_retrievers(self, query: str, requested_types: Optional[List[str]] = None) -> List[BaseRetriever]:
        """Selects target retrievers based on query intent or explicit requested list."""
        if requested_types:
            selected = [r for r_type, r in self._retrievers.items() if r_type in requested_types]
            if selected:
                return selected

        # By default return all standard active retrievers
        return list(self._retrievers.values())

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
        target_retrievers = self.select_retrievers(clean_query, retriever_types)

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
            total_found=len(ranked_docs),
            retrieval_latency_ms=latency_ms,
            retrievers_used=[r.retriever_type for r in target_retrievers],
        )


knowledge_pipeline = KnowledgePipeline()
