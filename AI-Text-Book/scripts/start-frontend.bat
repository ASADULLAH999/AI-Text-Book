@echo off
echo ========================================
echo   Starting Docusaurus Frontend
echo ========================================
echo.

cd /d "%~dp0..\"

echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm start
pause
