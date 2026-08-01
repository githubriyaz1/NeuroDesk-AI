import os
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.models.asset import Asset, AssetStatus, AssetType
from app.repositories.asset_repository import asset_repository
from app.schemas.asset import (
    AssetBulkActionResponse,
    AssetDetailResponse,
    AssetStatisticsResponse,
    AssetUploadResponse,
    PaginatedAssetResponse,
)
from app.services.asset_validation_service import asset_validation_service
from app.services.storage_service import storage_service


def infer_asset_type(mime_type: str, filename: str) -> AssetType:
    """Classifies asset type from MIME type and file extension."""
    ext = os.path.splitext(filename)[1].lower()
    mime = (mime_type or "").lower()

    if mime.startswith("image/"):
        return AssetType.IMAGE
    if mime.startswith("audio/"):
        return AssetType.AUDIO
    if mime.startswith("video/"):
        return AssetType.VIDEO

    if ext in [".csv", ".xlsx", ".xls", ".ods"] or "spreadsheet" in mime or "excel" in mime or "csv" in mime:
        return AssetType.SPREADSHEET

    if ext in [".parquet", ".arrow", ".feather", ".h5", ".hdf5", ".json"] or "parquet" in mime or "json" in mime:
        return AssetType.DATASET

    if ext in [".pt", ".pth", ".onnx", ".safetensors", ".bin", ".tflite"]:
        return AssetType.MODEL

    if ext in [".pdf"] or "pdf" in mime:
        return AssetType.REPORT

    if ext in [".prompt"]:
        return AssetType.PROMPT

    return AssetType.DOCUMENT


