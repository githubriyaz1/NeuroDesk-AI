@echo off
TITLE NeuroDesk AI Environment Initializer
echo ===================================================
echo   NeuroDesk AI Monorepo - Setup Dependencies
echo ===================================================

echo [1/3] Setting up Python virtual environment...
cd backend
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
)
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx

echo [2/3] Installing Frontend Node dependencies...
cd ..\frontend
call npm install

echo [3/3] Creating default .env files...
if not exist ".env" copy .env.example .env
cd ..\backend
if not exist ".env" copy .env.example .env

cd ..
echo.
echo ===================================================
echo Setup complete! You can now run scripts\start-dev.bat
echo ===================================================
