import math
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.analysis import ColumnStatistics


class StatisticsEngine:
    """Calculates comprehensive descriptive statistics, null percentages, and outlier detection hooks."""

    @staticmethod
    def calculate_numeric_stats(numbers: List[float]) -> Dict[str, Any]:
        """Calculates mean, median, mode, min, max, and standard deviation for numeric series."""
        if not numbers:
            return {"mean": None, "median": None, "mode": None, "min": None, "max": None, "std_dev": None}

        n = len(numbers)
        mean_val = sum(numbers) / n

        sorted_nums = sorted(numbers)
        if n % 2 == 1:
            median_val = sorted_nums[n // 2]
        else:
            median_val = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2.0

        # Mode calculation
        counts: Dict[float, int] = {}
        for x in numbers:
            counts[x] = counts.get(x, 0) + 1
        mode_val = max(counts, key=counts.get)

        # Standard Deviation
        variance = sum((x - mean_val) ** 2 for x in numbers) / max(n - 1, 1)
        std_dev = math.sqrt(variance)

        return {
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "mode": str(mode_val),
            "min": round(min(numbers), 4),
            "max": round(max(numbers), 4),
            "std_dev": round(std_dev, 4),
        }

    def analyze_column(self, name: str, values: List[Any]) -> ColumnStatistics:
        """Analyzes a column data series and returns ColumnStatistics."""
        total = len(values)
        null_count = sum(1 for v in values if v is None or v == "" or str(v).lower() == "null")
        null_pct = round((null_count / total * 100) if total > 0 else 0.0, 2)

        non_nulls = [v for v in values if v is not None and v != "" and str(v).lower() != "null"]
        unique_count = len(set(non_nulls))

        # Check if column is numeric
        numeric_vals = []
        for v in non_nulls:
            try:
                numeric_vals.append(float(v))
            except (ValueError, TypeError):
                pass

        is_numeric = len(numeric_vals) > (len(non_nulls) * 0.7) if non_nulls else False
        num_stats = self.calculate_numeric_stats(numeric_vals) if is_numeric else {}

        return ColumnStatistics(
            column_name=name,
            data_type="numeric" if is_numeric else "categorical",
            total_count=total,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            mean=num_stats.get("mean"),
            median=num_stats.get("median"),
            mode=num_stats.get("mode") if is_numeric else (str(non_nulls[0]) if non_nulls else None),
            min_value=num_stats.get("min"),
            max_value=num_stats.get("max"),
            std_dev=num_stats.get("std_dev"),
        )


statistics_engine = StatisticsEngine()
