@echo off
:: Change to current working directory
cd /d "%CD%"

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Run Flask app in background
echo Starting Flask server...
start "" /b python app.py

:: Wait 10 seconds to allow server to start
timeout /t 10 /nobreak >nul

:: Open browser
start http://127.0.0.1:5000

pause
