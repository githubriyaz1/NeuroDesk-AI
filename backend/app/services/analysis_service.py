import re
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import analysis_engine
from app.repositories.asset_repository import asset_repository
from app.schemas.analysis import (
    AnalysisReportExportRequest,
    AnalysisReportExportResponse,
    ComparisonResponse,
    DatasetAnalysisResponse,
    DocumentAnalysisResponse,
    InsightItem,
)


class AnalysisService:
    """Service layer orchestrating AI Data Analyst capabilities, document analysis, dataset profiling, and intent detection."""

    def __init__(self):
        self.engine = analysis_engine

    @staticmethod
    def detect_analysis_intent(prompt: str) -> Dict[str, Any]:
        """Detects whether a user prompt implies an analysis, summary, dataset inquiry, or comparison request."""
        p_lower = prompt.lower()
        is_summary = any(k in p_lower for k in ["summarize", "summary", "overview", "executive summary", "key points"])
        is_comparison = any(k in p_lower for k in ["compare", "difference", "versus", "vs", "changes"])
        is_dataset = any(k in p_lower for k in ["missing values", "csv", "excel", "dataset", "columns", "rows", "statistics", "trend"])
        is_insights = any(k in p_lower for k in ["insight", "generate insights", "explain", "recommendation", "risk"])

        intent_type = "general"
        if is_comparison:
            intent_type = "compare"
        elif is_dataset:
            intent_type = "dataset_analysis"
        elif is_summary:
            intent_type = "summary"
        elif is_insights:
            intent_type = "insights"

        return {
            "intent_type": intent_type,
            "requires_analysis": intent_type != "general",
            "is_summary": is_summary,
            "is_comparison": is_comparison,
            "is_dataset": is_dataset,
        }

    async def analyze_document(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: UUID,
    ) -> DocumentAnalysisResponse:
        asset = await asset_repository.get_by_id(db, user_id=owner_id, asset_id=asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found or access denied.")

        dummy_text = f"Asset Name: {asset.filename}\nDescription: {asset.description or 'No description provided.'}\nType: {asset.mime_type}"
        return await self.engine.analyze_document_asset(
            db=db,
            owner_id=owner_id,
            asset_id=asset.id,
            filename=asset.filename,
            mime_type=asset.mime_type,
            content=dummy_text,
        )

    async def analyze_dataset(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: UUID,
    ) -> DatasetAnalysisResponse:
        asset = await asset_repository.get_by_id(db, user_id=owner_id, asset_id=asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found or access denied.")

        dummy_cols = ["ID", "Category", "Revenue", "Status", "Notes"]
        dummy_rows = [
            [1, "Product A", 12000.5, "Active", "Good"],
            [2, "Product B", 8500.0, "Active", None],
            [3, "Product C", None, "Pending", "Review"],
            [4, "Product A", 12000.5, "Active", "Good"],
        ]

        return await self.engine.analyze_dataset_asset(
            db=db,
            owner_id=owner_id,
            asset_id=asset.id,
            filename=asset.filename,
            mime_type=asset.mime_type,
            columns=dummy_cols,
            rows_data=dummy_rows,
        )

    async def compare_assets(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id_a: UUID,
        asset_id_b: UUID,
    ) -> ComparisonResponse:
        asset_a = await asset_repository.get_by_id(db, user_id=owner_id, asset_id=asset_id_a)
        asset_b = await asset_repository.get_by_id(db, user_id=owner_id, asset_id=asset_id_b)

        if not asset_a or not asset_b:
            raise ValueError("One or both assets not found or access denied.")

        text_a = f"{asset_a.filename} {asset_a.description or ''}"
        text_b = f"{asset_b.filename} {asset_b.description or ''}"

        return await self.engine.compare_asset_pair(
            db=db,
            owner_id=owner_id,
            asset_a_id=asset_a.id,
            asset_a_name=asset_a.filename,
            text_a=text_a,
            asset_b_id=asset_b.id,
            asset_b_name=asset_b.filename,
            text_b=text_b,
        )

    def generate_insights(self, title: str, summary: str) -> List[InsightItem]:
        return self.engine.generate_ai_insights(title=title, summary=summary)

    def export_report(self, req: AnalysisReportExportRequest) -> AnalysisReportExportResponse:
        return self.engine.export_analysis_report(req)


analysis_service = AnalysisService()
