from pathlib import Path
from typing import Any, Dict
from PIL import Image

from app.core.logging import logger
from app.models.asset import Asset
from app.schemas.preview import PreviewType
from app.services.preview_providers.base import PreviewProvider


class ImagePreviewProvider(PreviewProvider):
    """Preview provider for images (PNG, JPG, JPEG, WEBP, GIF, SVG)."""

    @property
    def preview_type(self) -> PreviewType:
        return PreviewType.IMAGE

    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = extension.lower().lstrip(".")
        mime = (mime_type or "").lower()
        return ext in ["png", "jpg", "jpeg", "webp", "gif", "svg"] or mime.startswith("image/") or asset_type == "IMAGE"

    def extract_metadata(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format or asset.extension.lstrip(".").upper()
                dpi = img.info.get("dpi", (72, 72))

                aspect_ratio = round(width / height, 2) if height > 0 else 1.0

                return {
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}",
                    "aspect_ratio": aspect_ratio,
                    "color_mode": mode,
                    "format": format_name,
                    "dpi": dpi[0] if isinstance(dpi, tuple) else dpi,
                    "file_size": asset.file_size,
                    "mime_type": asset.mime_type,
                }
        except Exception as e:
            logger.warning(f"Failed to extract image metadata for {file_path}: {e}")
            return {
                "width": 0,
                "height": 0,
                "resolution": "Unknown",
                "aspect_ratio": 1.0,
                "color_mode": "RGB",
                "format": asset.extension.lstrip(".").upper(),
                "file_size": asset.file_size,
                "mime_type": asset.mime_type,
            }

    def generate_preview(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        meta = self.extract_metadata(file_path, asset)
        return {
            "dimensions": {
                "width": meta["width"],
                "height": meta["height"],
                "aspect_ratio": meta["aspect_ratio"],
            },
            "format": meta["format"],
            "color_mode": meta["color_mode"],
            "mime_type": asset.mime_type,
        }

    def has_thumbnail(self, file_path: Path, asset: Asset) -> bool:
        return True
