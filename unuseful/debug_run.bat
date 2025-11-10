@echo off
REM Debug wrapper for run_with_improved_questions.bat
REM This script will run the main script and capture any errors

echo Running with debug mode enabled...
echo All output will be logged to debug_output.log
echo.

REM Enable command echoing to see which commands are being executed
echo on

REM Run the script and redirect all output to a log file
call run_with_improved_questions.bat > debug_output.log 2>&1

REM Disable command echoing
@echo off

echo.
echo Script execution completed.
echo Check debug_output.log for details.
echo.

echo Press any key to view the log file...
pause >nul

REM Display the log file
type debug_output.log

echo.
echo Press any key to exit...
pause >nul
