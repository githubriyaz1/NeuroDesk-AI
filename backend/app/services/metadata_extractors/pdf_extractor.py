import os
from pathlib import Path
from typing import Any, Dict, List
import pypdf
from app.services.metadata_extractors.base import BaseMetadataExtractor


class PDFMetadataExtractor(BaseMetadataExtractor):
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = (extension or "").lower()
        mime = (mime_type or "").lower()
        return ext == ".pdf" or "pdf" in mime or asset_type == "REPORT"

    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        meta = []
        try:
            reader = pypdf.PdfReader(str(file_path))
            meta.append({"key": "page_count", "value": len(reader.pages), "value_type": "number"})
            meta.append({"key": "is_encrypted", "value": reader.is_encrypted, "value_type": "boolean"})

            info = reader.metadata or {}
            title = info.get("/Title") or asset.name
            author = info.get("/Author") or "Unknown"
            producer = info.get("/Producer") or "Unknown"

            meta.append({"key": "title", "value": str(title), "value_type": "string"})
            meta.append({"key": "author", "value": str(author), "value_type": "string"})
            meta.append({"key": "producer", "value": str(producer), "value_type": "string"})
        except Exception:
            meta.append({"key": "page_count", "value": 0, "value_type": "number"})
            meta.append({"key": "is_encrypted", "value": False, "value_type": "boolean"})

        if os.path.exists(file_path):
            meta.append({"key": "file_size_bytes", "value": os.path.getsize(file_path), "value_type": "number"})

        return meta
