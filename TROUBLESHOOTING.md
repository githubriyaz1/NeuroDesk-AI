# NeuroDesk AI — Troubleshooting & Developer FAQ

## Overview

This guide addresses common developer issues encountered during setup, environment configuration, database initialization, and local execution.

---

## 1. Port Conflicts

### Port 8000 Already in Use (Backend)

If Uvicorn fails to start with `[Errno 10048] Address already in use`:

#### Windows (PowerShell / Command Prompt)
```powershell
# Identify process ID using port 8000
netstat -ano | findstr :8000

# Inspect process details
tasklist /FI "PID eq <PID>"

# Terminate process
taskkill /F /PID <PID>
```

#### Linux / macOS
```bash
# Find and terminate process on port 8000
lsof -i :8000
kill -9 <PID>
```

#### Running Backend on an Alternative Port
```bash
# Start Uvicorn on port 8001
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```
*Note: If changing backend port to 8001, update `VITE_API_URL` in `frontend/.env` or `frontend/src/services/api.js`.*

---

### Port 5173 Already in Use (Frontend)

Vite will automatically offer to use the next available port (e.g. `5174`). Alternatively:
```bash
npm run dev -- --port 3000
```

---

## 2. Environment & Dependency Issues

### Python Virtual Environment Not Activated or Missing Packages
```bash
cd backend
# Re-create virtual environment if corrupted
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'app'`
Set `PYTHONPATH` to the backend directory before running tests or python scripts:
```powershell
# Windows PowerShell
$env:PYTHONPATH="."
venv\Scripts\pytest.exe tests/ -v
```

---

## 3. Gemini API & Mock Fallback FAQ

### "Why is my LLM response coming from MockProvider?"
- **Cause**: `GOOGLE_API_KEY` is not set or invalid in `backend/.env`.
- **Solution**: Obtain a Gemini API key from Google AI Studio, set `GOOGLE_API_KEY=AIzaSy...` in `backend/.env`, and restart the Uvicorn server.
- **Behavior**: NeuroDesk AI is designed to fallback gracefully to `MockProvider` so developers can build and test full workflows offline without requiring an active API key.

---

## 4. Database Migration & Initialization Issues

### Database Table Not Found
```bash
cd backend
# Run database initialization script
venv\Scripts\python.exe -c "import asyncio; from app.database.session import init_db; asyncio.run(init_db())"
```

---

## 5. CORS Errors in Web Browser

### "Access to XMLHttpRequest at 'http://localhost:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy"
- **Cause**: Frontend origin is missing from `CORS_ORIGINS` in `backend/.env`.
- **Solution**: Ensure `CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173"]` is present in `backend/.env`.
