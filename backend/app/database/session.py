from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.core.logging import logger
from app.database.base import Base
import app.models  # noqa: F401 - Register all SQLAlchemy models on Base.metadata

# Configure Async Engine based on database dialect (SQLite vs PostgreSQL)
is_sqlite = "sqlite" in settings.DATABASE_URL.lower()

if is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=(settings.ENVIRONMENT == "development"),
        future=True,
        connect_args={"check_same_thread": False, "timeout": 30.0},
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=(settings.ENVIRONMENT == "development"),
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def _sync_inspect_and_clean_stale_tables(conn):
    """Synchronously inspect SQLite tables and drop any outdated schemas before create_all."""
    from sqlalchemy import inspect
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    # Clean outdated project_blueprints schema if missing 'name'
    if "project_blueprints" in tables:
        cols = [c["name"] for c in inspector.get_columns("project_blueprints")]
        if "name" not in cols:
            logger.warning("Outdated project_blueprints table detected. Dropping for schema sync...")
            conn.execute(text("DROP TABLE IF EXISTS blueprint_versions;"))
            conn.execute(text("DROP TABLE IF EXISTS project_blueprints;"))

    # Clean outdated workflows schema if missing 'nodes_json'
    if "workflows" in tables:
        cols = [c["name"] for c in inspector.get_columns("workflows")]
        if "nodes_json" not in cols:
            logger.warning("Outdated workflows table detected. Dropping for schema sync...")
            conn.execute(text("DROP TABLE IF EXISTS execution_logs;"))
            conn.execute(text("DROP TABLE IF EXISTS workflow_execution_nodes;"))
            conn.execute(text("DROP TABLE IF EXISTS workflow_executions;"))
            conn.execute(text("DROP TABLE IF EXISTS workflow_versions;"))
            conn.execute(text("DROP TABLE IF EXISTS workflows;"))

    if "chat_sessions" in tables:
        conn.execute(text("DROP TABLE IF EXISTS chat_sessions;"))


async def init_db() -> None:
    """Initialize database tables using Base.metadata.create_all for SQLite/dev setups."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(_sync_inspect_and_clean_stale_tables)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as exc:
        logger.error(f"Failed to initialize database schema: {exc}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection generator for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session error: {exc}")
            raise
        finally:
            await session.close()
