from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.asset import Asset
from app.models.asset_metadata import AssetMetadata
from app.schemas.knowledge import KnowledgeIndexItem


class KnowledgeRepository:
    """Repository handling database interactions for Knowledge Engine indexing and retrieval."""

    async def list_user_assets_for_indexing(
        self,
        db: AsyncSession,
        owner_id: UUID,
        limit: int = 100,
    ) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.owner_id == owner_id, Asset.is_deleted == False)
            .order_by(Asset.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_asset_with_metadata(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: UUID,
    ) -> Optional[Asset]:
        stmt = select(Asset).where(Asset.id == asset_id, Asset.owner_id == owner_id, Asset.is_deleted == False)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


knowledge_repo = KnowledgeRepository()
