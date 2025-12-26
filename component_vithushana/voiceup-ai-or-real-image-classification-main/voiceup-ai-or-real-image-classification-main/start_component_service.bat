@echo off
REM Quick Start Script for Component 2 Service
REM ==========================================
REM This script starts the AI vs Real Image Detection component

echo.
echo ============================================================
echo   Starting Component 2 Service (AI vs Real Detection)
echo ============================================================
echo.
echo Port: 5002
echo Endpoint: POST /analyze
echo Health Check: GET /health
echo.
echo ============================================================
echo.

REM Change to component directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if model file exists
if not exist "models\resnet50_ai_vs_real.pth" (
    echo WARNING: Model file not found
    echo Expected: models\resnet50_ai_vs_real.pth
    echo Please ensure the trained model is in the models directory
    echo.
    pause
)

REM Start the component service
echo Starting AI detection service...
echo.
python component_service.py

pause
