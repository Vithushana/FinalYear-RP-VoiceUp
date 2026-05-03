@echo off
echo ============================================================
echo   Install Existing APK to Phone
echo ============================================================
echo.
echo This will install the existing app-debug.apk to your phone
echo Make sure your phone is connected via USB with USB debugging enabled
echo.
echo ============================================================
echo.

REM Set ADB path from Android SDK
set ADB_PATH="C:\Users\Admin pc\AppData\Local\Android\Sdk\platform-tools\adb.exe"

REM Check if ADB exists
if not exist %ADB_PATH% (
    echo ERROR: ADB not found at %ADB_PATH%!
    echo Please install Android SDK Platform Tools
    echo.
    pause
    exit /b 1
)

REM Check if device is connected
%ADB_PATH% devices | findstr "device$" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No device connected!
    echo Please connect your phone via USB and enable USB debugging
    echo.
    pause
    exit /b 1
)

echo Installing APK...
%ADB_PATH% install -r "android\app\build\outputs\flutter-apk\app-debug.apk"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo ✅ APK installed successfully!
    echo ============================================================
    echo.
    echo Now you can:
    echo 1. Start backend services: start_all_validation_services.bat
    echo 2. Open the app on your phone
    echo 3. Test validation features!
    echo.
) else (
    echo.
    echo ============================================================
    echo ❌ Installation failed!
    echo ============================================================
    echo.
)

pause
