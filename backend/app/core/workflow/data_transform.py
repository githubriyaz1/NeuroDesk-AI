import re
from typing import Any, Dict, List, Optional, Union


def get_nested_value(data: Any, path: str) -> Any:
    """Safely traverses nested dictionary or list structures using dot-path notation."""
    if not path or data is None:
        return data

    parts = path.split(".")
    curr = data

    for part in parts:
        if curr is None:
            return None

        # Check for list indexing syntax, e.g. "items[0]"
        match = re.match(r"^(\w+)\[(\d+)\]$", part)
        if match:
            key, idx = match.group(1), int(match.group(2))
            if isinstance(curr, dict) and key in curr:
                curr = curr[key]
                if isinstance(curr, list) and 0 <= idx < len(curr):
                    curr = curr[idx]
                else:
                    return None
            else:
                return None
        elif isinstance(curr, dict) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(curr):
                curr = curr[idx]
            else:
                return None
        else:
            return None

    return curr


class DataTransformEvaluator:
    """Safe, rule-based data transformation evaluator without using arbitrary eval()."""

    @staticmethod
    def transform(operation: str, data: Any, config: Dict[str, Any]) -> Any:
        op = (operation or config.get("operation") or "extract").lower()

        if isinstance(data, dict) and "result" in data:
            data = data["result"]

        if op in ["extract", "json_extract"]:
            path = config.get("path") or config.get("field_path", "")
            return get_nested_value(data, path)

        elif op == "filter":
            field = config.get("field", "")
            operator = (config.get("operator") or "equals").lower()
            val = config.get("value")

            items = data if isinstance(data, list) else ([data] if data is not None else [])
            filtered = []

            for item in items:
                item_val = get_nested_value(item, field) if field else item
                if operator == "equals":
                    if item_val == val:
                        filtered.append(item)
                elif operator in ["not_equals", "neq"]:
                    if item_val != val:
                        filtered.append(item)
                elif operator == "contains":
                    if val is not None and item_val is not None and str(val).lower() in str(item_val).lower():
                        filtered.append(item)
                elif operator in ["greater_than", "gt"]:
                    if item_val is not None and val is not None and float(item_val) > float(val):
                        filtered.append(item)
                elif operator in ["less_than", "lt"]:
                    if item_val is not None and val is not None and float(item_val) < float(val):
                        filtered.append(item)
                elif operator == "in":
                    if isinstance(val, list) and item_val in val:
                        filtered.append(item)

            return filtered

        elif op == "select":
            fields = config.get("fields", [])
            if isinstance(data, list):
                return [{k: v for k, v in item.items() if k in fields} for item in data if isinstance(item, dict)]
            elif isinstance(data, dict):
                return {k: v for k, v in data.items() if k in fields}
            return data

        elif op == "rename":
            mapping = config.get("mapping", {})
            if isinstance(data, dict):
                return {mapping.get(k, k): v for k, v in data.items()}
            elif isinstance(data, list):
                return [{mapping.get(k, k): v for k, v in item.items()} for item in data if isinstance(item, dict)]
            return data

        elif op == "sort":
            field = config.get("field", "")
            reverse = config.get("order", "asc").lower() == "desc"
            if isinstance(data, list):
                return sorted(
                    data,
                    key=lambda x: get_nested_value(x, field) if isinstance(x, dict) else x,
                    reverse=reverse,
                )
            return data

        elif op in ["format", "template"]:
            template = config.get("template", "{input}")
            res = template.replace("{input}", str(data or ""))
            if isinstance(data, dict):
                for k, v in data.items():
                    res = res.replace(f"{{{k}}}", str(v))
            return res

        elif op == "regex_extract":
            pattern = config.get("pattern", r"(.*)")
            target = str(data or "")
            match = re.search(pattern, target)
            if match:
                return match.group(1) if match.groups() else match.group(0)
            return None

        elif op == "aggregate":
            agg_type = (config.get("aggregation_type") or config.get("type") or "count").lower()
            field = config.get("field")
            items = data if isinstance(data, list) else []

            if field:
                values = [float(get_nested_value(i, field)) for i in items if get_nested_value(i, field) is not None]
            else:
                values = [float(i) for i in items if isinstance(i, (int, float))]

            if agg_type == "count":
                return len(items)
            elif agg_type == "sum":
                return sum(values)
            elif agg_type == "average":
                return sum(values) / len(values) if values else 0.0
            elif agg_type == "min":
                return min(values) if values else 0.0
            elif agg_type == "max":
                return max(values) if values else 0.0

        return data


data_transform_evaluator = DataTransformEvaluator()
