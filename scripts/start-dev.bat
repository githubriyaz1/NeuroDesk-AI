@echo off
TITLE NeuroDesk AI Local Development Server Launcher
echo ===================================================
echo   Starting NeuroDesk AI Monorepo Development Environment
echo ===================================================

echo [1/2] Launching Backend FastAPI Server (Port 8000)...
start "NeuroDesk Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Frontend Vite Server (Port 5173)...
start "NeuroDesk Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo Both services are starting!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://localhost:8000/docs
echo ===================================================
