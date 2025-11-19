@echo off
REM Start PostgreSQL Service (should already be running as Windows service)
echo Starting PostgreSQL service...
net start "postgresql-x64-18" > nul 2>&1
timeout /t 2

REM Note: Redis needs to be started separately or as a service
REM If you have redis-server.exe, uncomment and adjust path:
REM start "Redis Server" "C:\path\to\redis-server.exe"

REM For now, set environment variables and activate venv
setlocal enabledelayedexpansion
cd /d C:\Users\win\the_first\request-network

REM Set environment variables for this session
set REQUEST_DB_USER=requests_user
set REQUEST_DB_PASSWORD=SecurePass123!
set REQUEST_DB_HOST=localhost
set REQUEST_DB_PORT=5432
set REQUEST_DB_NAME=requests_db
set REDIS_URL=redis://localhost:6379/0
set PYTHONPATH=C:\Users\win\the_first

REM Activate venv
call .venv\Scripts\activate.bat

REM Install requirements if needed
pip install -r api\requirements.txt -q

REM Start Celery worker
echo.
echo Starting Celery Worker for Request Network...
python -m celery -A workers.celery_app.celery_app worker --loglevel=info

endlocal
pause
