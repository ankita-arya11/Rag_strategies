@echo off
echo ========================================
echo RAG Platform - Development Mode
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARN] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env and add your OPENAI_API_KEY
    pause
    exit /b 1
)

echo Starting Qdrant in Docker...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo ========================================
echo Qdrant is running!
echo ========================================
echo.
echo Qdrant Dashboard: http://localhost:6333/dashboard
echo.
echo Next steps:
echo 1. Open Terminal 1 - Run Backend:
echo    cd backend
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo    uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. Open Terminal 2 - Run Frontend:
echo    cd frontend
echo    npm install
echo    npm start
echo.
pause
