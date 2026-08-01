import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AssetMetadata(Base):
    __tablename__ = "asset_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metadata_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metadata_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(50), nullable=False, default="string")
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        Index("idx_asset_metadata_asset_key", "asset_id", "metadata_key", unique=True),
    )
