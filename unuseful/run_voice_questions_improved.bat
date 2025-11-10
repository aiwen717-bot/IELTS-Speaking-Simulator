@echo off
echo Voice-driven IELTS Question Generator (Improved Settings)
echo ========================================================

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
echo System test passed! Starting voice input mode with improved settings...
echo.
echo Improved Settings:
echo - Lower silence detection sensitivity
echo - Longer silence duration required (4 seconds instead of 2)
echo - Using Whisper engine for better accuracy
echo - Extended timeout periods
echo.
echo Instructions:
echo - You will be prompted to start recording
echo - Speak clearly and continuously into your microphone
echo - The system will wait for 4 seconds of silence before stopping
echo - You can also press Ctrl+C to stop recording manually
echo - Try to speak for at least 10-15 seconds for better results
echo.

REM Run voice input mode with improved settings
python voice_ielts_questions.py --voice-input --config voice_config_sensitive.json --output_dir ./voice_output --num_questions 5 --stt-engine whisper

echo.
echo Check the ./voice_output directory for generated files
pause
