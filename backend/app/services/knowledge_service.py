from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.knowledge.engine import knowledge_engine
from app.repositories.knowledge_repository import knowledge_repo
from app.schemas.knowledge import (
    KnowledgeDiagnosticsResponse,
    KnowledgeIndexItem,
    KnowledgeQueryRequest,
    KnowledgeQueryResult,
)


class KnowledgeService:
    """Service layer orchestrating Knowledge Engine queries and index synchronization."""

    def __init__(self):
        self.engine = knowledge_engine
        self.repo = knowledge_repo

    async def query(
        self,
        db: AsyncSession,
        owner_id: UUID,
        req: KnowledgeQueryRequest,
    ) -> KnowledgeQueryResult:
        """Executes Knowledge Engine query over user workspace assets."""
        return await self.engine.query_knowledge(owner_id=owner_id, req=req, db_session=db)

    async def trigger_index(
        self,
        db: AsyncSession,
        owner_id: UUID,
        asset_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Triggers incremental or full index refresh for user assets."""
        if asset_id:
            asset = await self.repo.get_asset_with_metadata(db, owner_id, asset_id)
            if not asset:
                return {"success": False, "message": "Asset not found"}
            
            text_blob = f"Title: {asset.filename}. Category: {asset.category}. Description: {asset.description or ''}"
            self.engine.indexer.index_asset(
                asset_id=asset.id,
                asset_name=asset.filename,
                file_type=asset.mime_type,
                extracted_text=text_blob,
                metadata_fields={"checksum": asset.checksum_sha256, "file_size": asset.file_size_bytes},
            )
            return {"success": True, "indexed_count": 1}

        count = await self.engine.indexer.refresh_index_from_db(db, owner_id)
        return {"success": True, "indexed_count": count}

    def get_diagnostics(self) -> KnowledgeDiagnosticsResponse:
        """Returns Knowledge Engine diagnostic metrics."""
        return self.engine.get_diagnostics()


knowledge_service = KnowledgeService()
