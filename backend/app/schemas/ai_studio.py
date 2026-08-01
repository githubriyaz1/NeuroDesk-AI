from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class AIModelCreate(BaseModel):
    name: str
    model_type: str
    framework: str
    workspace_id: Optional[UUID] = None
    hyperparameters: Optional[Dict[str, Any]] = {}


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    accuracy_score: Optional[float] = None
    hyperparameters: Optional[Dict[str, Any]] = None


class AIModelResponse(BaseModel):
    id: UUID
    name: str
    model_type: str
    framework: str
    workspace_id: Optional[UUID] = None
    owner_id: UUID
    status: str
    accuracy_score: Optional[float] = None
    hyperparameters: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
