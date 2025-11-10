@echo off
echo Quick Voice Input (4 Minutes Max)
echo ==================================

python voice_ielts_questions.py --voice-input --duration 240 --output_dir ./voice_output --num_questions 5 --stt-engine whisper --verbose

echo.
echo Done! Check ./voice_output for your files.
pause
