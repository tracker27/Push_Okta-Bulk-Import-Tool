@echo off
REM Restart the Okta Bulk Import Tool (stop then start) with the latest code.
REM No Docker involved - this restarts the actual backend/frontend processes.

cd /d "%~dp0"
call stop.bat
timeout /t 2 /nobreak >nul
call start.bat
