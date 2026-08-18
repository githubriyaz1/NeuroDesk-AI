from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis.comparison_engine import comparison_engine
from app.core.analysis.dataset_analyzer import dataset_analyzer
from app.core.analysis.document_analyzer import document_analyzer
from app.core.analysis.insight_generator import insight_generator
from app.core.analysis.recommendation_engine import recommendation_engine
from app.core.analysis.statistics_engine import statistics_engine
from app.core.analysis.summary_engine import summary_engine
from app.core.knowledge import knowledge_engine
from app.schemas.analysis import (
    AnalysisReportExportRequest,
    AnalysisReportExportResponse,
    ComparisonResponse,
    DatasetAnalysisResponse,
    DocumentAnalysisResponse,
    InsightItem,
)
from app.schemas.knowledge import KnowledgeQueryRequest


class AnalysisEngine:
    """Primary facade for AI Data Analyst & Document Intelligence.
    
    Architecture Rule: Integrates AnalysisEngine seamlessly with KnowledgeEngine to automatically
    retrieve relevant assets, metadata, citations, and prompt context for document analysis,
    dataset profiling, and comparative evaluations.
    """

    def __init__(self):
        self.doc_analyzer = document_analyzer
        self.data_analyzer = dataset_analyzer
        self.comp_engine = comparison_engine
        self.stats_engine = statistics_engine
        self.summary_eng = summary_engine
        self.insight_gen = insight_generator
        self.recom_engine = recommendation_engine
        self.knowledge_eng = knowledge_engine

    async def analyze_document_asset(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: UUID,
        filename: str,
        mime_type: str,
        content: str,
    ) -> DocumentAnalysisResponse:
        # Knowledge Engine Integration: query knowledge context & citations for asset
        req = KnowledgeQueryRequest(query=f"Analyze document {filename}", limit=5, asset_ids=[asset_id])
        kq = await self.knowledge_eng.query_knowledge(
            owner_id=owner_id,
            req=req,
            db_session=db,
        )

        res = self.doc_analyzer.analyze_document(
            asset_id=asset_id,
            filename=filename,
            mime_type=mime_type,
            text_content=content,
        )

        # Attach knowledge citations & context recommendations
        if kq.citations:
            res.recommendations.append(f"Retrieved {len(kq.citations)} relevant citations from Knowledge Engine.")

        return res

    async def analyze_dataset_asset(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: UUID,
        filename: str,
        mime_type: str,
        columns: List[str],
        rows_data: List[List[Any]],
    ) -> DatasetAnalysisResponse:
        res = self.data_analyzer.analyze_dataset(
            asset_id=asset_id,
            filename=filename,
            mime_type=mime_type,
            columns=columns,
            rows_data=rows_data,
        )
        return res

    async def compare_asset_pair(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_a_id: UUID,
        asset_a_name: str,
        text_a: str,
        asset_b_id: UUID,
        asset_b_name: str,
        text_b: str,
    ) -> ComparisonResponse:
        return self.comp_engine.compare_texts(
            asset_a_id=asset_a_id,
            asset_a_name=asset_a_name,
            text_a=text_a,
            asset_b_id=asset_b_id,
            asset_b_name=asset_b_name,
            text_b=text_b,
        )

    def generate_ai_insights(
        self,
        title: str,
        summary: str,
    ) -> List[InsightItem]:
        return self.insight_gen.generate_comprehensive_insights(title=title, content_summary=summary)

    def export_analysis_report(self, req: AnalysisReportExportRequest) -> AnalysisReportExportResponse:
        fmt = req.format.lower()
        if fmt == "json":
            import json
            content = json.dumps(req.model_dump(), indent=2)
        else:
            # Default Markdown format
            content = f"# {req.title}\n\n"
            content += f"## Executive Summary\n{req.summary}\n\n"
            content += "## AI Key Insights\n"
            for ins in req.insights:
                content += f"- **[{ins.category.upper()}] {ins.title}**: {ins.description}\n"

        return AnalysisReportExportResponse(
            title=req.title,
            format=fmt,
            content=content,
        )


analysis_engine = AnalysisEngine()
