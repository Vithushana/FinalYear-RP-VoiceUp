@echo off
echo ========================================
echo Flutter App Runner - Voice Up IME
echo ========================================
echo.

set FLUTTER_PATH=C:\Users\Admin pc\Downloads\flutter_windows_3.38.5-stable\flutter\bin

echo Checking connected devices...
echo.
"%FLUTTER_PATH%\flutter.bat" devices
echo.

echo ========================================
echo If you see your phone listed above, press any key to run the app.
echo If not, please:
echo   1. Connect your phone via USB
echo   2. Enable USB Debugging in Developer Options
echo   3. Allow USB debugging on your phone
echo   4. Run this script again
echo ========================================
pause

echo.
echo Running app on connected device...
echo.
"%FLUTTER_PATH%\flutter.bat" run

pause
