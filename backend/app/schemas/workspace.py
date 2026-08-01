from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    file_type: Optional[str] = "dataset"
    meta_data: Optional[Dict[str, Any]] = {}


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: UUID
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size_bytes: int = 0
    status: str
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
