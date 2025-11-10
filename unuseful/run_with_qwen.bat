@echo off
REM IELTS Question Generator using Qwen model
REM This script runs the IELTS question generator with Qwen API

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

REM Run the script
echo.
echo Generating IELTS Part 3 questions using Qwen model...

REM Check if API is available, if not use fallback mode
set /p use_api="Use Qwen API for question generation? (y/n, default: y): "

if /i "%use_api%"=="n" (
    echo Using fallback mode with improved topic extraction...
    
    REM Create a temporary Python script for fallback generation
    echo import sys> fallback_gen.py
    echo from llm_module.text_processor import TextProcessor>> fallback_gen.py
    echo from llm_module.question_generator import IELTSQuestionGenerator>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Initialize components>> fallback_gen.py
    echo text_processor = TextProcessor()>> fallback_gen.py
    echo question_generator = IELTSQuestionGenerator()>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Process input text>> fallback_gen.py
    echo text = sys.argv[1]>> fallback_gen.py
    echo num_questions = int(sys.argv[2])>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Extract topics from text>> fallback_gen.py
    echo topics = text_processor.extract_topics(text)>> fallback_gen.py
    echo print("Extracted topics:", topics)>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Generate questions using template-based approach>> fallback_gen.py
    echo questions = question_generator._generate_template_questions(topics, num_questions)>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Print and save questions>> fallback_gen.py
    echo print("\nGenerated questions:")>> fallback_gen.py
    echo for i, question in enumerate(questions):>> fallback_gen.py
    echo     print(f"{i+1}. {question}")>> fallback_gen.py
    echo.>> fallback_gen.py
    echo # Save to file>> fallback_gen.py
    echo with open("output/ielts_questions.txt", "w") as f:>> fallback_gen.py
    echo     for i, question in enumerate(questions):>> fallback_gen.py
    echo         f.write(f"{i+1}. {question}\n")>> fallback_gen.py
    
    REM Run the fallback generator
    python fallback_gen.py "%input_text%" %num_questions%
    
    REM Clean up
    del fallback_gen.py
) else (
    REM Use the Qwen API for question generation
    python generate_ielts_questions.py --text "%input_text%" --num_questions %num_questions% --config llm_module\config.json --output_dir output %tts_flag% %combined_flag%
)

echo.
echo Press any key to exit...
pause >nul
