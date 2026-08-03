from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_active_user
from app.schemas.knowledge import (
    KnowledgeDiagnosticsResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResult,
)
from app.services.knowledge_service import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["Enterprise Knowledge Engine"])


@router.post("/query", response_model=KnowledgeQueryResult)
async def query_knowledge_engine(
    req: KnowledgeQueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes parallel document retrieval, multi-factor ranking, and citation packaging."""
    return await knowledge_service.query(db, current_user.id, req)


@router.post("/index", status_code=status.HTTP_200_OK)
async def trigger_knowledge_indexing(
    asset_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Triggers incremental or workspace-wide Knowledge Engine re-indexing."""
    result = await knowledge_service.trigger_index(db, current_user.id, asset_id)
    return {"status": "success", "result": result}


@router.get("/diagnostics", response_model=KnowledgeDiagnosticsResponse)
async def get_knowledge_diagnostics(
    current_user: User = Depends(get_current_active_user),
):
    """Returns Knowledge Engine health diagnostics, index statistics, and retriever latency metrics."""
    return knowledge_service.get_diagnostics()
