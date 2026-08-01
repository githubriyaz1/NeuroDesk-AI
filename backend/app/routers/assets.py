from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_active_user
from app.schemas.asset import (
    AssetArchiveToggle,
    AssetBulkActionRequest,
    AssetBulkActionResponse,
    AssetDetailResponse,
    AssetFavoriteToggle,
    AssetStatisticsResponse,
    AssetUpdateRequest,
    AssetUploadResponse,
    PaginatedAssetResponse,
)
from app.schemas.preview import (
    AssetPreviewMetadataResponse,
    AssetPreviewResponse,
    ThumbnailResponse,
)
from app.schemas.metadata import AssetMetadataResponse
from app.services.asset_service import asset_service
from app.services.preview_service import preview_service
from app.services.metadata_service import metadata_service

router = APIRouter(prefix="/assets", tags=["Digital Asset Management System (DAMS) & Universal Preview Engine (UPE)"])


@router.post("/upload", response_model=AssetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Multipart upload endpoint persisting asset metadata and physical file to pluggable storage."""
    return await asset_service.upload_asset(
        db=db,
        user_id=current_user.id,
        file_obj=file.file,
        original_filename=file.filename or "uploaded_file",
        description=description,
        custom_mime_type=file.content_type,
    )


@router.post("/bulk-action", response_model=AssetBulkActionResponse)
async def bulk_asset_action(
    payload: AssetBulkActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute bulk actions (delete, restore, favorite, unfavorite, archive, unarchive) across assets."""
    return await asset_service.bulk_action(
        db=db, user_id=current_user.id, asset_ids=payload.asset_ids, action=payload.action
    )


@router.get("/statistics", response_model=AssetStatisticsResponse)
async def get_asset_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve total asset metrics, storage consumption, and asset aggregations for current user."""
    return await asset_service.get_statistics(db=db, user_id=current_user.id)


@router.get("", response_model=PaginatedAssetResponse)
async def list_assets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort column"),
    sort_dir: str = Query("desc", description="Sort direction (asc/desc)"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites"),
    asset_type: Optional[str] = Query(None, description="Filter by AssetType"),
    status: Optional[str] = Query(None, description="Filter by AssetStatus"),
    include_deleted: bool = Query(False, description="Include soft deleted assets"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List authenticated user's digital assets with flexible pagination and filtering."""
    return await asset_service.list_assets(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        is_favorite=is_favorite,
        asset_type=asset_type,
        status_filter=status,
        include_deleted=include_deleted,
    )


@router.get("/{asset_id}", response_model=AssetDetailResponse)
async def get_asset_details(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Fetch single asset metadata by ID."""
    return await asset_service.get_asset(db=db, user_id=current_user.id, asset_id=asset_id)


@router.get("/{asset_id}/preview", response_model=AssetPreviewResponse)
async def get_asset_preview(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate and return Universal Preview Engine payload for requested asset."""
    return await preview_service.get_preview(db=db, user_id=current_user.id, asset_id=asset_id)


@router.get("/{asset_id}/metadata", response_model=AssetMetadataResponse)
async def get_asset_metadata(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve structured metadata grouped by categories for requested asset."""
    return await metadata_service.get_metadata(db=db, user_id=current_user.id, asset_id=asset_id)


@router.post("/{asset_id}/metadata/refresh", response_model=AssetMetadataResponse)
async def refresh_asset_metadata(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Force re-extraction and refresh of asset metadata."""
    return await metadata_service.refresh_metadata(db=db, user_id=current_user.id, asset_id=asset_id)


@router.get("/{asset_id}/thumbnail")
async def get_asset_thumbnail(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return thumbnail file stream if available, or graceful JSON fallback indicating thumbnail status."""
    has_thumb, file_path, filename, mime_type = await preview_service.get_thumbnail(
        db=db, user_id=current_user.id, asset_id=asset_id
    )

    if has_thumb and file_path:
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=mime_type,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ThumbnailResponse(
            has_thumbnail=False,
            message="Thumbnail generation unavailable for this asset type.",
            asset_id=asset_id,
        ).model_dump(mode="json"),
    )


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Securely stream physical asset file to authorized owner without exposing internal storage path."""
    abs_path, original_filename, mime_type = await asset_service.download_asset(
        db=db, user_id=current_user.id, asset_id=asset_id
    )
    return FileResponse(
        path=str(abs_path),
        filename=original_filename,
        media_type=mime_type,
    )


@router.patch("/{asset_id}", response_model=AssetDetailResponse)
async def rename_asset(
    asset_id: UUID,
    payload: AssetUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update asset display name or description."""
    return await asset_service.rename_asset(
        db=db,
        user_id=current_user.id,
        asset_id=asset_id,
        new_name=payload.name,
        description=payload.description,
    )


@router.post("/{asset_id}/favorite", response_model=AssetDetailResponse)
async def toggle_favorite_asset(
    asset_id: UUID,
    payload: AssetFavoriteToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark or unmark asset as favorite."""
    return await asset_service.toggle_favorite(
        db=db, user_id=current_user.id, asset_id=asset_id, is_favorite=payload.is_favorite
    )


@router.post("/{asset_id}/archive", response_model=AssetDetailResponse)
async def toggle_archive_asset(
    asset_id: UUID,
    payload: AssetArchiveToggle = AssetArchiveToggle(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Archive or unarchive an asset."""
    return await asset_service.toggle_archive(
        db=db, user_id=current_user.id, asset_id=asset_id, is_archived=payload.is_archived
    )


@router.delete("/{asset_id}", response_model=AssetDetailResponse)
async def soft_delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft delete asset (marks as deleted, moves to trash)."""
    return await asset_service.soft_delete_asset(db=db, user_id=current_user.id, asset_id=asset_id)


@router.post("/{asset_id}/restore", response_model=AssetDetailResponse)
async def restore_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Restore a soft-deleted asset."""
    return await asset_service.restore_asset(db=db, user_id=current_user.id, asset_id=asset_id)
