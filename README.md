# NeuroDesk AI 🧠⚡

> Enterprise AI-Powered Intelligent Workspace for Data Analysis, AI Studio Modeling & Project Generator, Automated Workflows, Digital Asset Management (DAMS), Enterprise Asset Explorer, Universal Preview Engine (UPE), Metadata & Indexing Engine, Search & Discovery Platform, Enterprise LLM Integration Platform, Real-Time SSE Streaming Engine & Conversation Memory, Enterprise Knowledge Engine (RAG Foundation), AI Data Analyst & Document Intelligence, and Enterprise AI Workflow Automation Studio.

[![CI/CD Pipeline](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/Release-v0.4.7-blue.svg?style=flat&logo=github)](https://github.com/your-org/NeuroDesk-AI/releases/tag/v0.4.7)
[![Phase 4 Sprint 4.7 Completed](https://img.shields.io/badge/Sprint%204.7-COMPLETED-emerald.svg?style=flat&logo=checkmarx)](https://jwt.io)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?style=flat&logo=react)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)

---

## 📌 Executive Summary (Phase 4 Sprint 4.7 Release - v0.4.7)

**NeuroDesk AI** has completed **Phase 4 Sprint 4.7 (Enterprise AI Studio & Intelligent Project Generator)**. The system provides a flagship AI Studio platform that transforms plain English software ideas into complete 4-tier architectural blueprints with system specifications, functional/non-functional requirements, 4-tier system diagrams, PostgreSQL DDL schemas, REST API specs, folder tree structures, development roadmaps, code templates, versioning, cloning, export options (Markdown/JSON/YAML/PDF), and KnowledgeEngine asset grounding. Verified with 100% test coverage across backend (`54/54` passed) and frontend (`34/34` passed) test suites.

---

## 🚀 System Architecture & Sprint Summary

```
+---------------------------------------------------------------------------------------------------+
|                                     NEURODESK AI PLATFORM STACK                                    |
+---------------------------------------------------------------------------------------------------+
|  Sprint 4.1: AI Conversation Platform Foundation (Conversations, Messages, ORM & Repositories)   |
|  Sprint 4.2: Enterprise LLM Provider Platform (Mock, Gemini, OpenAI, Claude Abstraction)          |
|  Sprint 4.3: Real-Time SSE Streaming Engine & Conversation Memory (Budget, Context Window, SSE)   |
|  Sprint 4.4: Enterprise Knowledge Engine (Parallel Retrievers, Ranking, Citations, Indexing)       |
|  Sprint 4.5: AI Data Analyst & Document Intelligence (Document, Dataset, Diff, Insights, Export)  |
|  Sprint 4.6: Enterprise AI Workflow Automation Studio (DAG Engine, Nodes, Execution & Console)    |
|  Sprint 4.7: Enterprise AI Studio & Project Generator (12 Sub-Engines, Specs, 4-Tier, Exports)     |
+---------------------------------------------------------------------------------------------------+
```

### Sprint 4.7 Core Deliverables
1. **ORM Models (`backend/app/models/project_generator.py`)**: `ProjectBlueprint`, `BlueprintVersion`, `ProjectType`.
2. **DTO Schemas & Validation (`app/schemas/project_generator.py`)**: `ProjectGenerationRequest`, `BlueprintUpdateRequest`, `ExportRequest`, `ProjectBlueprintResponse`, `BlueprintVersionResponse`, `ProjectTemplateResponse`, `ProjectMetricsResponse`.
3. **AI Studio Sub-Engines (`app/core/project_generator/`)**:
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
4. **Repository & Service (`app/repositories/` & `app/services/project_generator_service.py`)**: Async SQLAlchemy repository with eager loading (`selectinload`), version snapshots, blueprint cloning, updating, and metrics calculation.
5. **REST Routers (`app/routers/project_generator.py`)**: `/api/v1/ai-studio` endpoints (`/generate`, `/blueprints`, `/blueprints/{id}`, `/blueprints/{id}/clone`, `/export`, `/metrics`, `/templates/starter`).
6. **Frontend AI Studio Dashboard & Components**: `AIStudioDashboard.jsx`, `ProjectGeneratorWizard.jsx`, `BlueprintViewer.jsx`, `ArchitectureViewer.jsx`, `DatabaseViewer.jsx`, `FolderTreeViewer.jsx`, `APIViewer.jsx`, `RoadmapViewer.jsx`, `TechnologySelector.jsx`, `RequirementEditor.jsx`, `BlueprintHistoryPanel.jsx`, `ExportDialog.jsx`, `generatorService.js`.

---

## 🚀 Quick Start & One-Command Setup

### PowerShell (Windows)
```powershell
.\dev.ps1 setup        # Install dependencies
.\dev.ps1 backend      # Start FastAPI Server (http://localhost:8000)
.\dev.ps1 frontend     # Start Vite React App (http://localhost:5173)
.\dev.ps1 test         # Run Pytest & Vitest test suites
.\dev.ps1 migrate      # Run Alembic DB migrations
.\dev.ps1 docker-up    # Launch Docker Compose stack
```

### Bash (Linux / macOS)
```bash
./dev.sh setup
./dev.sh backend
./dev.sh frontend
./dev.sh test
./dev.sh migrate
./dev.sh docker-up
```

---

## 📜 Version & Release Details
- **Version**: `v0.4.7`
- **Phase 4 Sprint 4.7 Status**: **COMPLETED & VERIFIED**
