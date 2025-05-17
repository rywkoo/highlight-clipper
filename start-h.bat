@echo off

cd /d "%CD%"

call .venv\Scripts\activate.bat

echo Starting Flask server...
start "" /b python app.py

timeout /t 10 /nobreak >nul

start http://127.0.0.1:5000

pause
