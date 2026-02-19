@echo off
title SENTINEL - Object Detection System

echo ==========================================
echo   SENTINEL - Starting Services...
echo ==========================================
echo.

:: Start Backend
echo [1/2] Starting Backend (FastAPI)...
start "SENTINEL Backend" cmd /k "cd /d D:\YOLO\backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

:: Wait 4 seconds for backend to initialize
timeout /t 4 /nobreak > nul

:: Start Frontend
echo [2/2] Starting Frontend (React)...
start "SENTINEL Frontend" cmd /k "cd /d D:\YOLO\frontend && npm start"

:: Wait for frontend to compile then open browser
echo.
echo Waiting for frontend to compile...
timeout /t 8 /nobreak > nul

:: Open browser
echo Opening browser...
start http://localhost:3000

echo.
echo ==========================================
echo   SENTINEL is running!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   Close the two terminal windows to stop.
echo ==========================================
