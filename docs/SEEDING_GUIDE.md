# 🌱 Database Seeding and Initialization Guide

## Overview

The project provides comprehensive database initialization and seeding mechanisms to support both development and production environments.

## Quick Start

### Response Network (Master)

#### Automatic Setup (Recommended)
```bash
cd /workspaces/the_first
chmod +x setup_env.sh
./setup_env.sh
```

This script:
1. ✅ Exports `PYTHONPATH`
2. ✅ Runs database migrations
3. ✅ Creates admin user
4. ✅ Seeds sample users
5. ✅ Displays credentials

#### Manual Setup

```bash
cd /workspaces/the_first

# Set PYTHONPATH
export PYTHONPATH="/workspaces/the_first:${PYTHONPATH}"

# Run migrations
cd response-network/api
python -m alembic upgrade head

# Seed data
cd /workspaces/the_first
python manage_db.py seed --network response
```

### Request Network (Secondary)

#### Automatic Setup
```bash
cd /workspaces/the_first
chmod +x setup_request_network.sh
./setup_request_network.sh
```

#### Manual Setup

```bash
cd /workspaces/the_first

# Set PYTHONPATH
export PYTHONPATH="/workspaces/the_first:${PYTHONPATH}"

# Run migrations
cd request-network/api
python -m alembic upgrade head

# Initialize
cd /workspaces/the_first
python manage_db.py seed --network request
```

## Management Commands

### Seed Data

```bash
export PYTHONPATH="/workspaces/the_first:${PYTHONPATH}"

# Seed both networks
python manage_db.py seed

# Seed only Response Network
python manage_db.py seed --network response

# Seed only Request Network
python manage_db.py seed --network request
```

### Drop All Data (Destructive)

```bash
# Drop data from both networks (after confirmation)
python manage_db.py drop-all

# Drop only Response Network
python manage_db.py drop-all --network response

# Drop only Request Network
python manage_db.py drop-all --network request
```

## Docker Integration

### Dockerfile Setup

The Dockerfiles are configured to automatically seed data during container initialization:

```dockerfile
# Set PYTHONPATH for imports
ENV PYTHONPATH="/app:${PYTHONPATH}"

# During entrypoint:
RUN python manage_db.py seed --network response
```

### Docker Compose

In `docker-compose.yml`, services automatically run setup on first start:

```yaml
response-network:
  environment:
    - SEED_DATA=true  # Enable seeding
```

To disable seeding in production:
```yaml
response-network:
  environment:
    - SEED_DATA=false  # Skip seeding
```

## Default Credentials

### Response Network Admin User
- **Username:** `admin`
- **Password:** `admin@123456`
- **Email:** `admin@example.com`
- **Limits:** 
  - Daily: 10,000 requests
  - Monthly: 100,000 requests

### Sample Users

#### Basic User
- **Username:** `user_basic`
- **Password:** `user@123456`
- **Email:** `basic@example.com`
- **Limits:**
  - Daily: 100 requests
  - Monthly: 2,000 requests

#### Premium User
- **Username:** `user_premium`
- **Password:** `user@123456`
- **Email:** `premium@example.com`
- **Limits:**
  - Daily: 1,000 requests
  - Monthly: 20,000 requests

## Seed Data Architecture

### Entry Points

1. **CLI Command** (`manage_db.py`)
   - Used for manual seeding from command line
   - Supports individual network selection
   - Best for development and testing

2. **Init Setup** (`response-network/api/setup/init_setup.py`)
   - Runs during initial Response Network setup
   - Creates admin user automatically
   - Can seed sample data if `SEED_DATA=true` env var

3. **Initialization Module** (`response-network/api/setup/initialization.py`)
   - Programmatic interface for seeding
   - Used by FastAPI startup events
   - Can be called during application initialization

### File Locations

```
├── manage_db.py                           # Main CLI tool
├── setup_env.sh                           # Response Network setup script
├── setup_request_network.sh               # Request Network setup script
├── response-network/api/
│   └── setup/
│       ├── init_setup.py                  # Initial setup script
│       └── initialization.py              # Programmatic interface
└── request-network/api/
    └── setup/
        └── initialization.py              # Request Network init
```

## Development Workflow

### 1. Fresh Start

```bash
# Setup Response Network
./setup_env.sh

# In another terminal, setup Request Network
./setup_request_network.sh

# Start services
docker-compose -f docker-compose.dev.yml --profile response up -d
docker-compose -f docker-compose.dev.yml --profile request up -d

# Start API servers
# Terminal 1: Response Network
cd response-network/api
PYTHONPATH="/workspaces/the_first:${PYTHONPATH}" python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Request Network
cd request-network/api
PYTHONPATH="/workspaces/the_first:${PYTHONPATH}" python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### 2. Resetting Data

```bash
# Drop all data from Response Network
python manage_db.py drop-all --network response

