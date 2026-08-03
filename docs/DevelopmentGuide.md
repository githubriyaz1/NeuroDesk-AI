# NeuroDesk AI Enterprise Development & DevOps Guide

> Comprehensive guide for local development, database migrations, Docker deployment, environment variables, code quality, and testing.

---

## 🛠️ Developer Tooling & One-Command Scripts

NeuroDesk AI provides cross-platform task runner scripts:

### PowerShell (Windows)
```powershell
.\dev.ps1 setup        # Initial environment & dependency setup
.\dev.ps1 backend      # Start FastAPI backend (http://localhost:8000)
.\dev.ps1 frontend     # Start Vite React frontend (http://localhost:5173)
.\dev.ps1 test         # Run backend Pytest & frontend Vitest test suites
.\dev.ps1 migrate      # Execute Alembic database migrations
.\dev.ps1 docker-up    # Launch multi-container production Docker stack
.\dev.ps1 docker-down  # Stop Docker containers
```

### Bash (Linux / macOS)
```bash
./dev.sh setup
./dev.sh backend
./dev.sh frontend
./dev.sh test
./dev.sh migrate
./dev.sh docker-up
./dev.sh docker-down
```

---

## 🐳 Production Docker Deployment

Launch full-stack production containers (PostgreSQL 16, FastAPI backend, Nginx frontend SPA):

```bash
docker-compose up -d --build
```

Health checks automatically monitor container health:
- Backend: `GET http://localhost:8000/api/v1/health`
- LLM Diagnostics: `GET http://localhost:8000/api/v1/chat/diagnostics`
- Knowledge Diagnostics: `GET http://localhost:8000/api/v1/knowledge/diagnostics`
- Workflow Metrics: `GET http://localhost:8000/api/v1/workflows/metrics`
- AI Studio Metrics: `GET http://localhost:8000/api/v1/ai-studio/blueprints/metrics`
- Starter Templates: `GET http://localhost:8000/api/v1/ai-studio/blueprints/templates/starter`
- Postgres: `pg_isready -U neurodesk -d neurodesk_db`
- Frontend: `GET http://localhost:80/`

---

## 🧪 Testing & Code Quality

```bash
# Run backend pytest suite (54 test cases)
cd backend && pytest -v

# Run frontend Vitest runner (34 test cases)
cd frontend && npm run test:run

# Run frontend production build validation
cd frontend && npm run build

# Run Python linter & formatter (Ruff)
cd backend && ruff check app/ tests/
```
