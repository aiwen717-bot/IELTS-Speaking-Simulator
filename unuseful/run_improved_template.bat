@echo off
REM IELTS Question Generator using improved template mode
REM This script uses the improved topic extraction with template generation

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

echo.
echo Generating IELTS Part 3 questions using improved template mode...

REM Create a Python script for improved template generation
echo import sys> improved_template_gen.py
echo from llm_module.text_processor import TextProcessor>> improved_template_gen.py
echo from llm_module.question_generator import IELTSQuestionGenerator>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Initialize components>> improved_template_gen.py
echo text_processor = TextProcessor()>> improved_template_gen.py
echo question_generator = IELTSQuestionGenerator()>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Process input text>> improved_template_gen.py
echo text = sys.argv[1]>> improved_template_gen.py
echo num_questions = int(sys.argv[2])>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Extract improved topics from text>> improved_template_gen.py
echo topics = text_processor.extract_topics(text)>> improved_template_gen.py
echo print("Extracted topics:", topics)>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Generate questions using improved template-based approach>> improved_template_gen.py
echo questions = question_generator._generate_template_questions(topics, num_questions)>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Print and save questions>> improved_template_gen.py
echo print("\nGenerated questions:")>> improved_template_gen.py
echo for i, question in enumerate(questions):>> improved_template_gen.py
echo     print(f"{i+1}. {question}")>> improved_template_gen.py
echo.>> improved_template_gen.py
echo # Save to file>> improved_template_gen.py
echo with open("output/ielts_questions.txt", "w") as f:>> improved_template_gen.py
echo     for i, question in enumerate(questions):>> improved_template_gen.py
echo         f.write(f"{i+1}. {question}\n")>> improved_template_gen.py

REM Run the improved template generator with error handling
echo Running improved template generation...
python improved_template_gen.py "%input_text%" %num_questions% 2> template_error.log
if %errorlevel% neq 0 (
    echo Error running template generation. Check template_error.log for details.
    type template_error.log
    goto cleanup
)

echo.
echo Questions generated successfully!
echo Results saved to output\ielts_questions.txt

REM Ask if TTS is wanted
set /p use_tts="Generate speech for questions? (y/n, default: n): "

REM Process TTS if requested
if /i "%use_tts%"=="y" (
    echo.
    echo Converting questions to speech...
    
    REM Ask if combined audio is wanted
    set /p combined="Create combined audio file? (y/n, default: n): "
    
    REM Set combined flag
    set combined_value=false
    if /i "%combined%"=="y" set combined_value=true
    
    REM Create a Python script for TTS processing
    echo import sys, os> tts_process.py
    echo from llm_module.tts_integration import TTSIntegration>> tts_process.py
    echo.>> tts_process.py
    echo # Initialize TTS integration>> tts_process.py
    echo tts = TTSIntegration()>> tts_process.py
    echo.>> tts_process.py
    echo # Read questions from file>> tts_process.py
    echo questions = []>> tts_process.py
    echo with open("output/ielts_questions.txt", "r") as f:>> tts_process.py
    echo     for line in f:>> tts_process.py
    echo         if line.strip():>> tts_process.py
    echo             # Extract question text (remove numbering)>> tts_process.py
    echo             parts = line.strip().split(".", 1)>> tts_process.py
    echo             if len(parts) > 1:>> tts_process.py
    echo                 questions.append(parts[1].strip())>> tts_process.py
    echo.>> tts_process.py
    echo # Create output directory if it doesn't exist>> tts_process.py
    echo if not os.path.exists("output"):>> tts_process.py
    echo     os.makedirs("output")>> tts_process.py
    echo.>> tts_process.py
    echo # Process questions>> tts_process.py
    echo combined = sys.argv[1].lower() == "true">> tts_process.py
    echo result = tts.batch_process(questions, "output", combined)>> tts_process.py
    echo.>> tts_process.py
    echo # Print results>> tts_process.py
    echo print("\nGenerated audio files:")>> tts_process.py
    echo for i, file_path in sorted(result["individual_files"].items()):>> tts_process.py
    echo     print(f"Question {i+1}: {file_path}")>> tts_process.py
    echo.>> tts_process.py
    echo if result["combined_file"]:>> tts_process.py
    echo     print(f"\nCombined audio: {result['combined_file']}")>> tts_process.py
    
    REM Run the TTS processor with error handling
    echo Running TTS processing...
    python tts_process.py "%combined_value%" 2> tts_error.log
    if %errorlevel% neq 0 (
        echo Error running TTS processing. Check tts_error.log for details.
        type tts_error.log
        goto cleanup
    )
)

:cleanup
REM Clean up temporary files
if exist improved_template_gen.py del improved_template_gen.py
if exist tts_process.py del tts_process.py
if exist template_error.log del template_error.log
if exist tts_error.log del tts_error.log

echo.
echo Press any key to exit...
pause >nul
