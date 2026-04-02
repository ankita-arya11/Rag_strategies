@echo off
echo Stopping Development Environment...
docker-compose -f docker-compose.dev.yml down
echo.
echo Qdrant stopped.
echo Remember to stop backend (Ctrl+C in terminal) and frontend (Ctrl+C in terminal)
pause
