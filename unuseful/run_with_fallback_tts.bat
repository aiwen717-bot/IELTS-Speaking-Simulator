@echo off
REM IELTS Question Generator with Fallback TTS
REM This script uses pyttsx3 as a fallback TTS system

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Install pyttsx3 if not already installed
pip show pyttsx3 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pyttsx3...
    pip install pyttsx3
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

REM Create a simple fallback TTS script
echo import pyttsx3> fallback_tts.py
echo import sys>> fallback_tts.py
echo.>> fallback_tts.py
echo def text_to_speech(text, output_file):>> fallback_tts.py
echo     engine = pyttsx3.init()>> fallback_tts.py
echo     engine.setProperty('rate', 150)>> fallback_tts.py
echo     engine.setProperty('volume', 0.9)>> fallback_tts.py
echo     engine.save_to_file(text, output_file)>> fallback_tts.py
echo     engine.runAndWait()>> fallback_tts.py
echo.>> fallback_tts.py
echo if __name__ == "__main__":>> fallback_tts.py
echo     if len(sys.argv) != 3:>> fallback_tts.py
echo         print("Usage: python fallback_tts.py 'text to speak' output_file.wav")>> fallback_tts.py
echo         sys.exit(1)>> fallback_tts.py
echo     text_to_speech(sys.argv[1], sys.argv[2])>> fallback_tts.py

REM Run the script to generate questions
echo.
echo Generating IELTS Part 3 questions...
python generate_ielts_questions.py --text "%input_text%" --num_questions %num_questions% --output_dir output

REM Check if questions were generated
if not exist output\ielts_questions.txt (
    echo Failed to generate questions.
    echo Please run set_openai_key.bat to set your OpenAI API key.
    goto cleanup
)

REM Read the generated questions
echo.
echo Converting questions to speech using fallback TTS...
for /f "tokens=1,* delims=." %%a in (output\ielts_questions.txt) do (
    set question=%%b
    if not "!question!"=="" (
        set question_num=%%a
        set question_num=!question_num: =!
        echo Converting question !question_num! to speech...
        python fallback_tts.py "!question!" "output\question_!question_num!.wav"
    )
)

echo.
echo Speech generation complete. Audio files are in the output directory.

:cleanup
REM Clean up temporary files
del fallback_tts.py

echo.
echo Press any key to exit...
pause >nul
