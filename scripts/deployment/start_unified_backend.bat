@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo   Unified Gateway Backend - Enhanced  
echo =====================================================

REM Get script directory and navigate to project root
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\..\.."
set "PROJECT_DIR=%CD%"

echo 📁 Project Directory: %PROJECT_DIR%
echo 🌐 Starting Unified Gateway Backend...
echo.

REM Check virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo Please run setup_enhanced.bat first
    pause
    exit /b 1
)

REM Check gateway source file
if not exist "src\biometric_flow\backend\unified_gateway.py" (
    echo ❌ Gateway source file not found: src\biometric_flow\backend\unified_gateway.py
    pause
    exit /b 1
)

REM Check backends config file
if not exist "config\unified_backends_config.json" (
    echo ❌ Configuration file not found: config\unified_backends_config.json
    pause
    exit /b 1
)

REM Set environment variables for Unified Gateway
set GATEWAY_PORT=9000
set FRONTEND_BACKEND_PORT=9001
set ALLOWED_ORIGINS=http://localhost:8501,http://localhost:9001
set PYTHONPATH=%PROJECT_DIR%\src

echo ⚙️  Configuration:
echo   Gateway Port: %GATEWAY_PORT%
echo   Frontend Backend Port: %FRONTEND_BACKEND_PORT%
echo   Allowed Origins: %ALLOWED_ORIGINS%
echo   Python Path: %PYTHONPATH%
echo.

echo 🚀 Starting unified gateway service...
.\.venv\Scripts\python.exe -m biometric_flow.backend.unified_gateway

echo.
echo ❌ Gateway service stopped
pause
