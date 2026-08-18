from typing import Any, Dict, List, Tuple
from uuid import UUID
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetStatus
from app.models.asset_metadata import AssetMetadata


class SearchRepository:
    """Repository executing database queries for asset search, filtering, and suggestions."""

    async def search_assets(
        self,
        db: AsyncSession,
        user_id: UUID,
        parsed: Dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> Tuple[List[Asset], int]:
        """Executes database query for matching assets based on parsed search parameters."""
        stmt = select(Asset).where(Asset.owner_id == user_id)

        # Exclude soft deleted unless explicitly requested via status:deleted
        if parsed.get("status") != "DELETED":
            stmt = stmt.where(Asset.is_deleted == False)

        # Attribute filters
        if parsed.get("asset_type"):
            stmt = stmt.where(Asset.asset_type == parsed["asset_type"])

        if parsed.get("is_favorite") is not None:
            stmt = stmt.where(Asset.is_favorite == parsed["is_favorite"])

        if parsed.get("status"):
            stmt = stmt.where(Asset.status == parsed["status"])

        if parsed.get("min_size_bytes") is not None:
            stmt = stmt.where(Asset.file_size >= parsed["min_size_bytes"])

        if parsed.get("max_size_bytes") is not None:
            stmt = stmt.where(Asset.file_size <= parsed["max_size_bytes"])

        if parsed.get("created_after") is not None:
            stmt = stmt.where(Asset.created_at >= parsed["created_after"])

        if parsed.get("name_filter"):
            stmt = stmt.where(Asset.name.ilike(f"%{parsed['name_filter']}%"))

        # Free text search across Asset fields & AssetMetadata values
        free_text = parsed.get("free_text", "").strip()
        if free_text:
            kw = f"%{free_text}%"
            # Subquery for assets with matching metadata values
            meta_subq = select(AssetMetadata.asset_id).where(
                AssetMetadata.metadata_value.ilike(kw)
            )

            stmt = stmt.where(
                or_(
                    Asset.name.ilike(kw),
                    Asset.original_filename.ilike(kw),
                    Asset.description.ilike(kw),
                    Asset.id.in_(meta_subq),
                )
            )

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        # Sorting logic
        sort_col = getattr(Asset, sort_by, Asset.created_at)
        if sort_dir.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        # Pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        assets = list(result.scalars().all())

        return assets, total

    async def get_suggestions(
        self, db: AsyncSession, user_id: UUID, query_prefix: str, limit: int = 8
    ) -> List[Dict[str, str]]:
        """Returns metadata-driven search suggestions for asset titles, types, and metadata values."""
        if not query_prefix or len(query_prefix.strip()) < 2:
            return []

        kw = f"%{query_prefix.strip()}%"
        suggestions: List[Dict[str, str]] = []
        seen = set()

        # 1. Matching Asset Names
        name_stmt = (
            select(Asset.name)
            .where(Asset.owner_id == user_id, Asset.is_deleted == False, Asset.name.ilike(kw))
            .limit(limit)
        )
        name_res = await db.execute(name_stmt)
        for name in name_res.scalars().all():
            if name and name not in seen:
                seen.add(name)
                suggestions.append({"text": name, "type": "filename"})

        # 2. Matching Metadata Values
        if len(suggestions) < limit:
            meta_stmt = (
                select(AssetMetadata.metadata_value)
                .join(Asset, Asset.id == AssetMetadata.asset_id)
                .where(
                    Asset.owner_id == user_id,
                    Asset.is_deleted == False,
                    AssetMetadata.metadata_value.ilike(kw),
                )
                .limit(limit - len(suggestions))
            )
            meta_res = await db.execute(meta_stmt)
            for val in meta_res.scalars().all():
                if val and val not in seen and len(val) < 60:
                    seen.add(val)
                    suggestions.append({"text": val, "type": "metadata"})

        return suggestions[:limit]


search_repository = SearchRepository()
