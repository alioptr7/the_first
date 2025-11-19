@echo off
REM Start Celery Beat for Request Network

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

REM Start Celery beat
echo.
echo Starting Celery Beat for Request Network...
python -m celery -A workers.celery_app.celery_app beat --loglevel=info

pause
