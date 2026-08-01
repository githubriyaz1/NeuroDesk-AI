import json
from pathlib import Path
from typing import Any, Dict, List
import openpyxl
from app.services.metadata_extractors.base import BaseMetadataExtractor


class ExcelMetadataExtractor(BaseMetadataExtractor):
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = (extension or "").lower()
        mime = (mime_type or "").lower()
        return ext in [".xlsx", ".xls", ".xlsm"] or "spreadsheet" in mime or "excel" in mime

    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        meta = []
        try:
            wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
            sheet_names = wb.sheetnames
            active_sheet = wb.active.title if wb.active else (sheet_names[0] if sheet_names else "Sheet1")

            meta.append({"key": "sheet_count", "value": len(sheet_names), "value_type": "number"})
            meta.append({"key": "sheet_names", "value": json.dumps(sheet_names), "value_type": "json"})
            meta.append({"key": "active_sheet", "value": str(active_sheet), "value_type": "string"})
            wb.close()
        except Exception:
            meta.append({"key": "sheet_count", "value": 0, "value_type": "number"})
            meta.append({"key": "sheet_names", "value": json.dumps([]), "value_type": "json"})
            meta.append({"key": "active_sheet", "value": "None", "value_type": "string"})

        return meta
