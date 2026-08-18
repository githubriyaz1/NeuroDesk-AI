@echo off
REM NeuroDesk AI One-Command Windows CMD Developer Script

IF "%1"=="setup" GOTO setup
IF "%1"=="backend" GOTO backend
IF "%1"=="frontend" GOTO frontend
IF "%1"=="test" GOTO test
IF "%1"=="migrate" GOTO migrate
IF "%1"=="docker-up" GOTO docker-up
IF "%1"=="docker-down" GOTO docker-down

echo Usage: dev.bat [setup ^| backend ^| frontend ^| test ^| migrate ^| docker-up ^| docker-down]
GOTO end

:setup
echo Setting up Backend...
cd backend
if not exist venv python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt
cd ..
echo Setting up Frontend...
cd frontend
npm install
cd ..
GOTO end

:backend
cd backend
call .\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
GOTO end

:frontend
cd frontend
npm run dev
GOTO end

:test
cd backend
call .\venv\Scripts\activate
pytest -v
cd ..
cd frontend
npm run test:run
cd ..
GOTO end

:migrate
cd backend
call .\venv\Scripts\activate
alembic upgrade head
cd ..
GOTO end

:docker-up
docker-compose up -d --build
GOTO end

:docker-down
docker-compose down
GOTO end

:end
