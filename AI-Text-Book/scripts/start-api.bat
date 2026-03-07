@echo off
echo ========================================
echo   Starting RAG Chatbot API Server
echo ========================================
echo.

cd /d "%~dp0..\api"

echo Checking environment variables...
if not exist ".env" (
    echo ERROR: api/.env file not found!
    echo Please create it from .env.template
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server on http://localhost:8000
echo API docs will be available at: http://localhost:8000/api/v1/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python src\main.py
pause
