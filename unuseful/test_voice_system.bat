@echo off
echo Testing Voice Recognition System
echo ===============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Running comprehensive system test...
echo.

REM Test system components
python voice_ielts_questions.py --test-system

echo.
echo Listing available audio devices...
python voice_ielts_questions.py --list-devices

echo.
echo Listing available speech recognition engines...
python voice_ielts_questions.py --list-engines

echo.
echo Test completed. Check the results above.
pause