class AssetService:
    """Enterprise Business Logic Service for Digital Asset Management System (DAMS)."""

    async def upload_asset(
        self,
        db: AsyncSession,
        user_id: UUID,
        file_obj: BinaryIO,
        original_filename: str,
        description: Optional[str] = None,
        custom_mime_type: Optional[str] = None,
    ) -> AssetUploadResponse:
        """Validates upload via AssetValidationService, saves to storage, persists DB record via AssetRepository."""
        safe_filename, ext, mime_type = asset_validation_service.validate_file(
            file_obj=file_obj,
            original_filename=original_filename,
            client_mime_type=custom_mime_type,
        )

        asset_type = infer_asset_type(mime_type, safe_filename)
        asset_name = os.path.splitext(safe_filename)[0]
        now = datetime.now(timezone.utc)

        # Save file to pluggable storage provider
        try:
            rel_storage_path, file_size, checksum_hex = await storage_service.save_file(
                user_id=user_id,
                original_filename=safe_filename,
                file_obj=file_obj,
            )
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as e:
            logger.error(f"File upload storage failure: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist asset in storage.",
            )

        # Check for duplicate upload (matching checksum and size)
        existing = await asset_repository.get_by_checksum_and_size(
            db, user_id, checksum_hex, file_size
        )
        if existing:
            await storage_service.delete_file(rel_storage_path)
            return AssetUploadResponse.model_validate(existing)

        new_asset = Asset(
            owner_id=user_id,
            name=asset_name,
            original_filename=safe_filename,
            description=description,
            asset_type=asset_type.value,
            mime_type=mime_type,
            extension=f".{ext}",
            file_size=file_size,
            checksum=checksum_hex,
            storage_provider=settings.DEFAULT_STORAGE_PROVIDER,
            storage_path=rel_storage_path,
            status=AssetStatus.READY.value,
            version=1,
            is_favorite=False,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )

        created_asset = await asset_repository.create(db, new_asset)
        logger.info(f"Asset uploaded successfully: {created_asset.id} [{created_asset.original_filename}]")

        # Automatically extract and index asset metadata
        try:
            from app.services.metadata_service import metadata_service
            await metadata_service.index_and_persist(db, created_asset)
        except Exception as e:
            logger.error(f"Failed to auto-extract metadata for asset {created_asset.id}: {e}")

        return AssetUploadResponse.model_validate(created_asset)

    async def get_asset_model(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID, include_deleted: bool = False
    ) -> Asset:
        """Internal helper resolving asset entity with strict ownership check via AssetRepository."""
        asset = await asset_repository.get_by_id(db, user_id, asset_id, include_deleted=include_deleted)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or access denied.",
            )
        return asset

    async def get_asset(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetDetailResponse:
        """Get single asset metadata by ID."""
        asset = await self.get_asset_model(db, user_id, asset_id)
        return AssetDetailResponse.model_validate(asset)

    async def download_asset(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> Tuple[Path, str, str]:
        """Validates ownership and returns (absolute_file_path, original_filename, mime_type)."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=False)

        if not storage_service.file_exists(asset.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical asset file missing from storage.",
            )

        abs_path = storage_service.get_absolute_path(asset.storage_path)
        return abs_path, asset.original_filename, asset.mime_type

    async def soft_delete_asset(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetDetailResponse:
        """Soft deletes asset by setting is_deleted=True and status=DELETED."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=False)
        
        now = datetime.now(timezone.utc)
        asset.is_deleted = True
        asset.status = AssetStatus.DELETED.value
        asset.deleted_at = now
        asset.updated_at = now

        updated = await asset_repository.save(db, asset)
        logger.info(f"Soft deleted asset: {updated.id}")
        return AssetDetailResponse.model_validate(updated)

    async def restore_asset(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID
    ) -> AssetDetailResponse:
        """Restores a soft deleted asset."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=True)

        if not asset.is_deleted:
            return AssetDetailResponse.model_validate(asset)

        now = datetime.now(timezone.utc)
        asset.is_deleted = False
        asset.status = AssetStatus.READY.value
        asset.deleted_at = None
        asset.updated_at = now

        updated = await asset_repository.save(db, asset)
        logger.info(f"Restored asset: {updated.id}")
        return AssetDetailResponse.model_validate(updated)

    async def toggle_archive(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID, is_archived: bool = True
    ) -> AssetDetailResponse:
        """Toggles asset archive status."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=False)

        now = datetime.now(timezone.utc)
        asset.status = AssetStatus.ARCHIVED.value if is_archived else AssetStatus.READY.value
        asset.updated_at = now

        updated = await asset_repository.save(db, asset)
        logger.info(f"Updated asset archive state: {updated.id} -> {updated.status}")
        return AssetDetailResponse.model_validate(updated)

    async def bulk_action(
        self, db: AsyncSession, user_id: UUID, asset_ids: List[UUID], action: str
    ) -> AssetBulkActionResponse:
        """Performs bulk action (delete, restore, favorite, unfavorite, archive, unarchive) across assets."""
        action = action.lower()
        if action not in ["delete", "restore", "favorite", "unfavorite", "archive", "unarchive"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported bulk action '{action}'.",
            )

        processed_count = await asset_repository.execute_bulk_action(db, user_id, asset_ids, action)

        return AssetBulkActionResponse(
            success=True,
            processed_count=processed_count,
            action=action,
            message=f"Successfully executed bulk action '{action}' on {processed_count} assets.",
        )

    async def rename_asset(
        self,
        db: AsyncSession,
        user_id: UUID,
        asset_id: UUID,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AssetDetailResponse:
        """Updates asset display name or description."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=False)

        now = datetime.now(timezone.utc)
        if new_name is not None and new_name.strip():
            asset.name = asset_validation_service.sanitize_filename(new_name)
        if description is not None:
            asset.description = description
        
        asset.updated_at = now
        updated = await asset_repository.save(db, asset)

        logger.info(f"Updated asset metadata: {updated.id}")
        return AssetDetailResponse.model_validate(updated)

    async def toggle_favorite(
        self, db: AsyncSession, user_id: UUID, asset_id: UUID, is_favorite: bool
    ) -> AssetDetailResponse:
        """Marks or unmarks an asset as favorite."""
        asset = await self.get_asset_model(db, user_id, asset_id, include_deleted=False)

        asset.is_favorite = is_favorite
        asset.updated_at = datetime.now(timezone.utc)
        updated = await asset_repository.save(db, asset)

        return AssetDetailResponse.model_validate(updated)

    async def list_assets(
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
    ) -> PaginatedAssetResponse:
        """Paginated asset listing via AssetRepository."""
        page = max(1, page)
        page_size = min(max(1, page_size), 100)

        assets, total = await asset_repository.list_paginated(
            db=db,
            user_id=user_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            is_favorite=is_favorite,
            asset_type=asset_type,
            status_filter=status_filter,
            include_deleted=include_deleted,
        )

        total_pages = max(1, (total + page_size - 1) // page_size)

        return PaginatedAssetResponse(
            items=[AssetDetailResponse.model_validate(a) for a in assets],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_statistics(
        self, db: AsyncSession, user_id: UUID
    ) -> AssetStatisticsResponse:
        """Calculates detailed storage usage and asset aggregations for the user via AssetRepository."""
        stats_dict = await asset_repository.get_user_statistics_aggregates(db, user_id)
        return AssetStatisticsResponse(**stats_dict)


asset_service = AssetService()
