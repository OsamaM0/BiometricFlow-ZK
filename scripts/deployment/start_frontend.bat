@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo   Streamlit Frontend - Enhanced
echo =====================================================

REM Get script directory and navigate to project root
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\..\.."
set "PROJECT_DIR=%CD%"

echo 📁 Project Directory: %PROJECT_DIR%
echo 🖥️  Starting Streamlit Frontend...
echo.

REM === Load .env from root project directory ===
if exist "%PROJECT_DIR%\.env" (
    echo 🔄 Loading environment variables from .env...
    for /f "usebackq tokens=* delims=" %%a in ("%PROJECT_DIR%\.env") do (
        set "line=%%a"
        REM Skip empty lines and comments
        if not "!line!"=="" if "!line:~0,1!" neq "#" (
            for /f "tokens=1,* delims==" %%b in ("!line!") do (
                set "%%b=%%c"
            )
        )
    )
) else (
    echo ⚠️  .env file not found in %PROJECT_DIR%
)

REM Check virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo Please run setup_enhanced.bat first
    pause
    exit /b 1
)

REM Check streamlit executable
if not exist ".venv\Scripts\streamlit.exe" (
    echo ❌ Streamlit not found in virtual environment
    echo Please run setup_enhanced.bat first
    pause
    exit /b 1
)

REM Check frontend source file
if not exist "src\biometric_flow\frontend\app.py" (
    echo ❌ Frontend source file not found: src\biometric_flow\frontend\app.py
    pause
    exit /b 1
)

REM Set additional environment variables
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set PYTHONPATH=%PROJECT_DIR%\src

echo ⚙️  Configuration:
echo   Port: %STREAMLIT_SERVER_PORT%
echo   Address: %STREAMLIT_SERVER_ADDRESS%
echo   Backend URL: http://localhost:9000
echo   Python Path: %PYTHONPATH%
echo.

echo 🚀 Starting frontend service...
echo 📱 Access at: http://localhost:8501
echo.
.\.venv\Scripts\streamlit.exe run src\biometric_flow\frontend\app.py --server.port %STREAMLIT_SERVER_PORT% --server.address %STREAMLIT_SERVER_ADDRESS%

echo.
echo ❌ Frontend service stopped
pause
