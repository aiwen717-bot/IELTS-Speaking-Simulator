@echo off
echo Voice-driven IELTS Question Generator (Manual Stop Mode)
echo =======================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Manual Stop Mode - No automatic silence detection
echo This mode requires you to manually stop recording with Ctrl+C
echo.
echo Instructions:
echo - You will be prompted to start recording
echo - Speak as long as you want into your microphone
echo - Press Ctrl+C when you finish speaking to stop recording
echo - The system will NOT automatically stop on silence
echo.

REM Run voice input mode with manual stop (no auto-silence detection)
python voice_ielts_questions.py --voice-input --output_dir ./voice_output --num_questions 5 --stt-engine whisper --duration 60

echo.
echo Check the ./voice_output directory for generated files
pause
