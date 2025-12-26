@echo off
echo ============================================================
echo   Flutter Clean Build - Force Reload Validation Code
echo ============================================================
echo.
echo This will:
echo 1. Clean Flutter build cache
echo 2. Get dependencies
echo 3. Rebuild the app with validation code
echo.
echo ============================================================
echo.

cd /d "C:\Users\Admin pc\Desktop\relevance_and_abuse_filteration_harish\new_version\application"

echo Step 1: Cleaning build cache...
call "C:\Users\Admin pc\Downloads\flutter_windows_3.38.5-stable\flutter\bin\flutter.bat" clean

echo.
echo Step 2: Getting dependencies...
call "C:\Users\Admin pc\Downloads\flutter_windows_3.38.5-stable\flutter\bin\flutter.bat" pub get

echo.
echo Step 3: Ready to run!
echo Now run: flutter run
echo.
echo ============================================================
echo IMPORTANT: After this, run 'flutter run' to rebuild the app
echo ============================================================
echo.
pause
