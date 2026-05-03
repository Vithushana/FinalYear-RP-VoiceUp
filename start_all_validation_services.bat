@echo off
echo ============================================================
echo   Starting All Voice Up Services for Validation
echo ============================================================
echo.
echo This will start 4 services in separate windows:
echo 1. Main Backend (Port 5000)
echo 2. Component 1 - Harish (Port 5001) - Privacy/Abuse/Relevance
echo 3. Component 2 - Vithushana (Port 5002) - AI Detection/Garbage
echo 4. Component 3 - Tharsan (Port 5003) - Road Damage Detection
echo.
echo ============================================================
echo.

REM Terminal 1: Main Application Backend
start "Main Backend (Port 5000)" cmd /k "cd /d application\backend && python app.py"

timeout /t 2 /nobreak >nul

REM Terminal 2: Component 1 (Harish - Privacy/Relevance/Abuse)
start "Component 1 (Port 5001)" cmd /k "cd /d component_harish && python component_service.py"

timeout /t 2 /nobreak >nul

REM Terminal 3: Component 2 (Dual Service - AI/Garbage)
start "Component 2 (Port 5002)" cmd /k "cd /d component_vithushana && python run_component_2.py"

timeout /t 2 /nobreak >nul

REM Terminal 4: Component 3 (Tharsan - Road Damage Detection)
start "Component 3 - Tharsan (Port 5003)" cmd /k "cd /d component_tharsan && python ApiV3.py"

echo.
echo ✅ All services launched in separate windows!
echo.
echo 📍 Main Backend: http://localhost:5000
echo 📡 Component 1 (Harish): http://localhost:5001
echo 🤖 Component 2 (Vithushana): http://localhost:5002
echo 🛣️  Component 3 (Tharsan): http://localhost:5003
echo.
echo ============================================================
echo IMPORTANT: Keep all 4 windows open for validation to work!
echo ============================================================
echo.
pause
