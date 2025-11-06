---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary

This is a multi-project air-gapped request/response system for managing distributed requests and responses across isolated networks. The system consists of two main network services: Request Network (handles request management) and Response Network (handles response processing), with a shared infrastructure and Next.js admin panel for monitoring and administration.

## Repository Structure

The repository is organized into distinct project components:

- **request-network/**: Python FastAPI service managing request submission, validation, and export workflows
- **response-network/**: Python FastAPI service handling response imports, processing, and result queries
- **response-network/admin-panel/**: Next.js TypeScript admin panel for system monitoring and management
- **shared/**: Shared Python utilities for authentication, database configuration, and data models
- **core/**: Core configuration and middleware modules
- **tests/**: Integration and unit tests for shared modules

### Main Repository Components

- **Request Network API**: FastAPI REST API for request lifecycle management with Celery export workers
- **Response Network API**: FastAPI REST API for response processing with Celery import workers and Redis caching
- **Admin Panel**: Next.js application providing web UI for system administration and monitoring
- **Message Queue**: Celery workers with Redis for asynchronous task processing
- **Database Layer**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Shared Services**: Authentication, database connectivity, logging, and schema definitions

## Projects

### Request Network API
**Configuration File**: equest-network/api/requirements.txt, equest-network/api/main.py

#### Language & Runtime
**Language**: Python
**Version**: Python 3.11+
**Build System**: pip/setuptools
**Package Manager**: pip
**Async Framework**: FastAPI with uvicorn

#### Dependencies
**Main Dependencies**:
- fastapi==0.109.2 - Web framework
- sqlalchemy==2.0.27 - ORM
- psycopg[binary]==3.1.18 - PostgreSQL driver
- asyncpg==0.30.0 - Async PostgreSQL driver
- alembic==1.13.1 - Database migrations
- celery - Task queue system
- redis - Caching and message broker
- pydantic==2.12.1 - Data validation
- python-jose==3.5.0 - JWT authentication
- cryptography==46.0.3 - Encryption
- bcrypt==5.0.0 - Password hashing
- python-dotenv==1.0.1 - Environment config

**Development Dependencies**:
- pytest==8.4.2 - Testing framework
- pytest-asyncio==0.21.1 - Async test support
- httpx==0.28.1 - Async HTTP client
- pytest-cov==4.1.0 - Coverage reporting

#### Build & Installation
`ash
cd request-network/api
pip install -r requirements.txt
pip install -r ../requirements-test.txt
`

#### Testing
**Framework**: pytest with async support
**Test Location**: equest-network/tests/
**Naming Convention**: 	est_*.py files
**Configuration**: equest-network/tests/conftest.py with async fixtures
**Run Command**:
`ash
pytest request-network/tests/
pytest --cov=request-network/api request-network/tests/
`

#### Database
**Migrations**: Alembic in equest-network/alembic/
**Init Command**:
`ash
alembic upgrade head
`

### Response Network API
**Configuration File**: esponse-network/api/requirements.txt, esponse-network/api/main.py

#### Language & Runtime
**Language**: Python
**Version**: Python 3.11+
**Build System**: pip/setuptools
**Package Manager**: pip
**Async Framework**: FastAPI with uvicorn

#### Dependencies
**Main Dependencies**:
- fastapi==0.109.2 - Web framework
- sqlalchemy==2.0.27 - ORM
- asyncpg==0.30.0 - Async PostgreSQL driver
- alembic==1.13.1 - Database migrations
- redis - Cache and queue
- celery - Async tasks
- pydantic==2.12.1 - Data validation
- elasticsearch - Search and indexing
- python-jose==3.5.0 - JWT tokens
- cryptography==46.0.3 - File encryption
- uvicorn==0.27.1 - ASGI server

#### Build & Installation
`ash
cd response-network/api
pip install -r requirements.txt
`

#### Database
**Migrations**: Alembic configured for response database

### Response Network Admin Panel
**Configuration File**: esponse-network/admin-panel/package.json, esponse-network/admin-panel/tsconfig.json

#### Language & Runtime
**Language**: TypeScript/JavaScript (Next.js)
**Version**: Next.js v14+
**Package Manager**: npm
**Runtime**: Node.js

#### Dependencies
**Main Dependencies**:
- next - React framework
- react - UI library
- axios - HTTP client
- @tanstack/react-query - State management
- @hookform/resolvers - Form validation
- @radix-ui - UI components
- lucide-react - Icons

#### Build & Installation
`ash
cd response-network/admin-panel
npm install
npm run build
npm run dev
`

#### Development
**Dev Server**:
`ash
npm run dev
`
**Linting**:
`ash
npm run lint
`

## Docker Configuration

**Docker Compose**: docker-compose.dev.yml (development setup)

### Services Configured
- **postgres-request**: PostgreSQL 15 (Request Network database)
- **postgres-response**: PostgreSQL 15 (Response Network database)
- **redis-request**: Redis (Request Network cache/queue)
- **redis-response**: Redis (Response Network cache/queue)
- **elasticsearch**: Elasticsearch cluster (Response Network search)
- **request-api**: FastAPI application (Request Network)
- **request-worker**: Celery worker (Request Network exports)
- **response-api**: FastAPI application (Response Network)
- **response-worker**: Celery worker (Response Network imports)
- **response-beat**: Celery Beat scheduler

### Build & Run
`ash
docker-compose -f docker-compose.dev.yml --profile all up -d
docker-compose -f docker-compose.dev.yml --profile request up -d
docker-compose -f docker-compose.dev.yml --profile response up -d
`

## Shared Modules

### shared/
**Key Modules**:
- shared/auth/security.py - Authentication utilities
- shared/database/ - Database configuration
- shared/models.py - Data models
- shared/schemas.py - Pydantic schemas
- shared/logger.py - Logging configuration

## Main Entry Points

**Request Network API**: equest-network/api/main.py
**Response Network API**: esponse-network/api/main.py
**Admin Panel**: esponse-network/admin-panel/app/page.tsx

## Configuration Files

- config.py - Root configuration
- schemas.py - Data schemas
- security.py - Security settings
- .env files for environment-specific configuration
- lembic.ini - Database migration config

## Development Workflow

**Test Execution**: equest-network/scripts/run_tests.ps1
**Database Setup**: Alembic migrations with seed data
**Export/Import**: JSONL file format with encryption
**Monitoring**: Redis queues and Elasticsearch indexing

## Key Technologies

- **API**: FastAPI, Starlette, Uvicorn
- **ORM**: SQLAlchemy with async support
- **Database**: PostgreSQL 15+
- **Caching**: Redis
- **Search**: Elasticsearch
- **Tasks**: Celery with Redis broker
- **Auth**: JWT with Python-Jose
- **Frontend**: Next.js, React, TypeScript
- **Validation**: Pydantic
- **Encryption**: cryptography library
- **Testing**: pytest with async support
