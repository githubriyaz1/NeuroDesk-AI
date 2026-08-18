from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class PreviewType(str, Enum):
    PDF = "PDF"
    CSV = "CSV"
    EXCEL = "EXCEL"
    IMAGE = "IMAGE"
    UNSUPPORTED = "UNSUPPORTED"


class AssetPreviewMetadataResponse(BaseModel):
    asset_id: UUID
    asset_name: str
    asset_type: str
    preview_type: PreviewType
    can_preview: bool
    has_thumbnail: bool
    file_size: int
    mime_type: str
    extension: str
    metadata: Dict[str, Any]


class AssetPreviewResponse(BaseModel):
    asset_id: UUID
    asset_name: str
    preview_type: PreviewType
    can_preview: bool
    mime_type: str
    file_size: int
    content: Dict[str, Any]
    metadata: Dict[str, Any]


class ThumbnailResponse(BaseModel):
    has_thumbnail: bool
    message: str
    asset_id: Optional[UUID] = None


PreviewResponse = AssetPreviewResponse
