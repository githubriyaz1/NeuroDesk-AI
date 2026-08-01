import enum
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AssetStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class AssetType(str, enum.Enum):
    DOCUMENT = "DOCUMENT"
    SPREADSHEET = "SPREADSHEET"
    DATASET = "DATASET"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    REPORT = "REPORT"
    PROMPT = "PROMPT"
    MODEL = "MODEL"
    VIDEO = "VIDEO"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AssetType.DOCUMENT.value, index=True
    )
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="local")
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AssetStatus.CREATED.value, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("idx_assets_owner_deleted", "owner_id", "is_deleted"),
        Index("idx_assets_owner_favorite", "owner_id", "is_favorite"),
        Index("idx_assets_owner_type", "owner_id", "asset_type"),
    )
