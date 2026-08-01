from typing import List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.asset import Asset
from app.schemas.preview import (
    AssetPreviewMetadataResponse,
    AssetPreviewResponse,
    ThumbnailResponse,
)
from app.services.asset_service import asset_service
from app.services.preview_providers import (
    CSVPreviewProvider,
    ExcelPreviewProvider,
    ImagePreviewProvider,
    PDFPreviewProvider,
    PreviewProvider,
    UnsupportedPreviewProvider,
)
from app.services.storage_service import storage_service


class PreviewService:
    """Universal Preview Engine (UPE) Service managing dynamic provider resolution."""

    def __init__(self):
        # Order matters: concrete specialized providers first, fallback last
        self.providers: List[PreviewProvider] = [
            PDFPreviewProvider(),
            CSVPreviewProvider(),
            ExcelPreviewProvider(),
            ImagePreviewProvider(),
        ]
        self.fallback_provider = UnsupportedPreviewProvider()

    def select_provider(self, asset: Asset) -> PreviewProvider:
        """Selects the appropriate PreviewProvider based on asset type, mime type, and extension."""
        for provider in self.providers:
            if provider.can_handle(asset.asset_type, asset.mime_type, asset.extension):
                return provider
        return self.fallback_provider

    async def get_preview(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetPreviewResponse:
        """Resolves asset ownership, selects provider, and generates structured preview payload."""
        asset = await asset_service.get_asset_model(db, user_id, asset_id, include_deleted=False)

        if not storage_service.file_exists(asset.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical asset file missing from storage.",
            )

        file_path = storage_service.get_absolute_path(asset.storage_path)
        provider = self.select_provider(asset)

        try:
            content = provider.generate_preview(file_path, asset)
            metadata = provider.extract_metadata(file_path, asset)

            return AssetPreviewResponse(
                asset_id=asset.id,
                asset_name=asset.name,
                preview_type=provider.preview_type,
                can_preview=provider.preview_type != self.fallback_provider.preview_type,
                mime_type=asset.mime_type,
                file_size=asset.file_size,
                content=content,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Error generating preview for asset {asset_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate preview for requested asset.",
            )

    async def get_metadata(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetPreviewMetadataResponse:
        """Resolves asset ownership and returns preview metadata."""
        asset = await asset_service.get_asset_model(db, user_id, asset_id, include_deleted=False)

        if not storage_service.file_exists(asset.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical asset file missing from storage.",
            )

        file_path = storage_service.get_absolute_path(asset.storage_path)
        provider = self.select_provider(asset)

        try:
            metadata = provider.extract_metadata(file_path, asset)
            has_thumb = provider.has_thumbnail(file_path, asset)

            return AssetPreviewMetadataResponse(
                asset_id=asset.id,
                asset_name=asset.name,
                asset_type=asset.asset_type,
                preview_type=provider.preview_type,
                can_preview=provider.preview_type != self.fallback_provider.preview_type,
                has_thumbnail=has_thumb,
                file_size=asset.file_size,
                mime_type=asset.mime_type,
                extension=asset.extension,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Error extracting metadata for asset {asset_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract preview metadata.",
            )

    async def get_thumbnail(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> Tuple[bool, str, any]:
        """Checks if thumbnail is available. If image, returns (is_image_stream, path, filename). Else JSON msg."""
        asset = await asset_service.get_asset_model(db, user_id, asset_id, include_deleted=False)

        if not storage_service.file_exists(asset.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical asset file missing from storage.",
            )

        file_path = storage_service.get_absolute_path(asset.storage_path)
        provider = self.select_provider(asset)

        if provider.has_thumbnail(file_path, asset) and asset.mime_type.startswith("image/"):
            return True, file_path, asset.original_filename, asset.mime_type

        return False, None, None, None


preview_service = PreviewService()
