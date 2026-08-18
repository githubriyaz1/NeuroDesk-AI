# NeuroDesk AI Enterprise Architecture Specification

> Release Version: **v0.4.7**  
> Status: **PHASE 4 SPRINT 4.7 COMPLETED & VERIFIED**

---

## 🏗️ 4-Tier Enterprise Architecture Pattern

Every backend domain follows a strict 4-tier dependency structure:

```
[ HTTP Router Layer ] -> [ Domain Service Layer ] -> [ Repository DB Layer ] -> [ SQLAlchemy Models ]
     (FastAPI)                (Business Logic)             (Database Queries)            (ORMs)
```

1. **Router Layer (`backend/app/routers/`)**: REST controllers parsing request parameters, enforcing authentication (`get_current_user`), and serializing response DTOs (`project_generator.py`, `workflow.py`).
2. **Domain Service Layer (`backend/app/services/`)**: Orchestrates business rules, search syntax parsing (`QueryParser`), preview generation (`PreviewService`), metadata extraction (`MetadataService`), file storage (`StorageService`), LLM execution & retries (`LLMService`), AI Chat (`AIChatService`), Enterprise Knowledge Engine (`KnowledgeService`), AI Data Analyst (`AnalysisService`), AI Workflow Studio (`WorkflowService`), and AI Studio Project Generator (`ProjectGeneratorService`).
3. **Core AI Studio & Project Generator Engine (`backend/app/core/project_generator/`)**:
   - `requirement_engine.py`: Problem statements, objectives, functional & non-functional requirements.
   - `tech_stack_engine.py`: 20+ technology stack recommendations.
   - `architecture_engine.py`: 4-tier system layer specifications, component relationships, security, and scalability.
   - `database_design_engine.py`: Entity tables, relationships, indexes, and PostgreSQL DDL SQL generator.
   - `api_contract_engine.py`: Endpoint specifications, HTTP verbs, status codes, and JWT auth strategy.
   - `folder_structure_engine.py`: Production directory trees with boilerplate file paths.
   - `prompt_engineering_engine.py`: System prompts, agent roles, and code gen prompt templates.
   - `code_template_engine.py`: Starter entrypoints, Dockerfiles, and root frontend templates.
   - `blueprint_engine.py`: Master assembler orchestrating all sub-engines into a cohesive blueprint payload.
   - `export_engine.py`: Document exporter for Markdown, JSON, YAML, and PDF specifications.
   - `project_generation_engine.py`: KnowledgeEngine, AnalysisEngine, WorkflowEngine, and LLMService context integration.
   - `ai_studio_engine.py`: Primary facade coordinating project generation, customization, templates, and analytics metrics.
4. **Repository Layer (`backend/app/repositories/`)**: Performs async database access (`ProjectGeneratorRepository`, `WorkflowRepository`, `ConversationRepository`, `ChatMessageRepository`, `KnowledgeRepository`) enforcing user tenancy checks (`owner_id == user_id`) and eager relationship loading (`selectinload`).
5. **Model / Database Layer (`backend/app/models/`)**: SQLAlchemy declarative models (`ProjectBlueprint`, `BlueprintVersion`, `Workflow`, `WorkflowVersion`, `WorkflowExecution`, `User`, `Asset`).

---

## ⚡ Frontend Architecture & AI Studio Components

- **State Management**: React Context (`AuthContext`, `ThemeContext`, `AssetContext`, `ChatContext`) optimized with `useMemo` and `useCallback` to prevent unnecessary re-renders.
- **AI Studio Dashboard (`AIStudioDashboard.jsx`)**: Central hub rendering metrics badges, starter template gallery, saved blueprint list, and active blueprint viewer.
- **Components**: `ProjectGeneratorWizard.jsx`, `BlueprintViewer.jsx`, `ArchitectureViewer.jsx`, `DatabaseViewer.jsx`, `FolderTreeViewer.jsx`, `APIViewer.jsx`, `RoadmapViewer.jsx`, `TechnologySelector.jsx`, `RequirementEditor.jsx`, `BlueprintHistoryPanel.jsx`, `ExportDialog.jsx`.
- **Services (`generatorService.js`)**: Async client managing project blueprint generation, list fetching, detail retrieval, updates, cloning, exports, starter templates, and metrics analytics.

---

## 🗄️ Database & Migration Strategy

- **ORM**: Async SQLAlchemy 2.0 with `asyncpg` (PostgreSQL) or `aiosqlite` (SQLite dev).
- **Migration Tool**: Alembic async runner (`backend/alembic/versions/`).
- **Schema**: Tables for `users`, `refresh_tokens`, `assets`, `asset_metadata`, `conversations`, `chat_messages`, `workflows`, `workflow_versions`, `project_blueprints`, `blueprint_versions`.
