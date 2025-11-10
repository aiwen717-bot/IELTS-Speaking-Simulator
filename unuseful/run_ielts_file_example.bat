@echo off
REM IELTS Question Generator Example with File Input
REM This script demonstrates using a file as input

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist output mkdir output

echo Using example_input.txt as input source...
echo.

REM Run the script
echo Generating IELTS Part 3 questions...
python generate_ielts_questions.py --file example_input.txt --num_questions 5 --output_dir output

echo.
echo Press any key to exit...
pause >nul
