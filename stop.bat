@echo off
REM Stops the Okta Bulk Import Tool backend (port 8000) and frontend (port 3000)

echo Stopping Okta Bulk Import Tool...

powershell -NoProfile -Command ^
  "Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction SilentlyContinue | " ^
  "Select-Object -ExpandProperty OwningProcess -Unique | " ^
  "ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue; Write-Host ('Stopped process ' + $_) }"

echo Done.
