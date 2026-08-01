from pathlib import Path
from typing import Any, Dict
from pypdf import PdfReader

from app.core.logging import logger
from app.models.asset import Asset
from app.schemas.preview import PreviewType
from app.services.preview_providers.base import PreviewProvider


class PDFPreviewProvider(PreviewProvider):
    """Preview provider for PDF documents."""

    @property
    def preview_type(self) -> PreviewType:
        return PreviewType.PDF

    def can_handle(self, asset_type: str, mime_type: str, extension: str) -> bool:
        ext = extension.lower().lstrip(".")
        mime = (mime_type or "").lower()
        return ext == "pdf" or "pdf" in mime or asset_type == "REPORT" and ext == "pdf"

    def extract_metadata(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        try:
            reader = PdfReader(str(file_path))
            meta = reader.metadata or {}
            
            title = meta.title if hasattr(meta, "title") and meta.title else None
            author = meta.author if hasattr(meta, "author") and meta.author else None
            
            return {
                "title": title or asset.name,
                "author": author or "Unknown",
                "page_count": len(reader.pages),
                "is_encrypted": reader.is_encrypted,
                "file_size": asset.file_size,
            }
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata for {file_path}: {e}")
            return {
                "title": asset.name,
                "author": "Unknown",
                "page_count": 0,
                "is_encrypted": False,
                "file_size": asset.file_size,
            }

    def generate_preview(self, file_path: Path, asset: Asset) -> Dict[str, Any]:
        metadata = self.extract_metadata(file_path, asset)
        text_snippet = ""
        try:
            reader = PdfReader(str(file_path))
            if len(reader.pages) > 0 and not reader.is_encrypted:
                text_snippet = reader.pages[0].extract_text()[:1000]
        except Exception as e:
            logger.warning(f"Failed to extract text snippet from PDF {file_path}: {e}")

        return {
            "title": metadata["title"],
            "author": metadata["author"],
            "page_count": metadata["page_count"],
            "sample_text": text_snippet,
            "can_preview": True,
        }

    def has_thumbnail(self, file_path: Path, asset: Asset) -> bool:
        return True
