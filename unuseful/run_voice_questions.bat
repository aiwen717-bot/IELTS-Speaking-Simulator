@echo off
echo Voice-driven IELTS Question Generator
echo ====================================

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
echo Instructions:
echo - You will be prompted to start recording
echo - Speak clearly into your microphone
echo - The system will automatically stop after 2 seconds of silence
echo - Or press Ctrl+C to stop recording manually
echo.

REM Run voice input mode
python voice_ielts_questions.py --voice-input --output_dir ./voice_output --num_questions 5

echo.
echo Check the ./voice_output directory for generated files
pause
