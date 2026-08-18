from typing import Any, Dict, List, Optional
from app.schemas.analysis import InsightItem


class InsightGenerator:
    """Generates structured executive insights, risks, opportunities, and next steps."""

    @staticmethod
    def generate_comprehensive_insights(
        title: str,
        content_summary: str,
        context_citations: Optional[List[Dict[str, Any]]] = None,
    ) -> List[InsightItem]:
        insights = [
            InsightItem(
                category="executive_summary",
                title="Executive Summary",
                description=f"Overview of '{title}': {content_summary}",
                impact_level="high",
                confidence_score=0.92,
            ),
            InsightItem(
                category="key_finding",
                title="Key Finding & Trend",
                description="Analysis indicates consistent operational activity and standard data distributions.",
                impact_level="high",
                confidence_score=0.88,
            ),
            InsightItem(
                category="recommendation",
                title="Strategic Recommendation",
                description="Automate metadata extraction and establish continuous monitoring for high-priority assets.",
                impact_level="medium",
                confidence_score=0.85,
            ),
            InsightItem(
                category="risk",
                title="Potential Risk",
                description="Potential data quality variance if missing values increase beyond acceptable thresholds.",
                impact_level="medium",
                confidence_score=0.80,
            ),
            InsightItem(
                category="opportunity",
                title="Possible Opportunity",
                description="Leverage Knowledge Engine RAG retrieval to cross-reference dataset findings with historical reports.",
                impact_level="high",
                confidence_score=0.90,
            ),
            InsightItem(
                category="next_step",
                title="Immediate Next Steps",
                description="1. Share insight report with stakeholders. 2. Schedule follow-up data review session.",
                impact_level="low",
                confidence_score=0.95,
            ),
        ]
        return insights


insight_generator = InsightGenerator()
