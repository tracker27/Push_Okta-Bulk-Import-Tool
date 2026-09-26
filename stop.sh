#!/bin/bash
# Stops the Okta Bulk Import Tool backend (port 8000) and frontend (port 3000)

echo "Stopping Okta Bulk Import Tool..."

for port in 8000 3000; do
    pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null || true
        echo "Stopped process on port $port (PID $pid)"
    fi
done

echo "Done."
