from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseMetadataExtractor(ABC):
    """Abstract Base Class for format-specific metadata extractors."""

    @abstractmethod
    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        """Determines if extractor can process requested asset."""
        pass

    @abstractmethod
    def extract(self, file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        """Extracts key-value metadata list from file path."""
        pass
