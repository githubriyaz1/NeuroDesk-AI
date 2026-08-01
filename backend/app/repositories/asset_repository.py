from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetStatus


class AssetRepository:
    """Repository handling all database persistence operations for Asset models."""

    async def create(self, db: AsyncSession, asset: Asset) -> Asset:
        """Persists a new Asset entity into the database."""
        db.add(asset)
        await db.flush()
        await db.refresh(asset)
        return asset

    async def get_by_id(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID, include_deleted: bool = False
    ) -> Optional[Asset]:
        """Queries asset by ID and owner_id."""
        stmt = select(Asset).where(Asset.id == asset_id, Asset.owner_id == user_id)
        if not include_deleted:
            stmt = stmt.where(Asset.is_deleted == False)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_checksum_and_size(
        self, db: AsyncSession, user_id: UUID, checksum: str, file_size: int
    ) -> Optional[Asset]:
        """Finds existing active asset with matching SHA256 checksum and size for duplicate detection."""
        stmt = select(Asset).where(
            Asset.owner_id == user_id,
            Asset.checksum == checksum,
            Asset.file_size == file_size,
            Asset.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession, asset: Asset) -> Asset:
        """Flushes and refreshes an updated Asset entity."""
        db.add(asset)
        await db.flush()
        await db.refresh(asset)
        return asset

    async def list_paginated(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        is_favorite: Optional[bool] = None,
        asset_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        include_deleted: bool = False,
    ) -> Tuple[List[Asset], int]:
        """Returns paginated assets list and total item count for the specified user."""
        stmt = select(Asset).where(Asset.owner_id == user_id)

        if not include_deleted:
            stmt = stmt.where(Asset.is_deleted == False)
        if is_favorite is not None:
            stmt = stmt.where(Asset.is_favorite == is_favorite)
        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type.upper())
        if status_filter:
            stmt = stmt.where(Asset.status == status_filter.upper())

        # Count total records matching criteria
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply sorting
        sort_col = getattr(Asset, sort_by, Asset.created_at)
        if sort_dir.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        # Apply pagination limit & offset
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        assets = result.scalars().all()

        return assets, total

    async def get_user_statistics_aggregates(
        self, db: AsyncSession, user_id: UUID
    ) -> dict:
        """Executes aggregated database queries calculating total storage and counts."""
        stmt = select(Asset).where(Asset.owner_id == user_id)
        result = await db.execute(stmt)
        all_assets = result.scalars().all()

        total_assets = len([a for a in all_assets if not a.is_deleted])
        ready_assets = len([a for a in all_assets if a.status == AssetStatus.READY.value and not a.is_deleted])
        processing_assets = len([a for a in all_assets if a.status == AssetStatus.PROCESSING.value and not a.is_deleted])
        deleted_count = len([a for a in all_assets if a.is_deleted])
        favorite_count = len([a for a in all_assets if a.is_favorite and not a.is_deleted])
        total_storage_bytes = sum(a.file_size for a in all_assets if not a.is_deleted)

        active_assets = [a for a in all_assets if not a.is_deleted]
        newest_upload = max((a.created_at for a in active_assets), default=None)
        largest_size = max((a.file_size for a in active_assets), default=0)

        assets_by_type = {}
        assets_by_status = {}

        for a in all_assets:
            if not a.is_deleted:
                assets_by_type[a.asset_type] = assets_by_type.get(a.asset_type, 0) + 1
                assets_by_status[a.status] = assets_by_status.get(a.status, 0) + 1

        return {
            "total_assets": total_assets,
            "ready_assets": ready_assets,
            "processing_assets": processing_assets,
            "deleted_assets": deleted_count,
            "favorite_assets": favorite_count,
            "total_storage_used_bytes": total_storage_bytes,
            "newest_upload_timestamp": newest_upload,
            "largest_asset_size_bytes": largest_size,
            "asset_count_by_type": assets_by_type,
            "assets_by_status": assets_by_status,
        }


asset_repository = AssetRepository()
