@echo off
cd /d %~dp0
set PYTHONPATH=%~dp0
.venv\Scripts\uvicorn.exe api.main:app --host 0.0.0.0 --port 8000 --reload
