from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class ProjectGenerateRequest(BaseModel):
    title: str
    idea_description: str
    target_stack: Optional[str] = "React + Python FastAPI + PostgreSQL"


class DatabaseDesignTable(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]
    relationships: List[str]


class APIEndpointPlan(BaseModel):
    method: str
    endpoint: str
    summary: str


class ProjectBlueprintResponse(BaseModel):
    id: UUID
    title: str
    idea_description: str
    owner_id: UUID
    architecture_overview: str
    database_design: Dict[str, Any]
    api_plan: Dict[str, Any]
    feature_breakdown: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
