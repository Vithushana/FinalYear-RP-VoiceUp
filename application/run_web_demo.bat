@echo off
echo ========================================
echo VoiceUp Web Demo Launcher
echo ========================================
echo.

REM Check if Flutter is installed
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Flutter is not installed or not in PATH
    echo Please install Flutter SDK first
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
call flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Checking web support...
call flutter config --enable-web
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to enable web support
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Flutter Web Application...
echo.
echo ========================================
echo Web app will open in Chrome browser
echo Access URL: http://localhost:8080
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run Flutter web on port 8080
call flutter run -d chrome --web-port=8080

pause
