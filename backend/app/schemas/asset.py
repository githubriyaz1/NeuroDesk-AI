from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.models.asset import AssetStatus, AssetType


class AssetCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class AssetUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class AssetFavoriteToggle(BaseModel):
    is_favorite: bool


class AssetDetailResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    original_filename: str
    description: Optional[str] = None
    asset_type: AssetType
    mime_type: str
    extension: str
    file_size: int
    checksum: str
    storage_provider: str
    status: AssetStatus
    version: int
    is_favorite: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssetUploadResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    original_filename: str
    asset_type: AssetType
    mime_type: str
    extension: str
    file_size: int
    checksum: str
    storage_provider: str
    status: AssetStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAssetResponse(BaseModel):
    items: List[AssetDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssetStatisticsResponse(BaseModel):
    total_assets: int
    ready_assets: int = 0
    processing_assets: int = 0
    deleted_assets: int = 0
    favorite_assets: int = 0
    total_storage_used_bytes: int = 0
    total_storage_bytes: int = 0  # Backward compatibility
    favorite_count: int = 0       # Backward compatibility
    deleted_count: int = 0        # Backward compatibility
    newest_upload_timestamp: Optional[datetime] = None
    largest_asset_size_bytes: int = 0
    asset_count_by_type: Dict[str, int] = Field(default_factory=dict)
    assets_by_type: Dict[str, int] = Field(default_factory=dict)      # Backward compatibility
    assets_by_status: Dict[str, int] = Field(default_factory=dict)    # Backward compatibility

    @model_validator(mode="before")
    @classmethod
    def populate_compatibility_fields(cls, values: dict) -> dict:
        if isinstance(values, dict):
            # Synchronize backward compatible names
            if "total_storage_used_bytes" in values and "total_storage_bytes" not in values:
                values["total_storage_bytes"] = values["total_storage_used_bytes"]
            elif "total_storage_bytes" in values and "total_storage_used_bytes" not in values:
                values["total_storage_used_bytes"] = values["total_storage_bytes"]

            if "favorite_assets" in values and "favorite_count" not in values:
                values["favorite_count"] = values["favorite_assets"]
            elif "favorite_count" in values and "favorite_assets" not in values:
                values["favorite_assets"] = values["favorite_count"]

            if "deleted_assets" in values and "deleted_count" not in values:
                values["deleted_count"] = values["deleted_assets"]
            elif "deleted_count" in values and "deleted_assets" not in values:
                values["deleted_assets"] = values["deleted_count"]

            if "asset_count_by_type" in values and "assets_by_type" not in values:
                values["assets_by_type"] = values["asset_count_by_type"]
            elif "assets_by_type" in values and "asset_count_by_type" not in values:
                values["asset_count_by_type"] = values["assets_by_type"]
        return values


# Aliases for backward compatibility
AssetCreate = AssetCreateRequest
AssetUpdate = AssetUpdateRequest
AssetResponse = AssetDetailResponse
AssetListResponse = PaginatedAssetResponse
