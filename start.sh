#!/bin/bash
# Okta Bulk Import Tool - Quick Start (Mac/Linux)
# Runs the backend (FastAPI via its venv) and frontend (static index.html
# via Python's http.server) directly - no Docker required.

set -e
cd "$(dirname "$0")"

echo ""
echo "Okta Bulk Import Tool - Starting..."
echo "===================================="
echo ""

if [ ! -f "backend/.env" ]; then
    echo "[ERROR] backend/.env not found."
    echo "Copy .env.example to backend/.env and fill in your Okta credentials."
    exit 1
fi

if [ ! -d "backend/venv" ]; then
    echo "[Setup] Creating Python virtual environment for backend..."
    (cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && deactivate)
fi

echo "[1/2] Starting backend on http://localhost:8000 ..."
(cd backend && nohup ./venv/bin/python main.py > backend_log.txt 2> backend_error.txt &)

sleep 3

echo "[2/2] Starting frontend on http://localhost:3000 ..."
nohup python3 -m http.server 3000 > frontend_log.txt 2> frontend_error.txt &

sleep 2

echo ""
echo "Ready! Open http://localhost:3000"
echo "Logs: backend/backend_log.txt, backend/backend_error.txt, frontend_log.txt"
echo "Run ./stop.sh to shut it down."
echo ""
