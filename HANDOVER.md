# NeuroDesk AI — Developer Handover & Engineering Context

## Executive Summary

- **Project**: NeuroDesk AI — Enterprise AI Workspace & Automation Canvas
- **Current Status**: **Phase 7 Complete — Production Ready**
- **Automated Tests**: **184 Passed / 0 Failed (100% Success)**
- **Git Commit**: `42e968f48ee904f8cc19823971659aadd0cbfd40`
- **Git Branch**: `phase-4-ai-workspace`

---

## 1. Quick Onboarding (10-Minute Setup)

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Navigate to `http://localhost:5173`.

3. **Verify Installation**:
   ```bash
   # Run 150 backend tests:
   cd backend
   $env:PYTHONPATH="."
   venv\Scripts\pytest.exe tests/ -v

   # Run 34 frontend tests:
   cd frontend
   npm test -- --run
   ```

---

## 2. Core Architecture Decisions

### Intent-Aware Hybrid RAG
- User queries are evaluated by `IntentRouter`.
- PDF document queries route to `PDFRetriever` for page-specific extraction and grounded citations.
- Structured CSV queries route to `CSVRetriever` running exact **Pandas** calculations (`count`, `mean`, `sum`, `min`/`max`) to prevent LLM arithmetic hallucinations.

### Official Gemini SDK & Mock Fallback
- LLM generation uses `@google/genai` (`gemini-2.5-flash`).
- If `GOOGLE_API_KEY` is not present, `GeminiProvider` gracefully falls back to `MockProvider` so development and automated tests function 100% offline.

### Visual Workflow Studio DAG Engine
- Supports 14 custom node types including `python_script`, `http_request`, `data_transform`, and `conditional`.
- Python scripts run in isolated subprocesses with AST security auditing (`python_sandbox.py`).
- HTTP requests perform DNS resolution and private IP blocklist audits (`http_executor.py`).
- Supports JSON import/export, node retries, variable resolution, and status `SKIPPED` branch routing.

---

## 3. Known Limitations & Architectural Notes

1. **Database Engine**: Defaults to SQLite (`neurodesk.db`) for local testing. Production high-concurrency deployments should configure PostgreSQL (`DATABASE_URL=postgresql+asyncpg://...`).
2. **Subprocess Hardware Limits**: Python workflow scripts enforce a 5.0s execution timeout and AST security audit; OS cgroups can be configured in Docker for hardware RAM caps.
3. **Scanned PDF OCR**: Standard text-layer PDFs are natively processed. High-resolution scanned image PDFs require an optional Tesseract OCR installation.

---

## 4. Production Deployment Checklist

- [x] All 184 automated tests passing.
- [x] Vite frontend production build succeeds (`npm run build`).
- [x] `SECRET_KEY` set to secure 256-bit random key in production `.env`.
- [x] `GOOGLE_API_KEY` set for live Gemini API calls.
- [x] `CORS_ORIGINS` restricted to production frontend domain names.
- [x] Multi-tenant server-side ownership checks verified (HTTP 404 on IDOR attempts).
- [x] AST sandbox security & SSRF IP blocklists verified.
