from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.analysis.statistics_engine import statistics_engine
from app.schemas.analysis import ColumnStatistics, DatasetAnalysisResponse


class DatasetAnalyzer:
    """Tabular dataset analyzer for CSV and Excel assets."""

    def __init__(self):
        self.stats_engine = statistics_engine

    def analyze_dataset(
        self,
        asset_id: UUID,
        filename: str,
        mime_type: str,
        columns: List[str],
        rows_data: List[List[Any]],
    ) -> DatasetAnalysisResponse:
        total_rows = len(rows_data)
        total_cols = len(columns)

        col_summaries: List[ColumnStatistics] = []
        missing_count = 0

        for idx, col_name in enumerate(columns):
            col_values = [row[idx] if idx < len(row) else None for row in rows_data]
            col_stat = self.stats_engine.analyze_column(col_name, col_values)
            col_summaries.append(col_stat)
            missing_count += col_stat.null_count

        # Check duplicates
        seen_rows = set()
        dup_count = 0
        for r in rows_data:
            r_str = str(r)
            if r_str in seen_rows:
                dup_count += 1
            else:
                seen_rows.add(r_str)

        exec_summary = (
            f"Dataset Analysis for '{filename}': Total Rows={total_rows}, Total Columns={total_cols}, "
            f"Missing Values={missing_count}, Duplicate Rows={dup_count}."
        )

        insights = [
            f"Analyzed {total_cols} columns across {total_rows} records.",
            f"Data quality assessment: {missing_count} missing cell entries detected.",
        ]
        if dup_count > 0:
            insights.append(f"Found {dup_count} duplicate rows requiring deduplication.")

        return DatasetAnalysisResponse(
            asset_id=asset_id,
            filename=filename,
            mime_type=mime_type,
            total_rows=total_rows,
            total_columns=total_cols,
            missing_values_count=missing_count,
            duplicate_rows_count=dup_count,
            columns_summary=col_summaries,
            outliers_detected=[],
            correlation_highlights=[],
            executive_summary=exec_summary,
            key_insights=insights,
            analyzed_at=datetime.now(timezone.utc),
        )


dataset_analyzer = DatasetAnalyzer()
