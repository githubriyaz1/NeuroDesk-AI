#!/usr/bin/env bash
# NeuroDesk AI One-Command Developer Script for Linux / macOS

set -e

ACTION="${1:-dev}"

echo "🧠⚡ NeuroDesk AI Developer Tooling [$ACTION]"

case "$ACTION" in
    setup)
        echo "--> Setting up Backend Virtual Environment..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..

        echo "--> Setting up Frontend Dependencies..."
        cd frontend
        npm install
        cd ..
        echo "✅ Setup complete!"
        ;;
    backend)
        echo "--> Launching FastAPI Backend on http://localhost:8000..."
        cd backend
        source venv/bin/activate
        uvicorn app.main:app --reload --port 8000
        ;;
    frontend)
        echo "--> Launching Vite Frontend on http://localhost:5173..."
        cd frontend
        npm run dev
        ;;
    test)
        echo "--> Running Backend Pytest Suite..."
        cd backend
        source venv/bin/activate
        pytest -v
        cd ..

        echo "--> Running Frontend Vitest Runner..."
        cd frontend
        npm run test:run
        cd ..
        ;;
    migrate)
        echo "--> Running Alembic Migrations..."
        cd backend
        source venv/bin/activate
        alembic upgrade head
        cd ..
        ;;
    docker-up)
        echo "--> Launching Docker Compose Stack..."
        docker-compose up -d --build
        ;;
    docker-down)
        echo "--> Stopping Docker Compose Stack..."
        docker-compose down
        ;;
    *)
        echo "Usage: ./dev.sh [setup | backend | frontend | test | migrate | docker-up | docker-down]"
        ;;
esac
