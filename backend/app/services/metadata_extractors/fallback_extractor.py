import os
from pathlib import Path
from typing import Any, Dict, List
from app.services.metadata_extractors.base import BaseMetadataExtractor


class FallbackMetadataExtractor(BaseMetadataExtractor):
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        return True

    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        meta = [
            {"key": "file_name", "value": asset.original_filename, "value_type": "string"},
            {"key": "mime_type", "value": asset.mime_type, "value_type": "string"},
            {"key": "extension", "value": asset.extension, "value_type": "string"},
        ]

        if os.path.exists(file_path):
            meta.append({"key": "file_size_bytes", "value": os.path.getsize(file_path), "value_type": "number"})

        return meta