# Reseed
python manage_db.py seed --network response
```

### 3. Custom Seeding

To seed additional custom users, edit `manage_db.py`:

```python
# In seed_response_network() function
sample_users = [
    # ... existing users
    {
        "username": "your_username",
        "email": "your@email.com",
        "password": "your_password",
        "profile_type": "custom",
        "daily_limit": 500,
        "monthly_limit": 5000,
    },
]
```

Then run:
```bash
python manage_db.py seed --network response
```

## Production Deployment

### Docker Production Build

```dockerfile
# Production Dockerfile automatically sets PYTHONPATH
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Seed only if environment variable is set
RUN if [ "$SEED_DATA" = "true" ]; then \
    python manage_db.py seed --network response; \
    fi
```

### Environment Variables

```bash
# Enable seeding during container initialization
SEED_DATA=true      # Development
SEED_DATA=false     # Production (after initial setup)
```

### Production Setup Steps

```bash
# 1. Build images
docker build -f Dockerfile -t response-network:latest .

# 2. Start database only (first run)
docker-compose -f docker-compose.yml up -d postgres redis elasticsearch

# 3. Run migrations
docker run --rm \
  -e DATABASE_URL="postgresql://..." \
  response-network:latest \
  python -m alembic upgrade head

# 4. Seed data (if needed)
docker run --rm \
  -e PYTHONPATH="/app" \
  response-network:latest \
  python manage_db.py seed --network response

# 5. Start all services
docker-compose -f docker-compose.yml up -d
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'shared'`:

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/workspaces/the_first:${PYTHONPATH}"

# Verify
python -c "from shared.database.base import Base; print('✓ OK')"
```

### Database Connection Errors

Check that services are running:

```bash
# Check Docker services
docker-compose ps

# Check database connectivity
python -c "from db.session import SessionLocal; db = SessionLocal(); print('✓ Connected')"
```

### Migration Errors

```bash
# View migration status
cd response-network/api
alembic current
alembic history

# Downgrade if needed
alembic downgrade -1

# Then upgrade again
alembic upgrade head
```

### Duplicate User Errors

The seeding script automatically skips existing users:

```bash
# Safe to run multiple times
python manage_db.py seed --network response
# ℹ Admin user already exists, skipping...
```

## Advanced: Custom Initialization

### Add Custom Initialization Logic

In `response-network/api/main.py`, add startup event:

```python
from setup.initialization import initialize_database

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await initialize_database()
```

### Seed with Custom Logic

Create `response-network/api/setup/custom_seed.py`:

```python
from db.session import SessionLocal
from models.user import User
from core.hashing import get_password_hash
from uuid import uuid4

def seed_custom_data():
    db = SessionLocal()
    try:
        # Your custom seeding logic
        user = User(
            id=uuid4(),
            username="custom_user",
            email="custom@example.com",
            hashed_password=get_password_hash("password"),
            # ... other fields
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
```

Then call from `manage_db.py`:

```python
from setup.custom_seed import seed_custom_data

def seed(network):
    # ... existing code
    seed_custom_data()  # Add this
```

## Verification

### Verify Users Created

```bash
export PYTHONPATH="/workspaces/the_first:${PYTHONPATH}"

python -c "
from response-network.api.db.session import SessionLocal
from response-network.api.models.user import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f'✓ {user.username} ({user.email}) - Admin: {user.is_admin}')
db.close()
"
```

### Check API Endpoints

```bash
# Response Network API
curl -s http://localhost:8000/docs | head -20

# Request Network API
curl -s http://localhost:8001/docs | head -20

# Try login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin@123456"
```

## FAQ

**Q: Can I seed data after the application is running?**
A: Yes, run `python manage_db.py seed --network response` anytime.

**Q: Will seeding overwrite existing data?**
A: No, it skips existing users. Use `python manage_db.py drop-all` first if needed.

**Q: How do I add more test users?**
A: Edit the `sample_users` list in `manage_db.py` and reseed.

**Q: Should I seed in production?**
A: No, set `SEED_DATA=false` in production after initial setup.

**Q: How are Request Network users seeded?**
A: They're automatically imported from Response Network via import workers. No manual seeding needed.

**Q: Can I use different passwords?**
A: Yes, edit the seed functions or create a custom seeding script.

**Q: What if migrations fail?**
A: Check database connectivity and alembic configuration. See "Migration Errors" in troubleshooting.
