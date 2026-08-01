from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.asset import Asset
from app.repositories.asset_repository import asset_repository
from app.repositories.metadata_repository import metadata_repository
from app.schemas.metadata import (
    AssetMetadataResponse,
    MetadataGroupSchema,
    MetadataItemSchema,
)
from app.services.metadata_indexer import metadata_indexer
from app.services.storage_service import storage_service


class MetadataService:
    """Enterprise Business Logic Service for Asset Metadata & Indexing Engine."""

    async def get_asset_with_ownership_check(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> Asset:
        """Internal helper verifying asset existence and owner authorization."""
        asset = await asset_repository.get_by_id(db, user_id, asset_id, include_deleted=False)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or access denied.",
            )
        return asset

    async def index_and_persist(self, db: AsyncSession, asset: Asset) -> List[dict]:
        """Indexes asset metadata via MetadataIndexer and persists records in database."""
        if not storage_service.file_exists(asset.storage_path):
            logger.warning(f"File missing during metadata indexing: {asset.storage_path}")
            return []

        abs_path = storage_service.get_absolute_path(asset.storage_path)
        extracted_entries = metadata_indexer.index_asset(abs_path, asset)

        records = await metadata_repository.upsert_metadata_entries(
            db=db, asset_id=asset.id, entries=extracted_entries
        )
        return [
            {
                "key": r.metadata_key,
                "value": r.metadata_value,
                "value_type": r.value_type,
                "extracted_at": r.extracted_at,
            }
            for r in records
        ]

    async def get_metadata(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetMetadataResponse:
        """Retrieves asset metadata grouped by logical categories."""
        asset = await self.get_asset_with_ownership_check(db, user_id, asset_id)

        records = await metadata_repository.get_metadata_by_asset_id(db, asset.id)

        # If no metadata stored yet, extract and index immediately
        if not records:
            await self.index_and_persist(db, asset)
            records = await metadata_repository.get_metadata_by_asset_id(db, asset.id)

        items = [MetadataItemSchema.model_validate(r) for r in records]

        # Categorize metadata items
        general_keys = {"file_name", "mime_type", "extension", "file_size_bytes"}
        general_items = [i for i in items if i.key in general_keys]
        format_items = [i for i in items if i.key not in general_keys]

        groups = []
        if format_items:
            groups.append(
                MetadataGroupSchema(
                    category=f"{asset.asset_type.capitalize()} Format Metadata",
                    items=format_items,
                )
            )

        groups.append(
            MetadataGroupSchema(
                category="General File Attributes",
                items=general_items if general_items else items,
            )
        )

        return AssetMetadataResponse(
            asset_id=asset.id,
            groups=groups,
            items=items,
            total_keys=len(items),
        )

    async def refresh_metadata(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetMetadataResponse:
        """Forces re-extraction and refresh of asset metadata."""
        asset = await self.get_asset_with_ownership_check(db, user_id, asset_id)
        await self.index_and_persist(db, asset)
        return await self.get_metadata(db, user_id, asset_id)


metadata_service = MetadataService()
