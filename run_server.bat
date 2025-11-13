@echo off
REM filepath: c:\Users\HP\OneDrive\Desktop\pvy\ml-model-project\run_server.bat

cd /d "%~dp0"
call venv\Scripts\activate.bat
python app.py
pause