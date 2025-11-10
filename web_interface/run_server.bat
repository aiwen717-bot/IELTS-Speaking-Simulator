@echo off
echo Starting IELTS Speaking Test Web Interface Server...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7+
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Flask and required packages...
    pip install flask flask-cors
)

REM Start the server
echo Starting web server on http://localhost:5000
python server.py
pause
