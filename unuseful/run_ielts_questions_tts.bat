@echo off
REM IELTS Question Generator with TTS Batch Script
REM This script runs the IELTS question generator with text input and converts to speech

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist output mkdir output

REM Ask for input text
set /p input_text="Enter your English text: "

REM Ask for number of questions
set /p num_questions="Enter number of questions to generate (default: 5): "

REM Set default if empty or validate input is a number
if "%num_questions%"=="" (
    set num_questions=5
) else (
    REM Check if input is a valid number
    echo %num_questions%| findstr /r "^[1-9][0-9]*$" >nul
    if errorlevel 1 (
        echo Invalid input. Using default value of 5 questions.
        set num_questions=5
    )
)

REM Ask if combined audio is wanted
set /p combined="Create combined audio file? (y/n, default: n): "

REM Set combined flag based on input
set combined_flag=
if /i "%combined%"=="y" set combined_flag=--combined

REM Run the script
echo.
echo Generating IELTS Part 3 questions with speech...
python generate_ielts_questions.py --text "%input_text%" --num_questions %num_questions% --tts --output_dir output %combined_flag%

echo.
echo Press any key to exit...
pause >nul
