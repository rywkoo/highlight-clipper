@echo off
cd /d D:\Fun\ClipsAI
call .venv\Scripts\activate.bat

REM Run the Python app in the same console (blocks here)
start "" /b python app.py

REM Wait 10 seconds to allow server to start
timeout /t 10 /nobreak >nul

start http://127.0.0.1:5000

pause
