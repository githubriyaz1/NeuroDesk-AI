from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class WorkflowNodeSchema(BaseModel):
    id: str
    type: str  # start, end, llm_prompt, knowledge_query, document_analysis, dataset_analysis, conditional, loop, merge, split, variable, delay, http_request, python_script, export, notification
    label: str
    position: Dict[str, float] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None
    condition_expr: Optional[str] = None


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_template: bool = False
    tags: List[str] = Field(default_factory=list)
    nodes: List[WorkflowNodeSchema] = Field(default_factory=list)
    edges: List[WorkflowEdgeSchema] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    nodes: Optional[List[WorkflowNodeSchema]] = None
    edges: Optional[List[WorkflowEdgeSchema]] = None
    variables: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    status: str
    is_template: bool
    tags: List[str]
    nodes: List[WorkflowNodeSchema]
    edges: List[WorkflowEdgeSchema]
    variables: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowRunRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)
    trigger_source: str = "manual"


class ExecutionNodeResponse(BaseModel):
    id: UUID
    node_id: str
    node_type: str
    status: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    latency_ms: float
    retry_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExecutionLogResponse(BaseModel):
    id: UUID
    node_id: Optional[str] = None
    log_level: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    owner_id: UUID
    status: str
    trigger_source: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    total_latency_ms: float
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    nodes: List[ExecutionNodeResponse] = Field(default_factory=list)
    logs: List[ExecutionLogResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    nodes: List[WorkflowNodeSchema]
    edges: List[WorkflowEdgeSchema]
