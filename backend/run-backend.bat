@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed (or if uvicorn is missing)
set "NEEDS_INSTALL=0"
if not exist "venv\.installed" (
    set "NEEDS_INSTALL=1"
) else (
    python -c "import uvicorn" >nul 2>nul
    if errorlevel 1 (
        set "NEEDS_INSTALL=1"
    )
)

if "%NEEDS_INSTALL%"=="1" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Dependency installation failed.
        echo [TIP] Free up disk space and retry.
        echo [TIP] You can clear pip cache with: pip cache purge
        exit /b 1
    )
    echo. > venv\.installed
)

REM Check if .env exists in parent directory
if not exist "..\\.env" (
    echo [WARN] .env file not found in parent directory
    echo Make sure OPENAI_API_KEY is set
)

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
