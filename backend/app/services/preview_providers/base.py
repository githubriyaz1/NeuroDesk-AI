from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
from app.models.asset import Asset
from app.schemas.preview import PreviewType


class PreviewProvider(ABC):
    """Abstract Base Class for Universal Preview Engine Providers."""

    @property
    @abstractmethod
    def preview_type(self) -> PreviewType:
        """Returns the PreviewType enum value for this provider."""
        pass

    @abstractmethod
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        """Determines if this provider can process the given asset specifications."""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        """Extracts technical metadata relevant for preview display."""
        pass

    @abstractmethod
    def generate_preview(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        """Generates structured content payload for preview renderer."""
        pass

    def has_thumbnail(self, file_path: Path, asset: Asset) -> bool:
        """Returns True if a thumbnail image can be generated/served for this asset."""
        return False
