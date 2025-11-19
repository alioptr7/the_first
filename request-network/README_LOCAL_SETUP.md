# Local Development Setup - Request Network

## Overview
This guide sets up the Request Network for local development without Docker Desktop.

## Prerequisites
- PostgreSQL 18 (already installed via Chocolatey)
- Redis (to be installed; see options below)
- Python 3.11+ with venv

## Setup Steps

### 1. Database Setup (PostgreSQL)

The following credentials are configured in `.env`:
- Username: `requests_user`
- Password: `requests_pass`
- Database: `requests_db`
- Host: `localhost`
- Port: `5432`

#### Option A: Create DB via SQL Script (if you know postgres password)
```bash
# In PowerShell (Admin)
$env:PGPASSWORD='<postgres_superuser_password>'
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h localhost -f 'C:\Users\win\the_first\init_db.sql'
```

#### Option B: Create DB via pgAdmin (GUI)
1. Open pgAdmin 4 from PostgreSQL folder
2. Connect to local PostgreSQL server
3. Create role `requests_user` with password `requests_pass`
4. Create database `requests_db` with owner `requests_user`

#### Option C: Use Docker Compose (if Docker is fixed)
```bash
cd request-network
docker-compose -f docker-compose.local.yml up -d
```
This will create isolated Postgres and Redis for request-network.

### 2. Redis Setup

Choose one option:

#### Option A: Use Redis-64 via Chocolatey (if installed)
- Service may not have started after nstall; start manually:
```bash
# Check if service exists
Get-Service | Where-Object Name -like "*redis*"

# If service exists, start it
Start-Service -Name Redis

# Verify connection
redis-cli ping   # expect: PONG
```

#### Option B: Use Docker Compose (recommended if Docker works)
```bash
cd request-network
docker-compose -f docker-compose.local.yml up -d
```

#### Option C: Manual Redis Installation (Windows)
- Download Memurai or prebuilt redis-server.exe
- Run redis-server in a terminal or register as service

### 3. Environment Variables (.env)
The `.env` file is pre-configured in `request-network/.env`:
```bash
REQUEST_DB_USER=requests_user
REQUEST_DB_PASSWORD=requests_pass
REQUEST_DB_HOST=localhost
REQUEST_DB_PORT=5432
REQUEST_DB_NAME=requests_db
REDIS_URL=redis://localhost:6379/0
```

### 4. Activate venv and Install Dependencies
```bash
cd C:\Users\win\the_first\request-network
. .\.venv\Scripts\Activate.ps1
pip install -r .\api\requirements.txt
```

### 5. Run Celery Worker (Request Network)
In PowerShell:
```bash
$env:PYTHONPATH='C:\Users\win\the_first'
. .\.venv\Scripts\Activate.ps1
python -m celery -A workers.celery_app.celery_app worker --loglevel=info
```

### 6. Run Celery Beat (Request Network)
In another PowerShell:
```bash
$env:PYTHONPATH='C:\Users\win\the_first'
. .\.venv\Scripts\Activate.ps1
python -m celery -A workers.celery_app.celery_app beat --loglevel=info
```

### 7. Run Tests
```bash
. .\.venv\Scripts\Activate.ps1
python -m pytest tests/test_simple.py -v
```

## Troubleshooting

### PostgreSQL Password Not Known
If the postgres superuser password was forgotten during installation:
1. Use pgAdmin GUI (included with PostgreSQL)
2. Or use Windows authentication (if installed with those options)
3. Or reinstall PostgreSQL with a known password

### Redis Not Found
- Run `where redis-cli` or `redis-server` to check if Redis is in PATH
- If not installed or path not set, use Docker Compose instead
- Or install Memurai (Windows-friendly Redis alternative)

### Connection Errors
- Verify services are running:
  - PostgreSQL: `Get-Service postgresql-x64-18` should show "Running"
  - Redis: `redis-cli ping` should return "PONG"
- Check firewall (ports 5432 and 6379 should be open locally)
- Verify `.env` file has correct credentials

### Celery Worker Can't Connect to Redis/Postgres
- Ensure `.env` file is in `request-network/` directory
- Verify PYTHONPATH includes repo root (so `shared` module is importable)
- Check that localhost services (Postgres, Redis) are actually running

## Next Steps: Response Network

Once Request Network is stable, Response Network can be set up:
- Response Network DB: `responses_db` (different database, same Postgres instance)
- Response Network Redis: Use Redis port 6380 (separate instance or same instance, different DB)
- See `response-network/` folder for similar setup instructions

## Docker Compose Notes

If Docker Desktop is repaired/updated, you can replace manual services with:
```bash
docker-compose -f docker-compose.local.yml down   # stop services
# Then manage everything via docker-compose going forward
```

The included `docker-compose.local.yml` defines isolated Postgres and Redis for development.
