from typing import Any, Dict, List


class RecommendationEngine:
    """Generates actionable recommendations based on document and dataset analysis results."""

    @staticmethod
    def generate_recommendations(
        asset_type: str,
        missing_count: int = 0,
        duplicate_count: int = 0,
    ) -> List[str]:
        recs = []
        if missing_count > 0:
            recs.append(f"Impute or filter {missing_count} missing values before model training or reporting.")
        if duplicate_count > 0:
            recs.append(f"Execute deduplication to remove {duplicate_count} duplicate rows.")

        if "pdf" in asset_type.lower() or "text" in asset_type.lower():
            recs.append("Index document in Knowledge Engine for real-time RAG context retrieval.")
            recs.append("Verify key compliance clauses and executive summary highlights.")
        else:
            recs.append("Generate automated statistical plots and correlation matrix for numeric columns.")

        return recs


recommendation_engine = RecommendationEngine()
