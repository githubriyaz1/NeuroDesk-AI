from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetStatus
from app.schemas.asset import AssetDetailResponse


class DiscoveryService:
    """Enterprise Business Logic Service for Discovery Platform curated collections."""

    async def get_recent_assets(
        self, db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> List[AssetDetailResponse]:
        """Returns user's most recently updated active assets."""
        stmt = (
            select(Asset)
            .where(Asset.owner_id == user_id, Asset.is_deleted == False)
            .order_by(Asset.updated_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [AssetDetailResponse.model_validate(a) for a in res.scalars().all()]

    async def get_favorite_assets(
        self, db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> List[AssetDetailResponse]:
        """Returns user's favorited active assets."""
        stmt = (
            select(Asset)
            .where(Asset.owner_id == user_id, Asset.is_deleted == False, Asset.is_favorite == True)
            .order_by(Asset.updated_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [AssetDetailResponse.model_validate(a) for a in res.scalars().all()]

    async def get_largest_assets(
        self, db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> List[AssetDetailResponse]:
        """Returns user's largest active files by file size."""
        stmt = (
            select(Asset)
            .where(Asset.owner_id == user_id, Asset.is_deleted == False)
            .order_by(Asset.file_size.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [AssetDetailResponse.model_validate(a) for a in res.scalars().all()]

    async def get_newest_assets(
        self, db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> List[AssetDetailResponse]:
        """Returns user's newest uploaded active assets."""
        stmt = (
            select(Asset)
            .where(Asset.owner_id == user_id, Asset.is_deleted == False)
            .order_by(Asset.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [AssetDetailResponse.model_validate(a) for a in res.scalars().all()]


discovery_service = DiscoveryService()
