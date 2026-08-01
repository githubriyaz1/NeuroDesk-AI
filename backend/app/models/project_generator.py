import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import DateTime, ForeignKey, String, Text, UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectBlueprint(Base):
    __tablename__ = "project_blueprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    idea_description: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    architecture_overview: Mapped[str] = mapped_column(Text, nullable=True)
    database_design: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    api_plan: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    feature_breakdown: Mapped[List[Any]] = mapped_column(JSON, default=list)
    roadmap: Mapped[List[Any]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
