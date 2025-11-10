@echo off
echo Installing Voice Recognition Dependencies...
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Installing dependencies...

REM Install core dependencies
echo Installing core speech recognition packages...
pip install SpeechRecognition>=3.10.0
if errorlevel 1 (
    echo Error installing SpeechRecognition
    pause
    exit /b 1
)

echo Installing audio processing packages...
pip install pyaudio>=0.2.11
if errorlevel 1 (
    echo Warning: PyAudio installation failed
    echo This might be due to missing system dependencies
    echo You may need to install PyAudio manually or use conda
    echo Continuing with other packages...
)

pip install numpy>=1.21.0
if errorlevel 1 (
    echo Error installing numpy
    pause
    exit /b 1
)

pip install scipy>=1.7.0
if errorlevel 1 (
    echo Error installing scipy
    pause
    exit /b 1
)

pip install pydub>=0.25.1
if errorlevel 1 (
    echo Error installing pydub
    pause
    exit /b 1
)

pip install sounddevice>=0.4.0
if errorlevel 1 (
    echo Warning: sounddevice installation failed
    echo Continuing without it...
)

echo.
echo ==========================================
echo Installation completed!
echo.
echo Optional: To install Whisper for offline speech recognition, run:
echo pip install openai-whisper
echo.
echo If PyAudio installation failed, try one of these alternatives:
echo 1. conda install pyaudio
echo 2. pip install pipwin && pipwin install pyaudio
echo 3. Download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/
echo.
pause
