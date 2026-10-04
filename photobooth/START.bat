@echo off
title STI Photobooth
color 0B

echo ============================================
echo   STI PHOTOBOOTH
echo ============================================
echo.

cd /d "%~dp0"

:: Start backend using venv
echo [1/2] Starting backend server...
if exist "backend\venv\Scripts\python.exe" (
    start "Photobooth Backend" cmd /k "cd backend && venv\Scripts\python.exe main.py"
) else (
    echo Creating venv and installing dependencies...
    cd backend
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
    start "Photobooth Backend" cmd /k "cd backend && venv\Scripts\python.exe main.py"
    cd ..
)

:: Wait for backend
timeout /t 4 /nobreak >nul

:: Start frontend
echo [2/2] Starting frontend server...
start "Photobooth Frontend" cmd /k "cd frontend && npx vite --host --port 3000"

echo.
echo ============================================
echo   Servers starting...
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo.
echo   Close this window or press Ctrl+C to stop
echo ============================================
pause
