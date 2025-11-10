@echo off
REM IELTS Question Generator with Improved Topic Extraction
REM This script runs the IELTS question generator with improved topic extraction

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

REM Ask which mode to use
echo.
echo Available question generation modes:
echo 1. Mock mode (uses predefined questions about friendship and meals)
echo 2. Template mode (uses improved topic extraction with templates)
echo 3. API mode (uses Qwen API - requires API key)
echo.
set /p mode="Select mode (1-3, default: 2): "

if "%mode%"=="" set mode=2

echo.
echo Generating IELTS Part 3 questions...

if "%mode%"=="1" (
    REM Use mock mode with predefined questions
    echo Using mock mode with predefined questions...
    
    REM Create a temporary Python script for mock generation
    echo import sys> mock_gen.py
    echo from llm_module.question_generator import IELTSQuestionGenerator>> mock_gen.py
    echo.>> mock_gen.py
    echo class MockGenerator:>> mock_gen.py
    echo     def generate_with_system_prompt(self, system_prompt, user_prompt):>> mock_gen.py
    echo         """Mock LLM that returns predefined questions based on the text.""">> mock_gen.py
    echo         return '''>> mock_gen.py
    echo 1. How do you think shared experiences like meals influence the development of close friendships?>> mock_gen.py
    echo 2. In what ways have social gatherings around food changed in recent years compared to traditional practices?>> mock_gen.py
    echo 3. What factors make certain memories, like your graduation meal, particularly significant in people's lives?>> mock_gen.py
    echo 4. How do you think technology has affected the way people maintain long-distance friendships compared to your experience?>> mock_gen.py
    echo 5. What role do you think educational institutions should play in fostering meaningful friendships among students?>> mock_gen.py
    echo         '''>> mock_gen.py
    echo.>> mock_gen.py
    echo # Create question generator with mock LLM>> mock_gen.py
    echo generator = IELTSQuestionGenerator(MockGenerator())>> mock_gen.py
    echo.>> mock_gen.py
    echo # Test with the input text>> mock_gen.py
    echo test_text = sys.argv[1]>> mock_gen.py
    echo num_questions = int(sys.argv[2])>> mock_gen.py
    echo.>> mock_gen.py
    echo # Generate questions>> mock_gen.py
    echo questions = generator.generate_questions(test_text, num_questions)>> mock_gen.py
    echo.>> mock_gen.py
    echo # Print results>> mock_gen.py
    echo print("Generated IELTS Part 3 questions:")>> mock_gen.py
    echo for i, question in enumerate(questions):>> mock_gen.py
    echo     print(f"{i+1}. {question}")>> mock_gen.py
    echo.>> mock_gen.py
    echo # Save to file>> mock_gen.py
    echo with open("output/ielts_questions.txt", "w") as f:>> mock_gen.py
    echo     for i, question in enumerate(questions):>> mock_gen.py
    echo         f.write(f"{i+1}. {question}\n")>> mock_gen.py
    
    REM Run the mock generator
    python mock_gen.py "%input_text%" %num_questions%
    
    REM Clean up
    del mock_gen.py
    
) else (
    if "%mode%"=="2" (
        REM Use template mode with improved topic extraction
        echo Using template mode with improved topic extraction...
        
        REM Create a temporary Python script for template-based generation
        echo import sys> template_gen.py
        echo from llm_module.text_processor import TextProcessor>> template_gen.py
        echo from llm_module.question_generator import IELTSQuestionGenerator>> template_gen.py
        echo.>> template_gen.py
        echo # Initialize components>> template_gen.py
        echo text_processor = TextProcessor()>> template_gen.py
        echo question_generator = IELTSQuestionGenerator()>> template_gen.py
        echo.>> template_gen.py
        echo # Process input text>> template_gen.py
        echo text = sys.argv[1]>> template_gen.py
        echo num_questions = int(sys.argv[2])>> template_gen.py
        echo.>> template_gen.py
        echo # Extract topics from text>> template_gen.py
        echo topics = text_processor.extract_topics(text)>> template_gen.py
        echo print("Extracted topics:", topics)>> template_gen.py
        echo.>> template_gen.py
        echo # Generate questions using template-based approach>> template_gen.py
        echo questions = question_generator._generate_template_questions(topics, num_questions)>> template_gen.py
        echo.>> template_gen.py
        echo # Print and save questions>> template_gen.py
        echo print("\nGenerated questions:")>> template_gen.py
        echo for i, question in enumerate(questions):>> template_gen.py
        echo     print(f"{i+1}. {question}")>> template_gen.py
        echo.>> template_gen.py
        echo # Save to file>> template_gen.py
        echo with open("output/ielts_questions.txt", "w") as f:>> template_gen.py
        echo     for i, question in enumerate(questions):>> template_gen.py
        echo         f.write(f"{i+1}. {question}\n")>> template_gen.py
        
        REM Run the template generator
        python template_gen.py "%input_text%" %num_questions%
        
        REM Clean up
        del template_gen.py
        
    ) else (
        if "%mode%"=="3" (
            REM Use Qwen API mode
            echo Using Qwen API for question generation...
            
            REM Check if config file exists
            if not exist llm_module\config.json (
                echo Qwen API key not set. Please run set_qwen_key.bat first.
                echo.
                echo Press any key to exit...
                pause >nul
                exit /b 1
            )
            
            REM Use the Qwen API for question generation
            python generate_ielts_questions.py --text "%input_text%" --num_questions %num_questions% --config llm_module\config.json --output_dir output %tts_flag% %combined_flag%
        ) else (
            echo Invalid mode selected. Using template mode...
            
            REM Use template mode with improved topic extraction (same as mode 2)
            echo import sys> template_gen.py
            echo from llm_module.text_processor import TextProcessor>> template_gen.py
            echo from llm_module.question_generator import IELTSQuestionGenerator>> template_gen.py
            echo.>> template_gen.py
            echo # Initialize components>> template_gen.py
            echo text_processor = TextProcessor()>> template_gen.py
            echo question_generator = IELTSQuestionGenerator()>> template_gen.py
            echo.>> template_gen.py
            echo # Process input text>> template_gen.py
            echo text = sys.argv[1]>> template_gen.py
            echo num_questions = int(sys.argv[2])>> template_gen.py
            echo.>> template_gen.py
            echo # Extract topics from text>> template_gen.py
            echo topics = text_processor.extract_topics(text)>> template_gen.py
            echo print("Extracted topics:", topics)>> template_gen.py
            echo.>> template_gen.py
            echo # Generate questions using template-based approach>> template_gen.py
            echo questions = question_generator._generate_template_questions(topics, num_questions)>> template_gen.py
            echo.>> template_gen.py
            echo # Print and save questions>> template_gen.py
            echo print("\nGenerated questions:")>> template_gen.py
            echo for i, question in enumerate(questions):>> template_gen.py
            echo     print(f"{i+1}. {question}")>> template_gen.py
            echo.>> template_gen.py
            echo # Save to file>> template_gen.py
            echo with open("output/ielts_questions.txt", "w") as f:>> template_gen.py
            echo     for i, question in enumerate(questions):>> template_gen.py
            echo         f.write(f"{i+1}. {question}\n")>> template_gen.py
            
            REM Run the template generator
            python template_gen.py "%input_text%" %num_questions%
            
            REM Clean up
            del template_gen.py
        )
    )
)
)

REM Process TTS if requested
if /i "%use_tts%"=="y" (
    echo.
    echo Converting questions to speech...
    
    if exist output\ielts_questions.txt (
        REM Create a Python script for TTS processing
        echo import sys, os>> tts_process.py
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
        
        REM Run the TTS processor
        python tts_process.py "%combined_flag:--combined=true%"
        
        REM Clean up
        del tts_process.py
    ) else (
        echo Error: Question file not found. TTS processing skipped.
    )
)

echo.
echo Press any key to exit...
pause >nul
