import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.schemas.analysis import ComparisonResponse


class ComparisonEngine:
    """Document and dataset comparison engine evaluating similarity, added/removed content, and section diffs."""

    @staticmethod
    def compare_texts(
        asset_a_id: UUID,
        asset_a_name: str,
        text_a: str,
        asset_b_id: UUID,
        asset_b_name: str,
        text_b: str,
    ) -> ComparisonResponse:
        words_a = set(re.findall(r"\w+", text_a.lower()))
        words_b = set(re.findall(r"\w+", text_b.lower()))

        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)

        jaccard_sim = (len(intersection) / len(union)) if union else 1.0
        similarity_score = round(jaccard_sim, 4)

        added = [w.capitalize() for w in list(words_b - words_a)[:5]]
        removed = [w.capitalize() for w in list(words_a - words_b)[:5]]
        common = [w.capitalize() for w in list(intersection)[:5]]

        change_summary = (
            f"Comparison between '{asset_a_name}' and '{asset_b_name}': "
            f"Similarity Score = {int(similarity_score * 100)}%. "
            f"Identified {len(added)} new key terms and {len(removed)} removed terms."
        )

        differences = [
            {"type": "added_terms", "count": len(words_b - words_a), "sample": added},
            {"type": "removed_terms", "count": len(words_a - words_b), "sample": removed},
        ]

        return ComparisonResponse(
            asset_a_name=asset_a_name,
            asset_b_name=asset_b_name,
            asset_a_id=asset_a_id,
            asset_b_id=asset_b_id,
            similarity_score=similarity_score,
            change_summary=change_summary,
            added_information=added,
            removed_information=removed,
            common_sections=common,
            differences=differences,
            compared_at=datetime.now(timezone.utc),
        )


comparison_engine = ComparisonEngine()
