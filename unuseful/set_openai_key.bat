@echo off
REM Script to set OpenAI API key

echo Setting up OpenAI API key for IELTS question generation
echo.
echo You need an OpenAI API key to generate IELTS questions.
echo If you don't have one, you can get it from: https://platform.openai.com/api-keys
echo.

set /p api_key="Enter your OpenAI API key: "

REM Create config file with the API key
echo Creating configuration file...
if not exist llm_module mkdir llm_module

echo {> llm_module\config.json
echo     "api_key": "%api_key%",>> llm_module\config.json
echo     "model": "gpt-3.5-turbo",>> llm_module\config.json
echo     "temperature": 0.7,>> llm_module\config.json
echo     "max_tokens": 500,>> llm_module\config.json
echo     "num_questions": 5,>> llm_module\config.json
echo     "tts_integration": {>> llm_module\config.json
echo         "enabled": true,>> llm_module\config.json
echo         "voice": "en-US-Neural2-F">> llm_module\config.json
echo     }>> llm_module\config.json
echo }>> llm_module\config.json

echo.
echo API key has been saved to llm_module\config.json
echo.
echo You can now run run_ielts_questions_tts.bat to generate IELTS questions.
echo.
echo Press any key to exit...
pause >nul
