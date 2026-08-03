import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional


def parse_size_bytes(size_str: str) -> Optional[int]:
    """Converts strings like 10MB, 1MB, 500KB, 2GB to bytes."""
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?$", size_str.strip())
    if not m:
        return None
    val = float(m.group(1))
    unit = (m.group(2) or "B").upper()

    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
    }
    return int(val * units.get(unit, 1))


class QueryParser:
    """Parses advanced structured search queries containing type, size, status, date, and name filters."""

    def parse(self, raw_query: str) -> Dict[str, Any]:
        result = {
            "free_text": "",
            "asset_type": None,
            "is_favorite": None,
            "status": None,
            "min_size_bytes": None,
            "max_size_bytes": None,
            "created_after": None,
            "name_filter": None,
        }

        if not raw_query:
            return result

        tokens = raw_query.strip().split()
        free_text_parts = []
        now = datetime.now(timezone.utc)

        type_alias_map = {
            "pdf": "REPORT",
            "doc": "DOCUMENT",
            "docx": "DOCUMENT",
            "csv": "SPREADSHEET",
            "excel": "SPREADSHEET",
            "xlsx": "SPREADSHEET",
            "image": "IMAGE",
            "img": "IMAGE",
            "png": "IMAGE",
            "jpg": "IMAGE",
            "dataset": "DATASET",
            "parquet": "DATASET",
            "model": "MODEL",
            "prompt": "PROMPT",
            "audio": "AUDIO",
            "video": "VIDEO",
        }

        for token in tokens:
            token_lower = token.lower()

            if token_lower.startswith("type:"):
                val = token_lower.split("type:", 1)[1]
                result["asset_type"] = type_alias_map.get(val, val.upper())

            elif token_lower.startswith("favorite:"):
                val = token_lower.split("favorite:", 1)[1]
                result["is_favorite"] = val in ["true", "1", "yes"]

            elif token_lower.startswith("status:"):
                val = token_lower.split("status:", 1)[1]
                result["status"] = val.upper()

            elif token_lower.startswith("name:"):
                result["name_filter"] = token.split("name:", 1)[1]

            elif token_lower.startswith("size>"):
                val = token_lower.split("size>", 1)[1]
                result["min_size_bytes"] = parse_size_bytes(val)

            elif token_lower.startswith("size<"):
                val = token_lower.split("size<", 1)[1]
                result["max_size_bytes"] = parse_size_bytes(val)

            elif token_lower.startswith("created:"):
                val = token_lower.split("created:", 1)[1]
                if val in ["today"]:
                    result["created_after"] = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif val in ["this-week", "week"]:
                    result["created_after"] = now - timedelta(days=7)
                elif val in ["this-month", "month"]:
                    result["created_after"] = now - timedelta(days=30)

            else:
                free_text_parts.append(token)

        result["free_text"] = " ".join(free_text_parts)
        return result


query_parser = QueryParser()
