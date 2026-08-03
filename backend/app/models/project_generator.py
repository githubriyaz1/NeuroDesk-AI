from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class ProjectType(str, Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    REST_API = "rest_api"
    MICROSERVICES = "microservices"
    AI_APP = "ai_app"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    IOT_APP = "iot_app"
    ACCESSIBILITY_APP = "accessibility_app"
    ENTERPRISE_SOFTWARE = "enterprise_software"
    SAAS_PLATFORM = "saas_platform"


class ProjectBlueprint(Base):
    """Database model for AI Studio Project Blueprints."""

    __tablename__ = "project_blueprints"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(50), default=ProjectType.WEB_APP.value, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Complete JSON specification blocks
    blueprint_json = Column(JSON, default=dict, nullable=False)
    tech_stack_json = Column(JSON, default=dict, nullable=False)
    architecture_json = Column(JSON, default=dict, nullable=False)
    requirements_json = Column(JSON, default=dict, nullable=False)
    database_schema_json = Column(JSON, default=dict, nullable=False)
    api_contracts_json = Column(JSON, default=dict, nullable=False)
    folder_tree_json = Column(JSON, default=dict, nullable=False)
    roadmap_json = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    versions = relationship("BlueprintVersion", back_populates="blueprint", cascade="all, delete-orphan")

    @property
    def tech_stack(self) -> Dict[str, Any]:
        return self.tech_stack_json or {}

    @property
    def architecture(self) -> Dict[str, Any]:
        return self.architecture_json or {}

    @property
    def requirements(self) -> Dict[str, Any]:
        return self.requirements_json or {}

    @property
    def database_schema(self) -> Dict[str, Any]:
        return self.database_schema_json or {}

    @property
    def api_contracts(self) -> Dict[str, Any]:
        return self.api_contracts_json or {}

    @property
    def folder_tree(self) -> Dict[str, Any]:
        return self.folder_tree_json or {}

    @property
    def roadmap(self) -> Dict[str, Any]:
        return self.roadmap_json or {}


class BlueprintVersion(Base):
    """Historical version snapshot of an AI Studio project blueprint."""

    __tablename__ = "blueprint_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    blueprint_id = Column(PG_UUID(as_uuid=True), ForeignKey("project_blueprints.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    blueprint_json = Column(JSON, default=dict, nullable=False)
    changelog = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    blueprint = relationship("ProjectBlueprint", back_populates="versions")
