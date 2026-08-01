# NeuroDesk AI Database Architecture & Schema Strategy

## Overview

NeuroDesk AI uses **PostgreSQL 16** as its primary relational database store. Database access in the Python FastAPI backend is managed via **SQLAlchemy 2.0 Async ORM** (`asyncpg` driver).

## DDL Schema

The `schema.sql` file in this directory contains the reference PostgreSQL schema definitions including:
- `users`: User identity and authentication parameters.
- `workspaces`: User datasets, documents, and workspace file metadata.
- `ai_models`: Trained AI models, artifacts, and evaluation metrics.
- `project_blueprints`: Generated software project architecture blueprints.
- `chat_sessions` & `chat_messages`: Conversational AI history.
- `workflows` & `workflow_runs`: Pipeline automation definitions and execution logs.

## Migration Workflow

For production migrations, Alembic is recommended.

```bash
# Initialize Alembic migrations (when DB is ready)
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial schema migration"
alembic upgrade head
```
