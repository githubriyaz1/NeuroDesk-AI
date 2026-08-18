import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.logging import logger
from app.schemas.knowledge import KnowledgeIndexItem


class KnowledgeIndexer:
    """Searchable in-memory & database knowledge index manager.
    
    Supports incremental indexing and refresh hooks after asset updates/uploads.
    """

    def __init__(self):
        self._index: Dict[UUID, KnowledgeIndexItem] = {}
        self._last_refresh: Optional[datetime] = None

    def index_asset(
        self,
        asset_id: UUID,
        asset_name: str,
        file_type: str,
        extracted_text: str,
        metadata_fields: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeIndexItem:
        """Indexes an individual asset into the Knowledge Index."""
        item = KnowledgeIndexItem(
            asset_id=asset_id,
            asset_name=asset_name,
            file_type=file_type,
            indexed_text=extracted_text,
            metadata_fields=metadata_fields or {},
            indexed_at=datetime.now(timezone.utc),
        )
        self._index[asset_id] = item
        logger.info(f"Indexed asset '{asset_name}' [{asset_id}] into Knowledge Engine Index")
        return item

    def remove_asset(self, asset_id: UUID) -> bool:
        """Removes an asset from the Knowledge Index following deletion."""
        if asset_id in self._index:
            del self._index[asset_id]
            logger.info(f"Removed asset [{asset_id}] from Knowledge Engine Index")
            return True
        return False

    def search_index(self, query: str, limit: int = 10) -> List[KnowledgeIndexItem]:
        """Performs fast in-memory keyword matching against the Knowledge Index."""
        query_words = set(query.lower().split())
        matched = []

        for item in self._index.values():
            searchable_blob = f"{item.asset_name} {item.file_type} {item.indexed_text} {str(item.metadata_fields)}".lower()
            overlap = sum(1 for word in query_words if word in searchable_blob)
            if overlap > 0:
                matched.append((overlap, item))

        # Sort by keyword overlap descending
        matched.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in matched[:limit]]

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the current Knowledge Index."""
        return {
            "total_indexed_assets": len(self._index),
            "total_indexed_chunks": sum(len(item.indexed_text.split("\n")) for item in self._index.values()),
            "last_refresh_at": self._last_refresh.isoformat() if self._last_refresh else None,
        }

    async def refresh_index_from_db(self, db_session: Any, owner_id: UUID) -> int:
        """Refreshes Knowledge Index incrementally from database records."""
        try:
            from app.models.asset import Asset
            from sqlalchemy import select

            stmt = select(Asset).where(Asset.owner_id == owner_id, Asset.is_deleted == False)
            res = await db_session.execute(stmt)
            assets = res.scalars().all()

            for asset in assets:
                filename = asset.original_filename or asset.name
                text_content = f"Title: {filename}. Type: {asset.asset_type}. Description: {asset.description or 'No description'}"
                self.index_asset(
                    asset_id=asset.id,
                    asset_name=filename,
                    file_type=asset.mime_type,
                    extracted_text=text_content,
                    metadata_fields={"checksum": asset.checksum, "file_size": asset.file_size},
                )

            self._last_refresh = datetime.now(timezone.utc)
            return len(assets)
        except Exception as exc:
            logger.error(f"Failed to refresh Knowledge Index from DB: {exc}")
            return 0


knowledge_indexer = KnowledgeIndexer()
