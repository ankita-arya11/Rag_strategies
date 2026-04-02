@echo off
echo ========================================
echo RAG Strategies Platform - Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo [1/4] Checking environment file...
if not exist .env (
    echo [WARN] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env file and add your OPENAI_API_KEY
    echo Then run this script again.
    pause
    exit /b 1
)

echo [2/4] Stopping existing containers...
docker-compose down

echo.
echo [3/4] Building and starting all services...
echo This may take a few minutes on first run...
docker-compose up --build -d

echo.
echo [4/4] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo Services are starting!
echo ========================================
echo.
echo Frontend:        http://localhost:3000
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Qdrant Dashboard: http://localhost:6333/dashboard
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
