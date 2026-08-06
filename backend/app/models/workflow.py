from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID as PyUUID, uuid4
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Workflow(Base):
    """Database model for enterprise workflows."""

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=WorkflowStatus.DRAFT.value, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    nodes_json = Column(JSON, default=list, nullable=False)
    edges_json = Column(JSON, default=list, nullable=False)
    variables_json = Column(JSON, default=dict, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    versions = relationship("WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")

    @property
    def nodes(self) -> List[Dict[str, Any]]:
        return self.nodes_json or []

    @property
    def edges(self) -> List[Dict[str, Any]]:
        return self.edges_json or []

    @property
    def variables(self) -> Dict[str, Any]:
        return self.variables_json or {}


class WorkflowVersion(Base):
    """Historical version snapshot of a workflow graph."""

    __tablename__ = "workflow_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    nodes_json = Column(JSON, default=list, nullable=False)
    edges_json = Column(JSON, default=list, nullable=False)
    variables_json = Column(JSON, default=dict, nullable=False)
    changelog = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    workflow = relationship("Workflow", back_populates="versions")


class WorkflowExecution(Base):
    """Execution record for a workflow run."""

    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default=ExecutionStatus.PENDING.value, nullable=False)
    trigger_source = Column(String(50), default="manual", nullable=False)  # manual, cron, api
    inputs_json = Column(JSON, default=dict, nullable=False)
    outputs_json = Column(JSON, default=dict, nullable=False)
    execution_context_json = Column(JSON, default=dict, nullable=False)
    total_latency_ms = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="executions")
    nodes = relationship("WorkflowExecutionNode", back_populates="execution", cascade="all, delete-orphan", lazy="selectin")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan", lazy="selectin")

    @property
    def inputs(self) -> Dict[str, Any]:
        return self.inputs_json or {}

    @property
    def outputs(self) -> Dict[str, Any]:
        return self.outputs_json or {}


class WorkflowExecutionNode(Base):
    """Execution state for an individual node within a workflow run."""

    __tablename__ = "workflow_execution_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=False)
    node_type = Column(String(100), nullable=False)
    status = Column(String(50), default=ExecutionStatus.PENDING.value, nullable=False)
    inputs_json = Column(JSON, default=dict, nullable=False)
    outputs_json = Column(JSON, default=dict, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    execution = relationship("WorkflowExecution", back_populates="nodes")

    @property
    def inputs(self) -> Dict[str, Any]:
        return self.inputs_json or {}

    @property
    def outputs(self) -> Dict[str, Any]:
        return self.outputs_json or {}


class ExecutionLog(Base):
    """Log record for node and workflow execution steps."""

    __tablename__ = "execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=True)
    log_level = Column(String(20), default="INFO", nullable=False)
    message = Column(Text, nullable=False)
    details_json = Column(JSON, default=dict, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    execution = relationship("WorkflowExecution", back_populates="logs")

    @property
    def details(self) -> Dict[str, Any]:
        return self.details_json or {}
