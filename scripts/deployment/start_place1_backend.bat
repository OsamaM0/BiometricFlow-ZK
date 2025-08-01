@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo   Place 1 Backend (Main Office) - Enhanced
echo =====================================================

REM Get script directory and navigate to project root
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\..\.."
set "PROJECT_DIR=%CD%"

echo 📁 Project Directory: %PROJECT_DIR%
echo 🏢 Starting Place 1 Backend (Main Office)...
echo.

REM Check virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo Please run setup_enhanced.bat first
    pause
    exit /b 1
)

REM Check backend source file
if not exist "src\biometric_flow\backend\place_backend.py" (
    echo ❌ Backend source file not found: src\biometric_flow\backend\place_backend.py
    pause
    exit /b 1
)

REM Check config file
if not exist "config\devices_config_place1.json" (
    echo ❌ Configuration file not found: config\devices_config_place1.json
    pause
    exit /b 1
)

REM Set environment variables for Place 1
set BACKEND_NAME=Place_1_BackOffice
set BACKEND_PORT=8000
set BACKEND_LOCATION=Main Office Building
set DEVICES_CONFIG_FILE=config\devices_config_place1.json
set PYTHONPATH=%PROJECT_DIR%\src

echo ⚙️  Configuration:
echo   Backend Name: %BACKEND_NAME%
echo   Port: %BACKEND_PORT%
echo   Location: %BACKEND_LOCATION%
echo   Config File: %DEVICES_CONFIG_FILE%
echo   Python Path: %PYTHONPATH%
echo.

echo 🚀 Starting backend service...
.\.venv\Scripts\python.exe -m biometric_flow.backend.place_backend

echo.
echo ❌ Backend service stopped
pause
