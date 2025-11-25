# 🚀 Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Python 3.11+
- Git

## Step 1: Verify Setup ✓

```bash
./validate_setup.sh
```

All checks should pass.

## Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (especially SECRET_KEY and passwords)
```

## Step 3: Start Services

### Option A: Full Stack (Both Networks)
```bash
docker-compose -f docker-compose.dev.yml up -d --profile all
```

### Option B: Response Network Only
```bash
docker-compose up -d
```

### Option C: Request Network Only
```bash
docker-compose -f docker-compose.dev.yml up -d --profile request
```

## Step 4: Verify Services

```bash
# Check all containers are running
docker ps

# View logs
docker-compose logs -f api

# Check database is initialized
docker-compose exec api python manage.py init

# Seed initial data (Response Network only)
docker-compose exec api python manage.py seed
```

## Step 5: Test the API

### Response Network API
```bash
# Health check
curl http://localhost:8000/health

# View API docs
# Open: http://localhost:8000/docs
```

### Request Network API (if running)
```bash
# Health check
curl http://localhost:8001/health
```

## ✅ Common Setup Tasks

### Access the Admin Panel
```
http://localhost:3000/admin
Username: admin
Password: admin@123456
```

### View Elasticsearch Status
```bash
curl http://localhost:9200/_cluster/health
```

### Check Redis
```bash
docker-compose exec redis redis-cli INFO
```

### Access PostgreSQL
```bash
# Response Network
PGPASSWORD=postgres psql -h localhost -U postgres -d response_network

# Request Network (port 5433)
PGPASSWORD=postgres psql -h localhost -U postgres -d request_network -p 5433
```

### View Celery Tasks (if Flower installed)
```
# Response Network: http://localhost:5556
# Request Network: http://localhost:5555
```

## 🔄 Data Import/Export

### Manual User Sync
```bash
# Export users from Response Network
docker-compose exec api python -m workers.tasks.users_exporter

# Import users to Request Network
docker-compose -f docker-compose.dev.yml exec api-request python -m workers.tasks.users_importer
```

## 📊 Monitoring

### View Real-time Logs
```bash
docker-compose logs -f api worker beat
```

### Database Migrations
```bash
# Run migrations
docker-compose exec api python manage.py migrate

# Check migration status
docker-compose exec api python -m alembic current
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

### Import/Export Not Working
1. Verify export directories exist: `ls response-network/api/exports/`
2. Check file permissions: `chmod -R 777 response-network/api/exports/`
3. View task logs: `docker-compose logs worker`

### PYTHONPATH Issues
The PYTHONPATH is automatically set in Dockerfiles. If running locally:
```bash
export PYTHONPATH="/workspaces/the_first:/workspaces/the_first/response-network/api"
```

## 📚 Important Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and critical setup information
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Comprehensive setup procedures
- **[TODO.md](./TODO.md)** - Development tasks and progress tracking

## 🔗 Useful Links

- **FastAPI Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6380
- **Elasticsearch**: http://localhost:9200
- **Admin Panel**: http://localhost:3000 (when running)

---

**Need Help?** Check the [ARCHITECTURE.md](./ARCHITECTURE.md) for critical setup information or review the [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed procedures.
