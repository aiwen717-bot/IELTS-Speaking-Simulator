@echo off
echo Testing Manual Recording Mode (No Auto-Stop)
echo ============================================

python voice_ielts_questions.py --voice-input --duration 10 --output_dir ./test_output --num_questions 3 --stt-engine whisper --verbose

echo.
echo Test completed. Check the log output above to verify:
echo - Should show "Manual stop mode enabled"
echo - Should NOT show "Silence detected" messages
echo - Should record for the full duration or until Ctrl+C
echo.
pause
