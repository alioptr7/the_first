# 🐳 Docker Setup Guide - Response Network

## فهرست

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Build & Run](#build--run)
4. [Environment Variables](#environment-variables)
5. [Services](#services)
6. [Database Migrations](#database-migrations)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Clone repository
git clone <repo>
cd the_first

# 2. Create .env file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f api

# 5. Access API
# http://localhost:8000/docs
```

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

**آیا داکر دارید؟**
```bash
docker --version
docker-compose --version
```

اگر نه:
- [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Build & Run

### Development Mode (with auto-reload)

```bash
# از root directory
docker-compose up

# یا background
docker-compose up -d
```

### Production Mode

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Stop Services

```bash
docker-compose down

# با حذف volumes
docker-compose down -v
```

---

## Environment Variables

**Create `.env` file in root directory:**

```bash
# Database
DB_NAME=response_network
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_PORT=5432

# Redis
REDIS_PORT=6380

# API
API_PORT=8000

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
```

---

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **API (FastAPI)** | 8000 | REST API |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6380 | Broker & Cache |
| **Worker** | - | Celery Worker |
| **Beat** | - | Celery Scheduler |

### View Service Logs

```bash
# تمام services
docker-compose logs -f

# خاص یک service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f beat
```

### Check Service Status

```bash
docker-compose ps

# Output:
# NAME                   STATUS
# response_postgres      Up 2 minutes
# response_redis         Up 2 minutes
# response_api           Up 1 minute
# response_worker        Up 1 minute
# response_beat          Up 1 minute
```

---

## Database Migrations

### Run Migrations Automatically

Migrations اجرا می‌شوند **automatically** وقتی API شروع شود:

```python
# docker-compose.yml میں
command: >
  bash -c "
  alembic upgrade head &&
  python -m uvicorn main:app --host 0.0.0.0 --port 8000
  "
```

### Run Migrations Manually

```bash
docker-compose exec api alembic upgrade head

# یا specific version
docker-compose exec api alembic upgrade +1
```

### Create New Migration

```bash
docker-compose exec api alembic revision --autogenerate -m "Add new column"
```

---

## Monitoring

### FastAPI Docs

```
http://localhost:8000/docs
```

Login with:
- **Username:** admin
- **Password:** admin123

### API Endpoints

```bash
# Check API health
curl http://localhost:8000/api/v1/system/health

# List users
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users

# Admin - View queue
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/tasks/queue/stats

# Admin - View workers
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/tasks/workers/stats
```

### Redis Monitoring

```bash
# دخول به Redis container
docker-compose exec redis redis-cli -p 6380

# Commands
> INFO
> LLEN celery
> KEYS *
```

### Celery Monitoring

```bash
# View active tasks
docker-compose exec worker celery -A workers.celery_app inspect active

# View registered tasks
docker-compose exec worker celery -A workers.celery_app inspect registered

# Stats
docker-compose exec worker celery -A workers.celery_app inspect stats
```

---

## Troubleshooting

### API won't start

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Database connection failed
#    - Check DB_PASSWORD in .env
#    - Ensure postgres is running

# 2. Redis connection failed
#    - Check REDIS_PORT in .env
#    - Ensure redis is running
```

### Worker not executing tasks

```bash
# Check worker logs
docker-compose logs worker

# Verify worker is connected to Redis
docker-compose logs worker | grep "Connected to"

# Check if tasks are registered
docker-compose exec worker celery -A workers.celery_app inspect registered
```

### Beat not scheduling tasks

```bash
# Check beat logs
docker-compose logs beat

# Verify beat is running
docker-compose logs beat | grep "celery beat"
```

### Clear Redis Queue

```bash
docker-compose exec redis redis-cli -p 6380 DEL celery
```

### Rebuild Images

```bash
# Remove old images
docker-compose down

# Rebuild
docker-compose build --no-cache

# Start again
docker-compose up -d
```

---

## Performance Tuning

### Increase Worker Concurrency

```yaml
# docker-compose.yml
worker:
  environment:
    CELERYD_CONCURRENCY: 4  # تعداد processes
```

### Optimize Database Connection Pool

```yaml
api:
  environment:
    SQLALCHEMY_POOL_SIZE: 20
    SQLALCHEMY_MAX_OVERFLOW: 40
```

---

## Production Deployment

### Use Production Compose File

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    environment:
      # Security
      DEBUG: "false"
      SQLALCHEMY_ECHO: "false"
      # Performance
      WORKERS: 4
  
  worker:
    restart: always
  
  beat:
    restart: always
```

### Run with Production File

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres response_network > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres response_network < backup.sql
```

---

## Health Checks

### Verify All Services

```bash
#!/bin/bash
echo "Checking Docker services..."

# API
curl -s http://localhost:8000/api/v1/system/health | jq '.status'

# Database
docker-compose exec -T postgres pg_isready -U postgres

# Redis
docker-compose exec -T redis redis-cli -p 6380 ping

# Worker
docker-compose logs worker | grep "celery@" | tail -1

# Beat
docker-compose logs beat | grep "celery beat" | tail -1
```

---

## Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (⚠️ deletes data)
docker-compose down -v

# Remove all images
docker image prune -a

# Clean everything
docker system prune -a --volumes
```

---

## Next Steps

1. ✅ Setup Docker
2. ✅ Run services
3. ⏭️ Create admin user
4. ⏭️ Configure settings
5. ⏭️ Deploy to production

