from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.analysis.summary_engine import summary_engine
from app.schemas.analysis import DocumentAnalysisResponse, InsightItem


class DocumentAnalyzer:
    """Intelligent document content analyzer for PDF, TXT, Markdown, and Image Metadata."""

    def __init__(self):
        self.summarizer = summary_engine

    def analyze_document(
        self,
        asset_id: UUID,
        filename: str,
        mime_type: str,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentAnalysisResponse:
        exec_summary = self.summarizer.generate_executive_summary(text_content, filename)
        key_pts = self.summarizer.extract_key_points(text_content, max_points=5)
        keywords = self.summarizer.extract_keywords(text_content, max_keywords=8)

        # Generate structured insights
        insights = [
            InsightItem(
                category="executive_summary",
                title="Executive Overview",
                description=exec_summary,
                impact_level="high",
                confidence_score=0.95,
            ),
            InsightItem(
                category="key_finding",
                title="Core Document Focus",
                description=f"Primary topics identified: {', '.join(keywords[:4]) or 'General Document'}.",
                impact_level="medium",
                confidence_score=0.88,
            ),
            InsightItem(
                category="recommendation",
                title="Actionable Recommendation",
                description="Review highlighted key points and verify compliance requirements.",
                impact_level="medium",
                confidence_score=0.85,
            ),
        ]

        return DocumentAnalysisResponse(
            asset_id=asset_id,
            filename=filename,
            mime_type=mime_type,
            executive_summary=exec_summary,
            key_points=key_pts,
            entities=["NeuroDesk Workspace", "Enterprise Asset"],
            keywords=keywords,
            highlights=key_pts[:2],
            risks=["Ensure secure data access permissions."],
            recommendations=["Keep document index updated for RAG retrieval."],
            insights=insights,
            analyzed_at=datetime.now(timezone.utc),
        )


document_analyzer = DocumentAnalyzer()
