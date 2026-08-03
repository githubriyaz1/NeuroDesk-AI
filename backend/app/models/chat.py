import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MessageRole(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    ERROR = "error"


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Conversation(Base):
    """Enterprise AI Conversation model supporting multi-tenancy, state management, and future provider metadata."""

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Conversation")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_token_usage: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        nullable=False,
    )
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    future_tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    settings_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {
            "model": "neurodesk-mock-v1",
            "temperature": 0.7,
            "max_tokens": 4096,
            "system_prompt": "You are NeuroDesk AI, an intelligent workspace assistant.",
        },
        nullable=False,
    )
    provider_info_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {"provider": "mock", "api_version": "v1"},
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    owner = relationship("User", backref="conversations")
    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    __table_args__ = (
        Index("idx_conversations_owner_archived", "owner_id", "is_archived"),
        Index("idx_conversations_owner_favorite", "owner_id", "is_favorite"),
        Index("idx_conversations_owner_pinned", "owner_id", "is_pinned"),
        Index("idx_conversations_owner_last_msg", "owner_id", "last_message_at"),
    )


class ChatMessage(Base):
    """Production-grade Chat Message model supporting branching, attachments, token usage, and streaming states."""

    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_message_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True, index=True
    )

    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    attachments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    attached_assets: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)
    mentioned_assets: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)
    retrieved_assets: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)

    token_usage: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        nullable=False,
    )
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    message_status: Mapped[str] = mapped_column(
        String(50), default=MessageStatus.COMPLETED.value, nullable=False
    )
    feedback: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    parent_message = relationship("ChatMessage", remote_side=[id], backref="child_messages")

    __table_args__ = (
        Index("idx_chat_messages_conv_created", "conversation_id", "created_at"),
    )
