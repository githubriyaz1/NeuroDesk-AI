# NeuroDesk AI — Enterprise AI Workspace & Automation Platform

![NeuroDesk AI Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Vite-blue)
![Python Version](https://img.shields.io/badge/Python-3.12-green)
![Tests Passed](https://img.shields.io/badge/Tests-184%20Passed-brightgreen)
![Build](https://img.shields.io/badge/Build-Production--Ready-success)

**NeuroDesk AI** is a production-grade enterprise workspace platform integrating grounded Hybrid RAG document reasoning, exact Pandas CSV data analytics, an official Google Gemini API provider, and a visual Workflow Studio DAG automation canvas with an isolated Python AST sandbox and SSRF-protected HTTP request execution.

---

## Key Features

1. **Grounded AI Chat & Hybrid RAG Engine**:
   - Intent-aware routing (`intent_router.py`) separating PDF document reasoning, Pandas CSV mathematical calculations, and general workspace search.
   - Grounded citations formatted as `[Filename, Page X]` with zero system prompt/history text leakage.
   - SSE (Server-Sent Events) live streaming response delivery.
2. **Exact Pandas CSV Analytics Engine**:
   - Performs exact mathematical calculations (count, average age, sum, distribution, min/max) directly via Pandas without relying on LLM arithmetic hallucinations.
3. **Google Gemini LLM Integration**:
   - Integrated with the official `@google/genai` SDK (`gemini-2.5-flash`).
   - Seamless fallback to `MockProvider` if no API key is configured or external services time out.
4. **Visual Workflow Studio & Automation DAG**:
   - Visual drag-and-drop workflow canvas (`WorkflowCanvas.jsx`).
   - Isolated Python sandbox executor (`python_sandbox.py`) with AST security auditing and 5.0s subprocess timeout enforcement.
   - SSRF-protected HTTP request executor (`http_executor.py`) with DNS resolution and private IP blocklists.
   - Rule-based Data Transform evaluator (`data_transform.py`), active conditional branch routing (`true`/`false`), per-node retries, variable resolution, and JSON import/export.
5. **Project Architecture Generator**:
   - Automated tech stack recommendation, risk assessment, and system architecture blueprint generation.
6. **Multi-Tenant Authorization & Security**:
   - Strict JWT bearer authentication with server-side ownership checks on all resources (HTTP 404 for unauthorized IDOR attempts).

---

## Repository Structure

```
NeuroDesk-AI/
├── backend/
│   ├── app/
│   │   ├── core/           # RAG, IntentRouter, LLM Providers, Sandbox, Workflow Engine
│   │   ├── database/       # SQLAlchemy 2.0 sessions & Base models
│   │   ├── models/         # User, Asset, Chat, Workflow, Project Generator SQLAlchemy models
│   │   ├── repositories/   # Async Database repository layer
│   │   ├── routers/        # FastAPI API routes (Auth, Workspace, Chat, Workflow, etc.)
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Domain business logic services
│   │   └── utils/          # Security & helper utilities
│   ├── tests/              # 150 automated pytest suites
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components (Workflow, Canvas, Chat, Modals, Cards)
│   │   ├── contexts/       # AuthContext, AssetContext, ChatContext
│   │   ├── pages/          # Dashboard, Workspace, Chat, Workflows, Studio, Generator
│   │   ├── services/       # Axios API client services
│   │   └── __tests__/      # 34 Vitest frontend test suites
│   ├── package.json
│   └── vite.config.js
├── docs/                   # System architecture & developer guides
├── scratch/                # Verified E2E verification & security audit scripts
├── .env.example            # Environment configuration template
└── README.md
```

---

## Prerequisites

- **Python**: 3.10+ (Recommended: Python 3.12)
- **Node.js**: 18+ (Recommended: Node.js 20 LTS)
- **Git**: 2.30+

---

## Quickstart Guide

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/githubriyaz1/NeuroDesk-AI.git
cd NeuroDesk-AI/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
```

### 2. Frontend Setup

```bash
cd ../frontend

# Install frontend dependencies
npm install
```

---

## Running the Application

### Option A: Development Mode

1. **Start Backend Server** (Port 8000):
   ```bash
   cd backend
   venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```
   API Docs available at: `http://localhost:8000/docs`

2. **Start Frontend Dev Server** (Port 5173):
   ```bash
   cd frontend
   npm run dev
   ```
   Access Web App at: `http://localhost:5173`

---

## Running Automated Tests & Verification

### Backend Tests (150 Passed)
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\pytest.exe tests/ -v
```

### Frontend Tests (34 Passed)
```bash
cd frontend
npm test -- --run
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

### E2E Security & Workflow Verification Scripts
```bash
# E2E Security & IDOR Audit:
python scratch/phase6_security_and_auth_audit.py

# E2E Workflow Studio Verification:
python scratch/verify_phase5_workflows_e2e.py
```

---

## Environment Variables (.env)

| Variable | Mandatory | Default / Placeholder | Description |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Yes | `development` | Deployment mode (`development`/`production`) |
| `SECRET_KEY` | Yes | `replace_with_secure_jwt_secret` | JWT signing secret key |
| `DATABASE_URL` | Yes | `sqlite+aiosqlite:///./neurodesk.db` | Async database URL |
| `GOOGLE_API_KEY` | No | `your_google_gemini_api_key_here` | Google Gemini API key (Fallback to MockProvider if omitted) |
| `LLM_PROVIDER` | No | `gemini` | Primary LLM provider (`gemini` or `mock`) |
| `STORAGE_LOCAL_ROOT` | Yes | `storage/uploads` | Document storage root directory |

---

## Core System Architecture & Documentation Links

Detailed architectural guides are available in the repository root:
- [ARCHITECTURE.md](file:///d:/PROJECTS/NeuroDesk-AI/ARCHITECTURE.md): System architecture map, data flows, and database schemas.
- [AI_FEATURES.md](file:///d:/PROJECTS/NeuroDesk-AI/AI_FEATURES.md): Hybrid RAG pipeline, Intent Router, grounded citations, and Pandas CSV engine.
- [WORKFLOW_GUIDE.md](file:///d:/PROJECTS/NeuroDesk-AI/WORKFLOW_GUIDE.md): Visual Workflow Studio node catalog and execution engine.
- [SECURITY.md](file:///d:/PROJECTS/NeuroDesk-AI/SECURITY.md): Python AST security sandbox, SSRF blocklists, and IDOR isolation.
- [TESTING.md](file:///d:/PROJECTS/NeuroDesk-AI/TESTING.md): 184 automated tests breakdown and audit commands.
- [API_DOCUMENTATION.md](file:///d:/PROJECTS/NeuroDesk-AI/API_DOCUMENTATION.md): Complete REST API specification.
- [TROUBLESHOOTING.md](file:///d:/PROJECTS/NeuroDesk-AI/TROUBLESHOOTING.md): Common developer errors and port conflict solutions.
- [HANDOVER.md](file:///d:/PROJECTS/NeuroDesk-AI/HANDOVER.md): Developer handover guide and operational decisions.

---

## Current Release Status

- **Version**: `1.0.0`
- **Release Status**: **Production-Ready**
- **Passed Test Coverage**: **184 / 184 Automated Tests Passed (100%)**
- **Git Branch**: `phase-4-ai-workspace`
