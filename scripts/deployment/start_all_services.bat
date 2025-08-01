@echo off
setlocal enabledelayedexpansion

REM =================================================================
REM Enhanced Universal Service Launcher - Windows
REM Works from any location with proper path detection
REM =================================================================

echo =======================================================
echo   Multi-Place Fingerprint Attendance System Launcher
echo   Enhanced Universal Version
echo =======================================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
REM Navigate to project root (2 levels up from scripts/deployment)
cd /d "%SCRIPT_DIR%\..\.."
set "PROJECT_DIR=%CD%"

echo 📁 Working from: %PROJECT_DIR%
echo.
echo This will start all components of the system:
echo.
echo 1. Place 1 Backend (Port 8000) - Main Office
echo 2. Place 2 Backend (Port 8001) - Show Room  
echo 3. Place 3 Backend (Port 8002) - Warehouse
echo 4. Unified Gateway (Port 9000)
echo 5. Streamlit Frontend (Port 8501)
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found at %PROJECT_DIR%\.venv
    echo Please run setup_enhanced.bat first
    pause
    exit /b 1
)

REM Check if source files exist
if not exist "src\biometric_flow\backend\place_backend.py" (
    echo ❌ Backend source files not found
    echo Expected: src\biometric_flow\backend\place_backend.py
    pause
    exit /b 1
)

echo Press any key to start all services...
pause >nul

echo.
echo 🚀 Starting all services...
echo.

REM Start Place 1 Backend
echo Starting Place 1 Backend...
start "Place 1 Backend" cmd /k "cd /d "%PROJECT_DIR%" && scripts\deployment\start_place1_backend_enhanced.bat"
timeout /t 3 >nul

REM Start Place 2 Backend  
echo Starting Place 2 Backend...
start "Place 2 Backend" cmd /k "cd /d "%PROJECT_DIR%" && scripts\deployment\start_place2_backend_enhanced.bat"
timeout /t 3 >nul

REM Start Place 3 Backend
echo Starting Place 3 Backend...
start "Place 3 Backend" cmd /k "cd /d "%PROJECT_DIR%" && scripts\deployment\start_place3_backend_enhanced.bat"
timeout /t 3 >nul

REM Start Unified Gateway
echo Starting Unified Gateway...
start "Unified Gateway" cmd /k "cd /d "%PROJECT_DIR%" && scripts\deployment\start_unified_backend_enhanced.bat"
timeout /t 5 >nul

REM Start Frontend
echo Starting Frontend...
start "Frontend UI" cmd /k "cd /d "%PROJECT_DIR%" && scripts\deployment\start_frontend_enhanced.bat"

echo.
echo ✅ All services started! Access the system at:
echo   Frontend: http://localhost:8501
echo   Unified Gateway: http://localhost:9000
echo   Place 1 Backend: http://localhost:8000
echo   Place 2 Backend: http://localhost:8001  
echo   Place 3 Backend: http://localhost:8002
echo.
echo 📊 Check each terminal window for service status...
echo 📂 Running from: %PROJECT_DIR%
echo.
pause
