# NeuroDesk AI — Automated Testing & Verification Suite

## Overview

NeuroDesk AI is verified by **184 automated tests** covering backend unit logic, integration routes, RAG pipeline intent classification, visual workflow execution, and security blocklists, alongside Vitest frontend component tests and Vite production build verification.

---

## 1. Verified Test Suite Summary

- **Backend Automated Tests (Pytest)**: **150 / 150 Passed**
- **Frontend Component Tests (Vitest)**: **34 / 34 Passed**
- **Total Automated Tests**: **184 Passed (100% Success Rate)**
- **Frontend Production Build**: **Passed** in 4.20s via Vite v5.4.21.

---

## 2. Test Execution Commands

### 2.1 Backend Unit & Integration Tests (150 Passed)
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\pytest.exe tests/ -v
```

### 2.2 Frontend Component Tests (34 Passed)
```bash
cd frontend
npm test -- --run
```

### 2.3 Frontend Production Build
```bash
cd frontend
npm run build
```

### 2.4 E2E Security & Auth Audit Script
```bash
python scratch/phase6_security_and_auth_audit.py
```

### 2.5 E2E Workflow Studio Verification Script
```bash
python scratch/verify_phase5_workflows_e2e.py
```

---

## 3. Backend Test Coverage Breakdown

| Test File | Category | Tests | Description |
| :--- | :--- | :---: | :--- |
| `test_analysis_engine.py` | Document Analysis | 8 | Verifies text analysis, entity extraction, and metric calculation. |
| `test_assets.py` | Asset Management | 9 | Verifies file upload, MIME detection, checksum, search, and deletion. |
| `test_auth.py` | Authentication | 4 | Verifies registration, JWT login, token refresh, and invalid passwords. |
| `test_chat.py` | AI Chat Router | 2 | Verifies chat message creation and SSE streaming response endpoint. |
| `test_chat_memory_streaming.py` | Memory & Streaming | 5 | Verifies conversation history window and streaming SSE formatting. |
| `test_explain_and_leakage.py` | RAG Grounding | 5 | Verifies grounded document explanation and prompt leakage prevention. |
| `test_explorer.py` | Workspace Explorer | 1 | Verifies workspace folder hierarchy and asset tree. |
| `test_gemini_provider.py` | LLM Provider | 5 | Verifies Gemini SDK integration and MockProvider fallback. |
| `test_health.py` | System Health | 2 | Verifies `/health` endpoint and system status reporting. |
| `test_hybrid_rag_router.py` | RAG Intent Router | 85 | Verifies intent classification, confidence scores, and multi-retriever selection. |
| `test_knowledge_engine.py` | Knowledge Engine | 4 | Verifies context packaging and citation formatting. |
| `test_metadata.py` | Metadata Extractor | 2 | Verifies metadata extraction for PDF, CSV, and image assets. |
| `test_preview.py` | Document Preview | 6 | Verifies PDF page rendering and CSV table preview generation. |
| `test_project_generator.py` | Architecture Engine | 2 | Verifies architecture blueprint generation and risk analysis. |
| `test_search.py` | Workspace Search | 3 | Verifies keyword search and asset metadata filtering. |
| `test_workflow_studio.py` | Workflow Engine | 5 | Verifies DAG execution, retries, variable resolution, AST sandbox, and HTTP SSRF. |
| `test_workspace.py` | Workspace Metrics | 2 | Verifies workspace summary statistics and asset counting. |

---

## 4. Frontend Test Coverage Breakdown

| Test Component File | Tests | Description |
| :--- | :---: | :--- |
| `App.test.jsx` | 1 | Verifies application layout, navigation bar, and dark mode theme. |
| `Assets.test.jsx` | 1 | Verifies DAMS Workspace asset table rendering and file upload UI. |
| `Chat.test.jsx` | 2 | Verifies ChatWindow message bubble rendering and streaming SSE response. |
| `Preview.test.jsx` | 5 | Verifies file preview modal rendering for PDF and CSV assets. |
| `ProjectGenerator.test.jsx` | 4 | Verifies architecture blueprint visual viewer and requirement input form. |
| `WorkflowStudio.test.jsx` | 7 | Verifies visual DAG canvas, custom node rendering, toolbar actions, and JSON import/export. |
| Other Component Tests | 14 | Verifies buttons, modals, badges, empty states, and profile page forms. |
