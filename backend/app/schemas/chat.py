from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ExportFormatEnum(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"


# Streaming DTO
class StreamingChunk(BaseModel):
    stream_id: str
    conversation_id: UUID
    message_id: UUID
    chunk_index: int
    content: str
    is_final: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Message Reactions DTOs
class ChatMessageReactionCreate(BaseModel):
    reaction_type: str = Field(..., description="thumbs_up or thumbs_down")
    feedback_text: Optional[str] = None


class ChatMessageReactionResponse(BaseModel):
    id: UUID
    message_id: UUID
    user_id: UUID
    reaction_type: str
    feedback_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Message Schemas
class ChatMessageCreate(BaseModel):
    conversation_id: Optional[UUID] = None
    prompt: str = Field(..., min_length=1, description="User prompt text")
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    attached_assets: List[UUID] = Field(default_factory=list)
    mentioned_assets: List[UUID] = Field(default_factory=list)


class ChatMessageUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    parent_message_id: Optional[UUID] = None
    role: str
    content: str
    markdown: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    attached_assets: List[UUID] = Field(default_factory=list)
    mentioned_assets: List[UUID] = Field(default_factory=list)
    retrieved_assets: List[UUID] = Field(default_factory=list)
    token_usage: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    metadata_info: Dict[str, Any] = Field(default_factory=dict)
    message_status: str
    feedback: Optional[Dict[str, Any]] = None
    version: int = 1
    is_edited: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    conversation_id: UUID
    messages: List[ChatMessageResponse]
    total: int


# Conversation Folders DTOs
class ConversationFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = "#3b82f6"
    icon: Optional[str] = "folder"


class ConversationFolderResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    color: str
    icon: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


ConversationFolder = ConversationFolderResponse


# Conversation Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    folder_id: Optional[UUID] = None
    settings_json: Optional[Dict[str, Any]] = None
    attached_assets: List[UUID] = Field(default_factory=list)


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    folder_id: Optional[UUID] = None
    is_pinned: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    settings_json: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None
    folder_id: Optional[UUID] = None
    message_count: int
    total_token_usage: Dict[str, Any] = Field(default_factory=dict)
    estimated_cost: float = 0.0
    is_pinned: bool
    is_favorite: bool
    is_archived: bool
    future_tags: List[str] = Field(default_factory=list)
    settings_json: Dict[str, Any] = Field(default_factory=dict)
    provider_info_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    messages: Optional[List[ChatMessageResponse]] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConversationExportResponse(BaseModel):
    conversation_id: UUID
    title: str
    format: str
    content: str
    exported_at: datetime


class ConversationImportRequest(BaseModel):
    json_content: Dict[str, Any]


# LLM Diagnostics DTO
class LLMDiagnosticsResponse(BaseModel):
    status: str
    active_provider: str
    streaming_health: str
    memory_health: str
    average_latency_ms: float
    total_token_usage: Dict[str, int]
    active_cancellation_count: int
    cache_stream_count: int
