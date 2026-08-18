from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ProjectGenerationRequest(BaseModel):
    """Input payload to trigger project blueprint generation from plain English description."""
    title: str = Field(description="Name or working title of the project")
    description: str = Field(description="Plain English description of the software idea")
    project_type: str = Field(default="web_app", description="Type of application")
    preferred_tech_stack: Optional[List[str]] = Field(default=None, description="Preferred technologies (e.g., React, FastAPI, PostgreSQL)")
    target_audience: Optional[str] = Field(default="Enterprise", description="Target users or market segment")
    include_knowledge_context: bool = Field(default=True, description="Whether to query KnowledgeEngine for context assets")
    asset_ids: Optional[List[UUID]] = Field(default=None, description="Specific asset IDs to ground project context")


class BlueprintUpdateRequest(BaseModel):
    """Payload to update an existing blueprint structure."""
    name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    tech_stack: Optional[Dict[str, Any]] = None
    database_schema: Optional[Dict[str, Any]] = None
    api_contracts: Optional[Dict[str, Any]] = None
    folder_tree: Optional[Dict[str, Any]] = None
    roadmap: Optional[Dict[str, Any]] = None


class ExportRequest(BaseModel):
    """Export request for blueprint specification documents."""
    blueprint_id: UUID
    format: str = Field(default="markdown", description="markdown, pdf, json, yaml")
    sections: Optional[List[str]] = Field(default=None, description="Specific sections to include")


class ProjectBlueprintResponse(BaseModel):
    """Complete serialized blueprint response."""
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    project_type: str
    is_template: bool
    version: int
    blueprint_json: Dict[str, Any]
    tech_stack: Dict[str, Any]
    architecture: Dict[str, Any]
    requirements: Dict[str, Any]
    database_schema: Dict[str, Any]
    api_contracts: Dict[str, Any]
    folder_tree: Dict[str, Any]
    roadmap: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlueprintVersionResponse(BaseModel):
    """Historical version snapshot of a blueprint."""
    id: UUID
    blueprint_id: UUID
    version_number: int
    changelog: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectTemplateResponse(BaseModel):
    """Starter project blueprint template."""
    id: str
    name: str
    description: str
    project_type: str
    tech_stack: Dict[str, Any]
    architecture: Dict[str, Any]
    requirements: Dict[str, Any]


class ProjectMetricsResponse(BaseModel):
    """AI Studio analytics metrics."""
    total_blueprints: int
    project_types_breakdown: Dict[str, int]
    most_recommended_technologies: List[Dict[str, Any]]
    total_versions_snapshot: int
