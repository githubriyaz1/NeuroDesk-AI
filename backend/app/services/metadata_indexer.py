from pathlib import Path
from typing import Any, Dict, List
from app.core.logging import logger
from app.services.metadata_extractors import (
    BaseMetadataExtractor,
    CSVMetadataExtractor,
    ExcelMetadataExtractor,
    FallbackMetadataExtractor,
    ImageMetadataExtractor,
    PDFMetadataExtractor,
)


class MetadataIndexer:
    """Indexer engine that orchestrates metadata extraction across pluggable extractors."""

    def __init__(self):
        self.extractors: List[BaseMetadataExtractor] = [
            PDFMetadataExtractor(),
            CSVMetadataExtractor(),
            ExcelMetadataExtractor(),
            ImageMetadataExtractor(),
        ]
        self.fallback = FallbackMetadataExtractor()

    def index_asset(self, abs_file_path: Path, asset: Any) -> List[Dict[str, Any]]:
        """Selects matching format extractor and extracts full metadata entries."""
        metadata_entries: List[Dict[str, Any]] = []

        # Find specific format extractor
        matched_extractor = None
        for ext in self.extractors:
            if ext.can_handle(asset.asset_type, asset.mime_type, asset.extension):
                matched_extractor = ext
                break

        if matched_extractor:
            try:
                entries = matched_extractor.extract(abs_file_path, asset)
                metadata_entries.extend(entries)
            except Exception as e:
                logger.error(f"Error in format metadata extraction for {asset.id}: {e}", exc_info=True)

        # Merge fallback metadata (basic file properties)
        try:
            fallback_entries = self.fallback.extract(abs_file_path, asset)
            # Add keys not already present
            existing_keys = {e["key"] for e in metadata_entries}
            for fe in fallback_entries:
                if fe["key"] not in existing_keys:
                    metadata_entries.append(fe)
        except Exception as e:
            logger.error(f"Error in fallback metadata extraction for {asset.id}: {e}", exc_info=True)

        return metadata_entries


metadata_indexer = MetadataIndexer()
