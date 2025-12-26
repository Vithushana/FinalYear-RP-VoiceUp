@echo off
REM Quick Start Script for Component Service
REM ==========================================
REM This script starts Harish's validation component as a separate service

echo.
echo ============================================================
echo   Starting Component Service (Harish's Validation)
echo ============================================================
echo.
echo Port: 5001
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

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please create .env file with model_auth_key
    echo.
)

REM Start the component service
echo Starting component service...
echo.
python component_service.py

pause
