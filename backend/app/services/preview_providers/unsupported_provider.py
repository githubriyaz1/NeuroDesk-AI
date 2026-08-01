from pathlib import Path
from typing import Any, Dict
from app.models.asset import Asset
from app.schemas.preview import PreviewType
from app.services.preview_providers.base import PreviewProvider


class UnsupportedPreviewProvider(PreviewProvider):
    """Fallback preview provider for unsupported file formats."""

    @property
    def preview_type(self) -> PreviewType:
        return PreviewType.UNSUPPORTED

    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        return True

    def extract_metadata(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        return {
            "title": asset.name,
            "original_filename": asset.original_filename,
            "extension": asset.extension,
            "mime_type": asset.mime_type,
            "file_size": asset.file_size,
            "message": f"In-browser preview is currently unavailable for '.{asset.extension.lstrip('.')}' files.",
        }

    def generate_preview(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        return {
            "can_preview": False,
            "reason": f"No native preview provider registered for extension '{asset.extension}'.",
            "message": "You can download the asset file directly to view it on your workstation.",
        }

    def has_thumbnail(self, file_path: Path, asset: Asset) -> bool:
        return False
