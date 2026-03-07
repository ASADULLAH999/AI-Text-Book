@echo off
echo ========================================
echo   Testing RAG Chatbot API
echo ========================================
echo.

echo Test 1: Health Check
echo ---------------------
curl -s http://localhost:8000/api/v1/health
echo.
echo.

echo Test 2: Chat Endpoint
echo ---------------------
curl -s -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What is ROS2?\", \"mode\": \"book_only\"}"
echo.
echo.

echo ========================================
echo   Tests Complete
echo ========================================
pause
