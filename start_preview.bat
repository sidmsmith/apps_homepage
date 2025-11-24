@echo off
cd /d "%~dp0"
echo Starting preview server...
echo.
echo Preview available at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.
python preview_server.py 8080


