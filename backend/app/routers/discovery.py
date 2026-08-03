from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_active_user
from app.schemas.asset import AssetDetailResponse
from app.services.discovery_service import discovery_service

router = APIRouter(prefix="/discovery", tags=["Discovery Platform & Curated Collections"])


@router.get("/recent", response_model=List[AssetDetailResponse])
async def get_recent_discovery(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve recently updated digital assets for current user."""
    return await discovery_service.get_recent_assets(db=db, user_id=current_user.id, limit=limit)


@router.get("/favorites", response_model=List[AssetDetailResponse])
async def get_favorites_discovery(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve favorite digital assets for current user."""
    return await discovery_service.get_favorite_assets(db=db, user_id=current_user.id, limit=limit)


@router.get("/largest", response_model=List[AssetDetailResponse])
async def get_largest_discovery(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve largest digital assets by file size for current user."""
    return await discovery_service.get_largest_assets(db=db, user_id=current_user.id, limit=limit)


@router.get("/newest", response_model=List[AssetDetailResponse])
async def get_newest_discovery(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve newest uploaded digital assets for current user."""
    return await discovery_service.get_newest_assets(db=db, user_id=current_user.id, limit=limit)
