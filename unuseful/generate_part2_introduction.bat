@echo off
echo Generating Part 2 introduction audio...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7+
    pause
    exit /b 1
)

REM Run the Python script to generate the audio
python generate_introduction_audio.py

echo Done.
pause
