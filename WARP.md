# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## System Overview

This is an air-gapped request/response system designed for secure data processing. The system consists of two completely isolated networks:

- **Request Network**: Receives requests from end users, handles authentication, and manages the request queue
- **Response Network**: Processes requests by executing queries on Elasticsearch in a completely isolated environment

Data transfer between networks happens only through manual file transfers (USB/secure transfer).

## Core Architecture

### Two-Network Design
- **Request Network**: FastAPI + PostgreSQL + Redis + Next.js admin panel
- **Response Network**: Celery workers + Elasticsearch + PostgreSQL + Redis + monitoring API
- **File Transfer**: JSONL files with metadata, manually transferred between `/export/` and `/import/` directories
- **No Network Communication**: The two networks never communicate directly over network protocols

### Key Components
- **Databases**: Separate PostgreSQL instances for each network with different schemas
- **Message Queues**: Redis-based Celery queues for async processing
- **Search Engine**: Elasticsearch cluster (Response Network only)
- **Admin Panels**: Next.js applications for monitoring and management
- **File Processing**: Custom JSONL handlers with checksum verification

## Development Commands

### Environment Setup
```powershell
# Start all infrastructure services
docker-compose -f docker-compose.dev.yml --profile all up -d

# Start only Request Network services
docker-compose -f docker-compose.dev.yml --profile request up -d

# Start only Response Network services  
docker-compose -f docker-compose.dev.yml --profile response up -d
```

### Database Operations
```powershell
# Request Network - Run migrations
cd request-network/api
alembic upgrade head

# Response Network - Run migrations  
cd response-network/api
alembic upgrade head

# Create new migration (example for request network)
cd request-network/api
alembic revision --autogenerate -m "Description of changes"
```

### Running API Services
```powershell
# Request Network API (default: http://localhost:8000)
cd request-network/api
uvicorn main:app --reload

# Response Network Monitoring API (default: http://localhost:8001)
cd response-network/api  
uvicorn main:app --reload --port 8001
```

### Running Workers
```powershell
# Request Network Workers
cd request-network/workers
celery -A celery_app worker --loglevel=info

# Request Network Beat Scheduler
cd request-network/workers
celery -A celery_app beat --loglevel=info

# Response Network Workers
cd response-network/workers
celery -A celery_app worker --loglevel=info --concurrency=8

# Response Network Beat Scheduler
cd response-network/workers
celery -A celery_app beat --loglevel=info
```

### Running Frontend
```powershell
# Response Network Admin Panel (default: http://localhost:3000)
cd response-network/admin-panel
npm install
npm run dev
```

### Testing
```powershell
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=shared --cov-report=html

# Run specific test file
python -m pytest tests/shared/test_file_format_handler.py -v

# Set PYTHONPATH for running tests
$env:PYTHONPATH="C:\Users\win\the_first"
```

### Linting and Code Quality
```powershell
# Python - Format code
black .

# Python - Lint code  
ruff check .

# Python - Type checking
mypy shared/ request-network/api/ response-network/api/

# TypeScript - Lint (from admin panel directory)
cd response-network/admin-panel
npx eslint .
```

### Monitoring
```powershell
# View Celery task monitor (if Flower is running)
# Request Network: http://localhost:5555
# Response Network: http://localhost:5556

# Check Redis queues
redis-cli -p 6379 llen celery  # Request Network
redis-cli -p 6380 llen celery  # Response Network

# Monitor log files
tail -f logs/request-network.log
tail -f logs/response-network.log
```

## High-Level Architecture

### Request Flow
1. **User Request**: Client submits request via FastAPI → stored in PostgreSQL as `pending`
2. **Export Task**: Celery worker exports pending requests to `/export/` as encrypted JSONL
3. **Manual Transfer**: Files manually moved from Request Network `/export/` to Response Network `/import/`
4. **Import Task**: Response Network imports requests and queues them for processing
5. **Query Execution**: Workers execute Elasticsearch queries with Redis caching
6. **Result Export**: Completed results exported to Response Network `/export/`  
7. **Manual Return**: Result files manually moved back to Request Network `/import/`
8. **Import Results**: Request Network imports results and updates request status to `completed`

### Data Models
- **Users**: Master records in Response Network, read-only replicas in Request Network
- **Requests**: Created in Request Network, mirrored as `incoming_requests` in Response Network
- **Responses**: Results stored in both networks with different schemas
- **Batches**: Track file transfers with checksums and metadata

### Security Model
- **Authentication**: JWT tokens for API access, API keys for service-to-service
- **Rate Limiting**: Redis-based per-user limits based on profile types (basic/premium/enterprise)
- **File Integrity**: SHA-256 checksums for all transferred files
- **Network Isolation**: No direct network communication between the two networks
- **Input Validation**: Pydantic schemas for all API inputs and file formats

### File Transfer Protocol
- **Format**: JSONL (JSON Lines) with accompanying `.meta` files
- **Naming**: `{timestamp}_{batch_type}_{batch_id}.jsonl`
- **Validation**: Checksum verification and duplicate detection
- **Archiving**: Processed files moved to archive directories

### Background Jobs

#### Request Network
- **Export Requests** (every 2 minutes): Export pending requests to JSONL
- **Import Results** (every 30 seconds): Import completed results from files  
- **Cleanup** (daily): Archive old requests and clean up files

#### Response Network  
- **Import Requests** (every 30 seconds): Import request files and queue for processing
- **Query Executor** (continuous): Execute Elasticsearch queries with caching
- **Export Results** (every 2 minutes): Export completed results to files
- **Cache Maintenance** (hourly): Clean expired cache entries
- **System Health Check** (every 5 minutes): Monitor service health

### Configuration Management
- Environment-specific `.env` files for database URLs, Redis URLs, API keys
- Structured logging with configurable levels (DEV_LOGGING for development)
- Docker Compose profiles for running different network combinations
- Alembic for database schema migrations

### Key Directories
- `shared/`: Common utilities (logging, file handling, schemas)
- `request-network/`: Public-facing API and workers
- `response-network/`: Isolated processing environment  
- `tests/`: Unit and integration tests
- `export/` & `import/`: File transfer directories (created during setup)

### Development Patterns
- **FastAPI**: Modern async Python API framework with automatic OpenAPI docs
- **SQLAlchemy**: ORM with async support and relationship management
- **Celery**: Distributed task queue for background processing
- **Structured Logging**: JSON logging for production, human-readable for development
- **Type Safety**: Full type hints with mypy checking
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes

This system prioritizes security and data isolation above all else, making it suitable for environments where air-gapped operation is required for compliance or security reasons.