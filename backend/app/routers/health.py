import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.database.session import get_db
from app.schemas.health import HealthCheckResponse
from app.services.storage_service import storage_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
@router.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check endpoint verifying API status, database connectivity, and storage access."""
    # 1. Real database connection test using active AsyncSession
    db_status = "disconnected"
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "connected"
    except Exception as exc:
        logger.warning(f"Health check database ping failed: {exc}")
        db_status = "disconnected"

    # 2. Storage access check
    storage_status = "writable"
    try:
        root_path = storage_service.get_absolute_path(".")
        if not os.access(root_path, os.W_OK):
            storage_status = "read-only"
    except Exception:
        storage_status = "unavailable"

    overall_status = "healthy" if db_status == "connected" and storage_status == "writable" else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        api_status="healthy",
        database_status=db_status,
        storage_status=storage_status,
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
    )
