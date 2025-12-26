@echo off
REM Flutter Development Workflow Helper
REM ====================================
REM This script helps you run Flutter in development mode with hot reload

echo.
echo ============================================================
echo   Flutter Development Mode
echo ============================================================
echo.
echo INSTRUCTIONS:
echo 1. This will start your app on the connected device
echo 2. After it starts, you can make code changes
echo 3. Press 'r' in this terminal to HOT RELOAD (fast, keeps state)
echo 4. Press 'R' to HOT RESTART (slower, resets state)
echo 5. Press 'q' to quit
echo.
echo TIP: Keep this terminal open while developing!
echo      Don't close it and restart - just use 'r' for hot reload
echo.
echo ============================================================
echo.

cd /d "%~dp0"

REM Set Flutter path
set FLUTTER_PATH=C:\Users\Admin pc\Downloads\flutter_windows_3.38.5-stable\flutter\bin\flutter.bat

REM Run Flutter in debug mode (enables hot reload)
"%FLUTTER_PATH%" run

pause
