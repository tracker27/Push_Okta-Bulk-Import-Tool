@echo off
REM Restart the tool and immediately show live backend logs for debugging.
REM No Docker involved - tails the real backend_log.txt / backend_error.txt
REM written by backend\main.py (run via its venv).

cd /d "%~dp0"
call restart.bat

echo.
echo Tailing backend logs (Ctrl+C to stop watching - the app keeps running)...
echo.
powershell -NoProfile -Command "Get-Content -Path 'backend\backend_log.txt','backend\backend_error.txt' -Wait -Tail 20"
