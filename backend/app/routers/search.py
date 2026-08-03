from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_active_user
from app.schemas.search import SearchResponse, SearchSuggestionsResponse
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search Engine & Discovery Platform"])


@router.get("", response_model=SearchResponse)
async def search_assets(
    q: str = Query("", description="Search query string with optional type:, status:, favorite: syntax"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute search query with advanced syntax parsing, metadata matching, and score ranking."""
    return await search_service.search(
        db=db,
        user_id=current_user.id,
        q=q,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    q: str = Query("", description="Prefix search term"),
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve metadata-driven auto-complete search suggestions."""
    return await search_service.get_suggestions(
        db=db, user_id=current_user.id, q=q, limit=limit
    )
