from pathlib import Path
from typing import Any, Dict, List
from PIL import Image
from app.services.metadata_extractors.base import BaseMetadataExtractor


class ImageMetadataExtractor(BaseMetadataExtractor):
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = (extension or "").lower()
        mime = (mime_type or "").lower()
        return ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"] or mime.startswith("image/") or asset_type == "IMAGE"

    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        meta = []
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                aspect_ratio = round(width / height, 2) if height > 0 else 1.0
                dpi = img.info.get("dpi", (72, 72))
                if isinstance(dpi, tuple):
                    dpi_val = f"{dpi[0]}x{dpi[1]}"
                else:
                    dpi_val = str(dpi)

                meta.append({"key": "width", "value": width, "value_type": "number"})
                meta.append({"key": "height", "value": height, "value_type": "number"})
                meta.append({"key": "aspect_ratio", "value": aspect_ratio, "value_type": "number"})
                meta.append({"key": "dpi", "value": dpi_val, "value_type": "string"})
                meta.append({"key": "color_mode", "value": img.mode, "value_type": "string"})
                meta.append({"key": "format", "value": img.format or asset.extension.replace(".", "").upper(), "value_type": "string"})
        except Exception:
            meta.append({"key": "width", "value": 0, "value_type": "number"})
            meta.append({"key": "height", "value": 0, "value_type": "number"})

        return meta
