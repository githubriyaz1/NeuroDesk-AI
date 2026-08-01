# NeuroDesk AI PowerShell Development Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting NeuroDesk AI Monorepo Development Stack" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "[1/2] Launching Backend FastAPI Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload --port 8000"

Write-Host "[2/2] Launching Frontend Vite Client..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`nEnvironment startup triggered successfully!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend Docs: http://localhost:8000/docs" -ForegroundColor Green
