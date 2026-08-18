# NeuroDesk AI One-Command PowerShell Developer Script
param (
    [string]$Action = "dev"
)

$ErrorActionPreference = "Stop"

Write-Host "🧠⚡ NeuroDesk AI Developer Tooling [$Action]" -ForegroundColor Cyan

switch ($Action) {
    "setup" {
        Write-Host "--> Setting up Backend Virtual Environment..." -ForegroundColor Yellow
        Set-Location backend
        if (-not (Test-Path "venv")) {
            python -m venv venv
        }
        .\venv\Scripts\activate
        pip install -r requirements.txt
        Set-Location ..

        Write-Host "--> Setting up Frontend Dependencies..." -ForegroundColor Yellow
        Set-Location frontend
        npm install
        Set-Location ..

        Write-Host "✅ NeuroDesk setup complete!" -ForegroundColor Green
    }
    "backend" {
        Write-Host "--> Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
        Set-Location backend
        .\venv\Scripts\activate
        uvicorn app.main:app --reload --port 8000
    }
    "frontend" {
        Write-Host "--> Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Green
        Set-Location frontend
        npm run dev
    }
    "test" {
        Write-Host "--> Running Backend Pytest Suite..." -ForegroundColor Yellow
        Set-Location backend
        .\venv\Scripts\activate
        pytest -v
        Set-Location ..

        Write-Host "--> Running Frontend Vitest Runner..." -ForegroundColor Yellow
        Set-Location frontend
        npm run test:run
        Set-Location ..
    }
    "migrate" {
        Write-Host "--> Running Alembic Database Migrations..." -ForegroundColor Yellow
        Set-Location backend
        .\venv\Scripts\activate
        alembic upgrade head
        Set-Location ..
    }
    "docker-up" {
        Write-Host "--> Launching Docker Compose Stack..." -ForegroundColor Green
        docker-compose up -d --build
    }
    "docker-down" {
        Write-Host "--> Stopping Docker Compose Stack..." -ForegroundColor Yellow
        docker-compose down
    }
    Default {
        Write-Host "Usage: .\dev.ps1 [setup | backend | frontend | test | migrate | docker-up | docker-down]" -ForegroundColor Yellow
    }
}
