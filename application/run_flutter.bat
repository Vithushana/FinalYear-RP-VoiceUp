@echo off
REM Flutter Run Script with Java 19 (forcing Java 19 to be first in PATH)

echo Setting Java 19 for Gradle...

REM Set JAVA_HOME to Java 19
set "JAVA_HOME=C:\Program Files\Common Files\Oracle\Java\javapath\.."

REM Put Java 19 FIRST in PATH, before VS Code's Java 25
set "PATH=C:\Program Files\Common Files\Oracle\Java\javapath;%PATH%"

REM Clear JAVA_TOOL_OPTIONS
set JAVA_TOOL_OPTIONS=

echo Java version being used:
java -version

echo.
echo Starting Flutter app...
echo.

cd /d "C:\Users\Admin pc\Desktop\relevance_and_abuse_filteration_harish\new_version\application"

REM Use full path to flutter.bat
"C:\Users\Admin pc\Downloads\flutter_windows_3.38.5-stable\flutter\bin\flutter.bat" run

pause
