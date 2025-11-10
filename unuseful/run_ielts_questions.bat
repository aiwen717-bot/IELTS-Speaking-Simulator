@echo off
REM IELTS Question Generator Batch Script
REM This script runs the IELTS question generator with text input

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

REM Run the script
echo.
echo Generating IELTS Part 3 questions...
python generate_ielts_questions.py --text "%input_text%" --output_dir output

echo.
echo Press any key to exit...
pause >nul
