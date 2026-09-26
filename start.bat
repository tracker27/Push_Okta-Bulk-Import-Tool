@echo off
REM Okta Bulk Import Tool - Quick Start (Windows)
REM Runs the backend (FastAPI via its venv) and frontend (static index.html
REM via Python's http.server) directly in the background - no Docker required.

cd /d "%~dp0"

echo.
echo Okta Bulk Import Tool - Starting...
echo ====================================
echo.

if not exist "backend\.env" (
    echo [ERROR] backend\.env not found.
    echo Copy .env.example to backend\.env and fill in your Okta credentials.
    pause
    exit /b 1
)

if not exist "backend\venv" (
    echo [Setup] Creating Python virtual environment for backend...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    call venv\Scripts\deactivate.bat
    cd ..
)

echo [1/2] Starting backend on http://localhost:8000 (background)...
powershell -NoProfile -Command ^
  "Start-Process -FilePath '%~dp0backend\venv\Scripts\python.exe' -ArgumentList 'main.py' -WorkingDirectory '%~dp0backend' -WindowStyle Hidden -RedirectStandardOutput '%~dp0backend\backend_log.txt' -RedirectStandardError '%~dp0backend\backend_error.txt'"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend on http://localhost:3000 (background)...
for /f "delims=" %%P in ('where python') do set "PYEXE=%%P" & goto :gotpy
:gotpy
powershell -NoProfile -Command ^
  "Start-Process -FilePath '%PYEXE%' -ArgumentList '-m','http.server','3000' -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%~dp0frontend_log.txt' -RedirectStandardError '%~dp0frontend_error.txt'"

timeout /t 2 /nobreak >nul

echo.
echo Checking backend health...
powershell -NoProfile -Command ^
  "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 5; Write-Host ('Backend OK: ' + $r.StatusCode) } catch { Write-Host 'Backend not responding yet - check backend\backend_error.txt' }"

echo.
echo Ready! Opening http://localhost:3000
echo Logs: backend\backend_log.txt / backend\backend_error.txt (backend), frontend_log.txt (frontend)
echo Run stop.bat to shut it down, or restart.bat to restart after a code change.
echo.

start http://localhost:3000
