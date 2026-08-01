from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset_metadata import AssetMetadata


class MetadataRepository:
    """Repository handling database persistence operations for AssetMetadata entities."""

    async def get_metadata_by_asset_id(
        self, db: AsyncSession, asset_id: UUID
    ) -> List[AssetMetadata]:
        """Returns all metadata records associated with the asset_id."""
        stmt = select(AssetMetadata).where(AssetMetadata.asset_id == asset_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_metadata_entries(
        self, db: AsyncSession, asset_id: UUID, entries: List[Dict[str, Any]]
    ) -> List[AssetMetadata]:
        """Deletes existing metadata for asset and persists fresh extracted metadata entries."""
        now = datetime.now(timezone.utc)

        # Delete existing entries for this asset
        del_stmt = delete(AssetMetadata).where(AssetMetadata.asset_id == asset_id)
        await db.execute(del_stmt)

        created_records = []
        for item in entries:
            key = item.get("key")
            val = item.get("value")
            val_type = item.get("value_type", "string")

            record = AssetMetadata(
                asset_id=asset_id,
                metadata_key=key,
                metadata_value=str(val) if val is not None else None,
                value_type=val_type,
                extracted_at=now,
            )
            db.add(record)
            created_records.append(record)

        await db.flush()
        return created_records

    async def delete_metadata_by_asset_id(
        self, db: AsyncSession, asset_id: UUID
    ) -> None:
        """Deletes all metadata entries for an asset."""
        stmt = delete(AssetMetadata).where(AssetMetadata.asset_id == asset_id)
        await db.execute(stmt)
        await db.flush()


metadata_repository = MetadataRepository()
