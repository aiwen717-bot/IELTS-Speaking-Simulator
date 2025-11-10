@echo off
echo Voice-driven IELTS Question Generator (Manual Stop - 4 Minutes Max)
echo ================================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Test system components first
echo Testing system components...
python voice_ielts_questions.py --test-system
if errorlevel 1 (
    echo.
    echo System test failed. Please check the error messages above.
    echo Make sure you have installed all dependencies by running:
    echo install_voice_dependencies.bat
    echo.
    pause
    exit /b 1
)

echo.
echo System test passed! Starting voice input mode...
echo.
echo Manual Stop Mode (4 Minutes Maximum):
echo - No automatic silence detection
echo - Maximum recording time: 4 minutes (240 seconds)
echo - You control when to stop recording
echo - Using Whisper engine for best accuracy
echo.
echo Instructions:
echo - You will be prompted to start recording
echo - Speak as long as you want into your microphone
echo - Press Ctrl+C when you finish speaking to stop recording
echo - Recording will automatically stop after 4 minutes if not stopped manually
echo - Try to speak for at least 10-15 seconds for better question generation
echo.

REM Run voice input mode with manual stop and 4-minute limit
python voice_ielts_questions.py --voice-input --duration 240 --output_dir ./voice_output --num_questions 5 --stt-engine whisper

echo.
echo Check the ./voice_output directory for generated files
pause
