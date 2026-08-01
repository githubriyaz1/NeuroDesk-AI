import csv
import json
from pathlib import Path
from typing import Any, Dict, List
from app.services.metadata_extractors.base import BaseMetadataExtractor


class CSVMetadataExtractor(BaseMetadataExtractor):
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = (extension or "").lower()
        mime = (mime_type or "").lower()
        return ext in [".csv", ".tsv"] or "csv" in mime or "tab-separated" in mime

    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        meta = []
        encoding_used = "utf-8"
        delimiter_used = ","

        content = None
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read(10000)
                    encoding_used = enc
                break
            except Exception:
                continue

        if not content:
            return [
                {"key": "row_count", "value": 0, "value_type": "number"},
                {"key": "column_count", "value": 0, "value_type": "number"},
                {"key": "encoding", "value": "unknown", "value_type": "string"},
            ]

        # Sniff delimiter
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(content)
            delimiter_used = dialect.delimiter
        except Exception:
            delimiter_used = "," if "," in content else "\t"

        headers = []
        row_count = 0
        try:
            with open(file_path, "r", encoding=encoding_used) as f:
                reader = csv.reader(f, delimiter=delimiter_used)
                for i, row in enumerate(reader):
                    if i == 0:
                        headers = row
                    row_count += 1
        except Exception:
            pass

        meta.append({"key": "row_count", "value": max(0, row_count - 1), "value_type": "number"})
        meta.append({"key": "column_count", "value": len(headers), "value_type": "number"})
        meta.append({"key": "headers", "value": json.dumps(headers), "value_type": "json"})
        meta.append({"key": "delimiter", "value": delimiter_used, "value_type": "string"})
        meta.append({"key": "encoding", "value": encoding_used, "value_type": "string"})

        return meta
