@echo off
echo ========================================
echo Starting Frontend Development Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Check if .env exists in parent directory
if not exist "..\\.env" (
    echo [INFO] Creating .env from parent .env...
    if exist "..\\.env" (
        copy "..\\.env" ".env"
    )
)

echo.
echo Starting React development server on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start
