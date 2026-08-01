import csv
from pathlib import Path
from typing import Any, Dict, List, Tuple
from app.core.logging import logger
from app.models.asset import Asset
from app.schemas.preview import PreviewType
from app.services.preview_providers.base import PreviewProvider


class CSVPreviewProvider(PreviewProvider):
    """Preview provider for CSV and delimiter-separated files."""

    @property
    def preview_type(self) -> PreviewType:
        return PreviewType.CSV

    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = extension.lower().lstrip(".")
        mime = (mime_type or "").lower()
        return ext in ["csv", "tsv", "txt"] and ("csv" in mime or "text" in mime or asset_type == "SPREADSHEET")

    def _read_csv_sample(self, file_path: Path, max_rows: int = 50) -> Tuple[List[str], List[Dict[str, Any]], int]:
        headers: List[str] = []
        rows: List[Dict[str, Any]] = []
        total_rows = 0

        for encoding in ["utf-8", "latin-1"]:
            try:
                with open(file_path, mode="r", encoding=encoding, errors="replace") as f:
                    sample = f.read(4096)
                    f.seek(0)
                    delimiter = ","
                    if "\t" in sample and "," not in sample:
                        delimiter = "\t"
                    elif ";" in sample and "," not in sample:
                        delimiter = ";"

                    reader = csv.reader(f, delimiter=delimiter)
                    try:
                        raw_headers = next(reader)
                        headers = [h.strip() for h in raw_headers if h is not None]
                    except StopIteration:
                        return [], [], 0

                    for i, row in enumerate(reader):
                        total_rows += 1
                        if i < max_rows:
                            row_dict = {}
                            for col_idx, col_name in enumerate(headers):
                                val = row[col_idx] if col_idx < len(row) else ""
                                row_dict[col_name] = val
                            rows.append(row_dict)
                break
            except Exception as e:
                logger.warning(f"Error parsing CSV with encoding {encoding}: {e}")
                continue

        return headers, rows, total_rows

    def extract_metadata(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        headers, rows, total_rows = self._read_csv_sample(file_path, max_rows=1)
        return {
            "column_names": headers,
            "column_count": len(headers),
            "total_rows": total_rows,
            "sample_rows_count": len(rows),
        }

    def generate_preview(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        headers, rows, total_rows = self._read_csv_sample(file_path, max_rows=50)
        return {
            "columns": headers,
            "rows": rows,
            "column_count": len(headers),
            "total_rows": total_rows,
            "preview_rows_count": len(rows),
        }
