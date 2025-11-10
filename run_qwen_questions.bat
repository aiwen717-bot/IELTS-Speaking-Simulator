@echo off
REM IELTS Question Generator using Qwen model
REM This script focuses only on using the Qwen API for high-quality question generation

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Check if requests library is installed
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests library...
    pip install requests
)

REM Create output directory if it doesn't exist
if not exist output mkdir output

REM Check if config file exists
if not exist llm_module\config.json (
    echo Qwen API key not set. Please run set_qwen_key.bat first.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

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

REM Ask if TTS is wanted
set /p use_tts="Generate speech for questions? (y/n, default: n): "

REM Set TTS flag based on input
set tts_flag=
if /i "%use_tts%"=="y" set tts_flag=--tts

REM Ask if combined audio is wanted (only if TTS is enabled)
set combined_flag=
if /i "%use_tts%"=="y" (
    set /p combined="Create combined audio file? (y/n, default: n): "
    if /i "%combined%"=="y" set combined_flag=--combined
)

echo.
echo Generating IELTS Part 3 questions using Qwen model...
echo This may take a moment...

REM Run the script with error handling
python generate_ielts_questions.py --text "%input_text%" --num_questions %num_questions% --config llm_module\config.json --output_dir output %tts_flag% %combined_flag% 2> qwen_error.log
if %errorlevel% neq 0 (
    echo.
    echo Error occurred while generating questions.
    echo Error details:
    type qwen_error.log
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo Questions generated successfully!
echo Results saved to output\ielts_questions.txt

if exist qwen_error.log del qwen_error.log

echo.
echo Press any key to exit...
pause >nul
