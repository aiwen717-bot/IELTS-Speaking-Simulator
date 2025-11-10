@echo off
echo Microphone Level Testing Tool
echo ============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo This tool will help you adjust your microphone settings.
echo.
echo What would you like to test?
echo 1. Test microphone input levels (recommended first)
echo 2. Test recording with different settings
echo 3. Both tests
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    python test_recording_settings.py --test-levels
) else if "%choice%"=="2" (
    echo.
    echo Testing with improved settings:
    echo - Lower silence threshold: 200
    echo - Longer silence duration: 4 seconds
    echo - Minimum recording time: 3 seconds
    echo.
    python test_recording_settings.py --test-recording --threshold 200 --silence-duration 4 --min-duration 3
) else if "%choice%"=="3" (
    python test_recording_settings.py --test-levels
    echo.
    echo Now testing recording...
    python test_recording_settings.py --test-recording --threshold 200 --silence-duration 4 --min-duration 3
) else (
    echo Invalid choice. Running both tests...
    python test_recording_settings.py --test-levels
    python test_recording_settings.py --test-recording --threshold 200 --silence-duration 4 --min-duration 3
)

echo.
pause
