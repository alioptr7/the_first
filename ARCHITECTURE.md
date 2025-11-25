# معماری سیستم ایزوله درخواست/پاسخ (Air-Gapped Request/Response System)

## 📋 خلاصه پروژه

یک سیستم ایزوله (Air-Gapped) برای مدیریت درخواست‌ها و پاسخ‌ها که در دو شبکه جداگانه عمل می‌کند:
- **شبکه درخواست (Request Network)**: دریافت و مدیریت درخواست‌ها
- **شبکه پاسخ (Response Network)**: پردازش درخواست‌ها و ارائه پاسخ
- انتقال داده از طریق فایل به صورت دستی

## 🎯 اهداف و محدودیت‌های سیستم

### الزامات عملکردی
- پشتیبانی از حداکثر **200 درخواست در دقیقه** (3.3 req/sec)
- مدیریت کاربران با پروفایل‌های مختلف
- Rate limiting بر اساس پروفایل کاربر
- نظارت و مدیریت از طریق پنل ادمین
- اجرای Query روی Elasticsearch در شبکه ایزوله
- امنیت کامل در انتقال داده بین دو شبکه

### الزامات غیرعملکردی
- Scalability: قابلیت افزایش تا 1000 req/min در آینده
- Reliability: حداقل 99.5% uptime
- Observability: لاگ کامل و monitoring
- Maintainability: کد تمیز، مستند و testable

---

## 🔐 Admin User و User Sync Mechanism

### ⭐ Critical Architecture Decision

**Admin users ONLY exist in Response Network!**

- ✅ Admin User: Created in **Response Network** (Master)
- ✅ User Replica: Synced to **Request Network** automatically
- ❌ NO direct user creation in Request Network
- ❌ NO password changes in Request Network

### 🔄 User Sync Process

```
┌──────────────────────────────────────────────────────────────┐
│  Response Network (Master/Source of Truth)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Admin User Created:                                    │  │
│  │ - create_admin_user.py (one-time setup)               │  │
│  │ - Models: User with is_admin=True, profile_type=admin │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Celery Task: Every   │
            │ 5 minutes            │
            │ export_users_to_     │
            │ request_network()    │
            │                      │
            │ Location: workers/   │
            │ tasks/users_         │
            │ exporter.py          │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Export File:         │
            │ /exports/users/      │
            │ latest.json          │
            │                      │
            │ Contains:            │
            │ - All users          │
            │ - Hashed passwords   │
            │ - Profile types      │
            │ - Permissions        │
            └──────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │  MANUAL FILE TRANSFER        │
        │  (USB / Secure Copy)         │
        │  to imports/users/latest.json│
        └──────────────┼──────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Request Network (Read-only Replica)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Celery Task: Every 1 minute                           │  │
│  │ import_users_from_response_network()                  │  │
│  │                                                        │  │
│  │ Location: workers/tasks/users_importer.py             │  │
│  │                                                        │  │
│  │ Process:                                              │  │
│  │ 1. Check /imports/users/latest.json                   │  │
│  │ 2. Calculate checksum (SHA-256)                       │  │
│  │ 3. Compare with previous checksum                     │  │
│  │ 4. If changed: import/update all users                │  │
│  │ 5. Save new checksum for next cycle                   │  │
│  │                                                        │  │
│  │ Result: Users are synced WITHOUT passwords being     │  │
│  │ exposed during import!                                │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 🔑 Setup Steps

**Setup Order is CRITICAL:**

1. **Response Network MUST be setup first**
   ```bash
   # In response-network/api/
   python -m alembic upgrade head
   python create_admin_user.py  # Creates admin user in DB
   ```

2. **Start Response Network Celery Workers**
   ```bash
   # Start workers to enable user export
   python -m celery -A workers.celery_app worker
   python -m celery -A workers.celery_app beat
   ```

3. **Request Network Setup**
   ```bash
   # In request-network/api/
   python -m alembic upgrade head
   python init_setup.py  # Creates import directories
   ```

4. **Start Request Network Celery Workers**
   ```bash
   # Starts automatic user import from Response Network
   python -m celery -A workers.celery_app worker
   python -m celery -A workers.celery_app beat
   ```

### 📁 Directory Structure

```
# Response Network (Master)
response-network/api/
├── models/user.py              # Primary user model with all fields
├── workers/tasks/
│   ├── users_exporter.py        # EXPORT users to file (every 5 min)
│   ├── settings_exporter.py     # EXPORT settings
│   └── profile_types_exporter.py
├── exports/
│   ├── users/
│   │   ├── latest.json          # Current user export
│   │   ├── users_YYYYMMDD_*.json
│   │   └── last_export_meta.json
│   ├── settings/
│   └── profile_types/

# Request Network (Replica)
request-network/api/
├── models/user.py              # Read-only user replica
├── workers/tasks/
│   ├── users_importer.py        # IMPORT users (every 1 min)
│   ├── settings_importer.py
│   └── profile_types_importer.py
├── imports/
│   ├── users/
│   │   ├── latest.json          # Latest import file
│   │   └── .processed_users     # Checksum tracking
│   ├── settings/
│   └── profile_types/
├── exports/
│   └── requests/               # Requests for Response Network
```

---

## 🏗️ معماری کلی سیستم

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REQUEST NETWORK                              │
│                                                                     │
│  ┌──────────────┐         ┌──────────────┐                        │
│  │   Next.js    │────────→│   FastAPI    │                        │
│  │ Admin Panel  │         │   REST API   │                        │
│  └──────────────┘         └──────┬───────┘                        │
│                                   │                                 │
│                          ┌────────▼────────┐                       │
│                          │  Redis Cache &  │                       │
│                          │   Queue (Port   │                       │
│                          │     6379)       │                       │
│                          └────────┬────────┘                       │
│                                   │                                 │
│                    ┌──────────────┼──────────────┐                │
│                    ▼              ▼              ▼                 │
│            ┌─────────────┐  ┌──────────┐  ┌──────────┐           │
│            │ PostgreSQL  │  │  Celery  │  │  Celery  │           │
│            │  Database   │  │  Worker  │  │  Beat    │           │
│            │  (Port      │  │  (Export)│  │(Scheduler)│          │
│            │   5432)     │  └────┬─────┘  └──────────┘           │
│            └─────────────┘       │                                 │
│                                   ▼                                 │
│                          ┌────────────────┐                        │
│                          │  Export Files  │                        │
│                          │  /export/      │                        │
│                          │  (JSONL)       │                        │
│                          └────────┬───────┘                        │
└───────────────────────────────────┼────────────────────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  MANUAL FILE TRANSFER │
                        │  (USB / Secure Copy)  │
                        └───────────┬───────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────┐
│                        RESPONSE NETWORK                             │
│                                                                     │
│                          ┌────────────────┐                        │
│                          │  Import Files  │                        │
│                          │  /import/      │                        │
│                          └────────┬───────┘                        │
│                                   ▼                                 │
│                          ┌────────────────┐                        │
│                          │  Celery Worker │                        │
│                          │  (Import +     │                        │
│                          │   Process)     │                        │
│                          └────────┬───────┘                        │
│                                   │                                 │
│                    ┌──────────────┼──────────────┐                │
│                    ▼              ▼              ▼                 │
│            ┌─────────────┐  ┌──────────┐  ┌──────────────┐       │
│            │ PostgreSQL  │  │  Redis   │  │Elasticsearch │       │
│            │  Database   │  │  Cache   │  │   Cluster    │       │
│            │             │  │          │  │  (Port 9200) │       │
│            └─────────────┘  └──────────┘  └──────┬───────┘       │
│                                                    │                │
│                          ┌─────────────────────────┘               │
│                          ▼                                          │
│                    ┌──────────────┐                                │
│                    │ Query Worker │                                │
│                    │ (Elasticsearch                                │
│                    │   Executor)  │                                │
│                    └──────┬───────┘                                │
│                           │                                         │
│                           ▼                                         │
│                    ┌──────────────┐                                │
│                    │Export Worker │                                │
│                    │  (Results)   │                                │
│                    └──────┬───────┘                                │
│                           ▼                                         │
│                    ┌──────────────┐                                │
│                    │ Export Files │                                │
│                    │  /export/    │                                │
│                    └──────┬───────┘                                │
│                           │                                         │
│  ┌──────────────┐         │         ┌──────────────┐              │
│  │   Next.js    │─────────┴────────→│   FastAPI    │              │
│  │ Admin Panel  │                   │  Monitoring  │              │
│  │              │                   │     API      │              │
│  └──────────────┘                   └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ طراحی دیتابیس

### Request Network Database Schema

```sql
-- Users Table (Read-only replica, synced from Response Network)
CREATE TABLE users (
    id UUID PRIMARY KEY, -- No default generation, synced from response network
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL, -- Synced for authentication
    full_name VARCHAR(255),
    profile_type VARCHAR(50) NOT NULL DEFAULT 'basic',
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 10,
    rate_limit_per_hour INTEGER NOT NULL DEFAULT 100,
    rate_limit_per_day INTEGER NOT NULL DEFAULT 500,
    priority INTEGER NOT NULL DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Requests Table
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_type VARCHAR(50) NOT NULL,
    query_params JSONB NOT NULL,
    elasticsearch_query JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exported_at TIMESTAMP WITH TIME ZONE,
    export_batch_id UUID,
    result_received_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB,
    
    CONSTRAINT check_status CHECK (status IN (
        'pending', 'queued', 'exported', 'processing', 
        'completed', 'failed', 'cancelled'
    )),
    CONSTRAINT check_retry CHECK (retry_count >= 0 AND retry_count <= 5)
);

CREATE INDEX idx_requests_user ON requests(user_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_requests_created ON requests(created_at DESC);
CREATE INDEX idx_requests_export ON requests(exported_at) WHERE exported_at IS NOT NULL;
CREATE INDEX idx_requests_batch ON requests(export_batch_id) WHERE export_batch_id IS NOT NULL;

-- Responses Table
CREATE TABLE responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    result_data JSONB,
    result_count INTEGER,
    execution_time_ms INTEGER,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    import_batch_id UUID,
    is_cached BOOLEAN DEFAULT FALSE,
    cache_key VARCHAR(255),
    metadata JSONB,
    
    CONSTRAINT fk_request UNIQUE(request_id)
);

CREATE INDEX idx_responses_request ON responses(request_id);
CREATE INDEX idx_responses_received ON responses(received_at DESC);
CREATE INDEX idx_responses_batch ON responses(import_batch_id) WHERE import_batch_id IS NOT NULL;
CREATE INDEX idx_responses_cache ON responses(cache_key) WHERE cache_key IS NOT NULL;

-- Export Batches Table
CREATE TABLE export_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    record_count INTEGER NOT NULL DEFAULT 0,
    checksum VARCHAR(64),
    encrypted BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    
    CONSTRAINT check_batch_type CHECK (batch_type IN ('requests', 'responses', 'system')),
    CONSTRAINT check_batch_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_batches_type ON export_batches(batch_type);
CREATE INDEX idx_batches_status ON export_batches(status);
CREATE INDEX idx_batches_created ON export_batches(created_at DESC);

-- Import Batches Table (for tracking received files)
CREATE TABLE import_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    record_count INTEGER NOT NULL DEFAULT 0,
    checksum VARCHAR(64),
    source_batch_id UUID,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    
    CONSTRAINT check_import_type CHECK (batch_type IN ('requests', 'responses', 'system')),
    CONSTRAINT check_import_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'duplicate'))
);

CREATE INDEX idx_import_batches_status ON import_batches(status);
CREATE INDEX idx_import_batches_created ON import_batches(created_at DESC);
CREATE INDEX idx_import_batches_checksum ON import_batches(checksum);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_status INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- API Keys Table (for service-to-service auth)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    prefix VARCHAR(20) NOT NULL,
    scopes JSONB,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_apikeys_user ON api_keys(user_id);
CREATE INDEX idx_apikeys_active ON api_keys(is_active);
CREATE INDEX idx_apikeys_expires ON api_keys(expires_at);
```

### Response Network Database Schema

```sql
-- Users Table (Primary source of truth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_type VARCHAR(50) NOT NULL DEFAULT 'basic',
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 10,
    rate_limit_per_hour INTEGER NOT NULL DEFAULT 100,
    rate_limit_per_day INTEGER NOT NULL DEFAULT 500,
    priority INTEGER NOT NULL DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_profile_type CHECK (profile_type IN ('basic', 'premium', 'enterprise', 'admin')),
    CONSTRAINT check_priority CHECK (priority >= 1 AND priority <= 10)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_profile ON users(profile_type);
CREATE INDEX idx_users_active ON users(is_active);

-- Incoming Requests Table (mirrored from Request Network)
CREATE TABLE incoming_requests (
    id UUID PRIMARY KEY,
    original_request_id UUID NOT NULL,
    user_id UUID NOT NULL,
    query_type VARCHAR(50) NOT NULL,
    query_params JSONB NOT NULL,
    elasticsearch_query JSONB,
    priority INTEGER NOT NULL DEFAULT 5,
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    import_batch_id UUID,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    assigned_worker VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB,
    
    CONSTRAINT check_status CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'retry'
    ))
);

CREATE INDEX idx_incoming_status ON incoming_requests(status);
CREATE INDEX idx_incoming_priority ON incoming_requests(priority DESC, imported_at ASC);
CREATE INDEX idx_incoming_batch ON incoming_requests(import_batch_id);
CREATE INDEX idx_incoming_original ON incoming_requests(original_request_id);

-- Query Results Table
CREATE TABLE query_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES incoming_requests(id) ON DELETE CASCADE,
    original_request_id UUID NOT NULL,
    result_data JSONB,
    result_count INTEGER,
    execution_time_ms INTEGER,
    elasticsearch_took_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exported_at TIMESTAMP WITH TIME ZONE,
    export_batch_id UUID,
    metadata JSONB,
    
    CONSTRAINT fk_incoming_request UNIQUE(request_id)
);

CREATE INDEX idx_results_request ON query_results(request_id);
CREATE INDEX idx_results_original ON query_results(original_request_id);
CREATE INDEX idx_results_executed ON query_results(executed_at DESC);
CREATE INDEX idx_results_export ON query_results(exported_at) WHERE exported_at IS NOT NULL;

-- Export Batches Table (same structure as Request Network)
CREATE TABLE export_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    record_count INTEGER NOT NULL DEFAULT 0,
    checksum VARCHAR(64),
    encrypted BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB
);

-- Import Batches Table
CREATE TABLE import_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    record_count INTEGER NOT NULL DEFAULT 0,
    checksum VARCHAR(64),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB
);

-- System Logs Table
CREATE TABLE system_logs (
    id BIGSERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    error_trace TEXT,
    request_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_component ON system_logs(component);
CREATE INDEX idx_logs_created ON system_logs(created_at DESC);
CREATE INDEX idx_logs_request ON system_logs(request_id) WHERE request_id IS NOT NULL;
```

---

## 🔐 امنیت و رمزنگاری

### 1. Authentication & Authorization

**Request Network API:**
- JWT Tokens (HS256) با expiry 1 ساعت
- Refresh Token (expiry 7 روز) برای تمدید session
- API Keys برای service-to-service
- Role-Based Access Control (RBAC)

**Roles:**
- `user`: دسترسی به API برای ارسال درخواست
- `admin`: دسترسی کامل به پنل ادمین
- `operator`: مشاهده و مانیتورینگ
- `system`: برای service-to-service calls

### 2. Rate Limiting Strategy

```python
# Redis-based Sliding Window
Key Pattern: rate_limit:{user_id}:{window}
Windows: minute, hour, day

# Algorithm: Token Bucket
- Each profile has different limits
- Distributed rate limiting با Redis
- Graceful degradation (soft limits با warning)
```

### 4. Data Validation

- Input sanitization با Pydantic
- Query injection prevention
- File type و size validation
- Checksum verification (SHA-256)

---

## 📦 فرمت فایل‌های انتقالی

### JSONL Format (JSON Lines)

```jsonl
{"type":"request","id":"uuid","user_id":"uuid","query_params":{...},"priority":5,"timestamp":"ISO8601"}
{"type":"request","id":"uuid","user_id":"uuid","query_params":{...},"priority":8,"timestamp":"ISO8601"}
```

### File Naming Convention

```
requests_YYYYMMDD_HHmmss_<batch_id>.jsonl.enc
responses_YYYYMMDD_HHmmss_<batch_id>.jsonl.enc
```

### Metadata File (همراه هر batch)

```json
{
  "batch_id": "uuid",
  "batch_type": "requests",
  "created_at": "2024-01-15T10:30:00Z",
  "record_count": 150,
  "file_size": 524288,
  "checksum": "sha256_hash",
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_version": "v1"
  },
  "source_network": "request",
  "destination_network": "response"
}
```

---

## 🔄 Workflow و Job Scheduling

### User Sync Jobs (CRITICAL - Run First!)

#### 1. Response Network: Export Users (Every 5 minutes)
```python
Task: export_users_to_request_network()
Location: response-network/api/workers/tasks/users_exporter.py
Schedule: Every 5 minutes (Celery Beat)

Workflow:
1. Query all users from Response Network database
2. Include: id, username, email, hashed_password, is_active, profile_type
3. Generate JSON file: exports/users/latest.json
4. Create backup: exports/users/users_YYYYMMDD_HHMMSS.json
5. Update metadata: exports/users/last_export_meta.json
6. DELTA sync: Only exports users changed since last export

Output File: exports/users/latest.json
{
    "users": [
        {
            "id": "uuid",
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": "bcrypt_hash",
            "role": "admin",
            "is_active": true
        }
    ],
    "exported_at": "2024-01-15T10:30:00Z",
    "total_count": 5
}
```

#### 2. Request Network: Import Users (Every 1 minute)
```python
Task: import_users_from_response_network()
Location: request-network/api/workers/tasks/users_importer.py
Schedule: Every 1 minute (Celery Beat)

Workflow:
1. Check: imports/users/latest.json exists
2. Calculate SHA-256 checksum of file
3. Compare with previous checksum (.processed_users)
4. If changed:
   a. Load JSON file
   b. For each user: INSERT or UPDATE
   c. Preserve ID from Response Network (NO new ID generation)
   d. Update all fields: username, email, hashed_password, role, is_active
5. Save new checksum
6. Result: Request Network now has synced user data

IMPORTANT: Users are READ-ONLY in Request Network!
- Cannot modify user data in Request Network
- All user updates come from Response Network only (DELTA sync)
- Password verification uses synced hashed_password
- Only changed users are re-exported (not full dump every time)
```

#### 3. Manual File Transfer Process
```
STEP 1: File Export (Automatic in Response Network)
  Response Network → exports/users/latest.json
  (Every 5 minutes, includes ONLY changed users)
  
STEP 2: Manual Copy (Manual by Administrator)
  USB Drive or Secure Copy:
  exports/users/latest.json → /path/to/transfer/location

STEP 3: File Import (Automatic in Request Network)
  Copy to: request-network/api/imports/users/latest.json
  Celery Worker will detect within 1 minute
  (Checksum verified to avoid re-importing same data)

STEP 4: Sync Confirmation
  Check Response Network logs:
    - "Exported X users to: exports/users/latest.json"
  
  Check Request Network logs:
    - "Imported X users, Updated Y users"

STEP 5: Manual Trigger (On-demand)
  Admin can force exports via API:
  • POST /api/v1/admin/exports/users (Response Network)
  • Command: curl -X POST http://localhost:8000/api/v1/admin/exports/users
```

### Settings & Profile Types Sync Jobs

#### 4. Response Network: Export Settings (On Change)
```python
Task: export_settings_to_request_network()
Location: response-network/api/workers/tasks/settings_exporter.py

Workflow:
1. Export system settings
2. Export profile types configuration
3. Generate: exports/settings/latest.json
4. Generate: exports/profile_types/latest.json
```

#### 5. Request Network: Import Settings (Every 1 minute)
```python
Task: import_settings_from_response_network()
Location: request-network/api/workers/tasks/settings_importer.py

Workflow:
1. Check for new settings files
2. Import profile types configuration
3. Update rate limits, request types, etc.
```

### Request & Response Processing Jobs

#### 6. Request Network: Export Requests Job
```python
Task: export_requests_to_response_network()
Location: request-network/api/workers/tasks/export_requests.py
Schedule: Every 2 minutes
Priority: HIGH

Workflow:
1. Query pending requests (status='pending')
2. Order by: priority DESC, created_at ASC
3. Batch size: Maximum 500 records
4. Generate JSONL file: exports/requests/requests_YYYYMMDD_HHMMSS.jsonl
5. Create: exports/requests/latest.jsonl
6. Encrypt file (optional)
7. Calculate checksum (SHA-256)
8. Update requests status to 'exported'

Output: request-network/api/exports/requests/latest.jsonl
```

#### 7. Response Network: Import Requests Job
```python
Task: import_requests_from_request_network()
Location: response-network/api/workers/tasks/import_requests.py
Schedule: Every 30 seconds (polling)
Priority: HIGH

Workflow:
1. Scan imports/requests/ directory for files
2. Validate file format & checksum (SHA-256)
3. Decrypt file (if encrypted)
4. Parse JSONL
5. Check for duplicates (by request_id)
6. Insert into incoming_requests table
7. Push to Redis queue by priority
8. Archive processed file

Input: response-network/api/imports/requests/latest.jsonl
```

#### 8. Response Network: Query Executor Job
```python
Task: execute_elasticsearch_query()
Location: response-network/api/workers/tasks/query_executor.py
Schedule: Continuous (Celery worker pool)
Workers: 4-8 parallel workers
Priority: HIGH

Workflow:
1. Pop request from Redis queue (sorted by priority)
2. Check cache (Redis) with TTL 300 seconds
3. If cache miss:
   a. Build Elasticsearch query from request params
   b. Execute query against Elasticsearch
   c. Store result in query_results table
   d. Update cache with TTL
4. Update incoming_requests status to 'completed'
5. Handle errors & retry with exponential backoff
```

#### 9. Response Network: Export Results Job
```python
Task: export_results_to_request_network()
Location: response-network/api/workers/tasks/export_results.py
Schedule: Every 2 minutes
Priority: HIGH

Workflow:
1. Query completed results (exported_at IS NULL)
2. Batch size: 500 records
3. Generate JSONL file: exports/results/results_YYYYMMDD_HHMMSS.jsonl
4. Create: exports/results/latest.jsonl
5. Encrypt file (optional)
6. Calculate checksum (SHA-256)
7. Update exported_at timestamp

Output: response-network/api/exports/results/latest.jsonl
```

#### 10. Request Network: Import Results Job
```python
Task: import_results_from_response_network()
Location: request-network/api/workers/tasks/results_importer.py
Schedule: Every 30 seconds (polling)
Priority: HIGH

Workflow:
1. Scan imports/results/ directory for files
2. Validate file format & checksum (SHA-256)
3. Decrypt file (if encrypted)
4. Parse JSONL
5. Insert into responses table
6. Update requests status to 'completed'
7. Cache results in Redis (TTL: 7 days)
8. Archive processed file

Input: request-network/api/imports/results/latest.jsonl
```

### Maintenance Jobs

#### 11. Cleanup Job (Both Networks)
```python
Schedule: Daily at 02:00 UTC
Priority: LOW

Tasks:
- Archive old requests/responses (>30 days)
- Delete old export files (>7 days)
- Clean up Redis expired keys
- Vacuum PostgreSQL
- Rotate logs
```

---

## 📊 Complete Data Flow Diagram

```
REQUEST NETWORK                          RESPONSE NETWORK
(User-facing)                            (Processing)

┌────────────────────────┐              ┌────────────────────────┐
│  Users Submit Request  │              │    Admin Creates Users │
│  via REST API          │              │    (create_admin_user) │
└───────────┬────────────┘              └───────────┬────────────┘
            │                                       │
            ▼                                       ▼
    ┌──────────────────┐           ┌──────────────────────────┐
    │ Request Queue    │           │ Response Network Users   │
    │ (status=pending) │           │ (is_admin=true)          │
    └────────┬─────────┘           └──────────┬───────────────┘
             │                                 │
        [Every 2 min]                    [Every 5 min - DELTA]
             │                                 │
             ▼                                 ▼
    ┌──────────────────────────────────────────────────┐
    │  export_requests_to_response_network()           │
    │  Location: request-network/workers/tasks/        │
    │  Output: exports/requests/latest.jsonl           │
    └─────────────────┬──────────────────────────────────┘
                      │
             ┌────────┴──────────┐
             │ MANUAL COPY (USB) │
             └────────┬──────────┘
                      │
                      ▼
    ┌──────────────────────────────────────────────────┐
    │ response-network/api/imports/requests/           │
    │ latest.jsonl                                     │
    └─────────────────┬──────────────────────────────────┘
                      │
                 [Every 30s]
                      │
                      ▼
    ┌──────────────────────────────────────────────────┐
    │  import_requests_from_request_network()          │
    │  Location: response-network/workers/tasks/       │
    │  Inserts → incoming_requests table               │
    │  Pushes → Redis queue (by priority)              │
    └────────────┬─────────────────────────────────────┘
                 │
             [Continuous]
                 │
                 ▼
    ┌──────────────────────────────────────────────────┐
    │  execute_elasticsearch_query()                   │
    │  Workers: 4-8 parallel                           │
    │  Queries Elasticsearch                           │
    │  Stores → query_results table                    │
    │  Updates → Redis cache (TTL: 300s)              │
    └────────────┬─────────────────────────────────────┘
                 │
            [Every 2 min]
                 │
                 ▼
    ┌──────────────────────────────────────────────────┐
    │  export_results_to_request_network()             │
    │  Location: response-network/workers/tasks/       │
    │  Output: exports/results/latest.jsonl            │
    └─────────────────┬──────────────────────────────────┘
                      │
             ┌────────┴──────────┐
             │ MANUAL COPY (USB) │
             └────────┬──────────┘
                      │
                      ▼
    ┌──────────────────────────────────────────────────┐
    │ request-network/api/imports/results/             │
    │ latest.jsonl                                     │
    └─────────────────┬──────────────────────────────────┘
                      │
                 [Every 30s]
                      │
                      ▼
    ┌──────────────────────────────────────────────────┐
    │  import_results_from_response_network()          │
    │  Location: request-network/workers/tasks/        │
    │  Inserts → responses table                       │
    │  Updates → requests.status = 'completed'         │
    └─────────────────┬──────────────────────────────────┘
                      │
                      ▼
    ┌──────────────────────────────────────────────────┐
    │  User gets results via GET /requests/{id}        │
    │  REST API returns completed response             │
    └──────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack Details

### Backend (Python)

```yaml
Core Framework:
  - FastAPI: 0.109.0
  - Pydantic: 2.5.0
  - Python: 3.11+

Database:
  - PostgreSQL: 15+
  - psycopg3: 3.1.0
  - SQLAlchemy: 2.0+
  - Alembic: 1.13.0 (migrations)

Cache & Queue:
  - Redis: 7.2+
  - redis-py: 5.0.0
  - Celery: 5.3.0
  - Flower: 2.0.0 (Celery monitoring)

Elasticsearch:
  - elasticsearch-py: 8.11.0
  - Elasticsearch: 8.x

Security:
  - cryptography: 41.0.0
  - python-jose[cryptography]: 3.3.0
  - passlib[bcrypt]: 1.7.4
  - python-multipart: 0.0.6

Utilities:
  - httpx: 0.26.0 (async HTTP client)
  - python-dotenv: 1.0.0
  - structlog: 23.3.0 (structured logging)
  - prometheus-client: 0.19.0

Development:
  - pytest: 7.4.0
  - pytest-asyncio: 0.21.0
  - pytest-cov: 4.1.0
  - black: 23.12.0 (formatter)
  - ruff: 0.1.0 (linter)
  - mypy: 1.7.0 (type checking)
```

### Frontend (Next.js)

```yaml
Core:
  - Next.js: 14.x (App Router)
  - React: 18.x
  - TypeScript: 5.x
  - Node.js: 20.x LTS

UI Framework:
  - Tailwind CSS: 3.4.0
  - shadcn/ui: latest
  - Radix UI: latest
  - Lucide Icons: latest

State Management:
  - Zustand: 4.x
  - TanStack Query (React Query): 5.x

Forms & Validation:
  - React Hook Form: 7.x
  - Zod: 3.x

Data Table:
  - TanStack Table: 8.x

Charts:
  - Recharts: 2.x
  - Chart.js: 4.x (alternative)

HTTP Client:
  - axios: 1.6.0

Authentication:
  - next-auth: 5.x (optional)

Development:
  - ESLint: 8.x
  - Prettier: 3.x
  - Husky: 8.x (git hooks)
```

### Infrastructure

```yaml
Containerization:
  - Docker: 24.x
  - Docker Compose: 2.x

Database:
  - PostgreSQL: 15-alpine
  - Redis: 7-alpine

Monitoring (Optional):
  - Prometheus: latest
  - Grafana: latest
  - Loki: latest (logs)

Reverse Proxy:
  - Nginx: 1.25-alpine
  - Traefik: 2.x (alternative)

OS:
  - Ubuntu Server: 22.04 LTS
  - Debian: 12 (alternative)
```

---

## 🔍 Elasticsearch Integration

### Query Builder

```python
# Supported Query Types
query_types = [
    "match",           # Full-text search
    "term",            # Exact match
    "range",           # Range queries
    "bool",            # Boolean combination
    "wildcard",        # Pattern matching
    "fuzzy",           # Fuzzy search
    "aggregation",     # Aggregations
    "multi_match",     # Multiple fields
]

# Query Template
{
    "index": "string",
    "query": {},
    "aggs": {},
    "size": "int (max: 1000)",
    "from": "int",
    "sort": [],
    "_source": []
}
```

### Security Considerations

- Read-only access به Elasticsearch
- Query timeout: 30 ثانیه
- Result size limit: 1000 documents
- Whitelist مجاز indices
- Query validation قبل از اجرا
- Rate limiting per user

### Caching Strategy

```python
# Cache Key Generation
cache_key = f"es:{index}:{hash(query)}:{size}:{from}"

# Cache TTL
- Hot queries: 15 minutes
- Normal queries: 5 minutes
- Aggregations: 30 minutes

# Cache Invalidation
- TTL-based expiration
- Manual invalidation via admin panel
```

---

## 📊 Monitoring & Observability

### Metrics (Prometheus)

```python
# Application Metrics
- request_duration_seconds (histogram)
- request_total (counter)
- request_errors_total (counter)
- active_users (gauge)
- celery_tasks_total (counter)
- celery_task_duration_seconds (histogram)
- elasticsearch_query_duration (histogram)
- cache_hit_ratio (gauge)
- export_batch_size (histogram)

# System Metrics
- cpu_usage_percent
- memory_usage_bytes
- disk_usage_bytes
- network_io_bytes
```

### Logging (Structured JSON)

```python
# Log Levels
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors که handle شدند
- CRITICAL: System failures

# Log Format
{
    "timestamp": "ISO8601",
    "level": "INFO",
    "component": "api.requests",
    "message": "Request created",
    "request_id": "uuid",
    "user_id": "uuid",
    "duration_ms": 123,
    "metadata": {}
}
```

### Health Checks

```python
# Endpoints
GET /health              # Basic liveness
GET /health/ready        # Readiness check
GET /health/detailed     # Detailed status

# Checks
- PostgreSQL connection
- Redis connection
- Elasticsearch connection (Response Network)
- Disk space
- Memory usage
- Active workers
```

---

## 🚀 Deployment Architecture

### Development Environment

```yaml
Services:
  - API: localhost:8000
  - Admin Panel: localhost:3000
  - PostgreSQL: localhost:5432
  - Redis: localhost:6379
  - Elasticsearch: localhost:9200
  - Flower (Celery UI): localhost:5555

Volumes:
  - ./data/postgres
  - ./data/redis
  - ./data/elasticsearch
  - ./export
  - ./import
  - ./logs
```

### Production Environment

```yaml
Request Network:
  Hardware:
    - CPU: 4 cores
    - RAM: 8GB
    - Disk: 100GB SSD
  
  Services:
    - API: 2 instances (load balanced)
    - Celery Workers: 4 workers
    - Celery Beat: 1 instance
    - Redis: 1 instance
    - PostgreSQL: 1 instance
    - Admin Panel: 1 instance
    - Nginx: Reverse proxy

Response Network:
  Hardware:
    - CPU: 8 cores
    - RAM: 16GB
    - Disk: 200GB SSD
  
  Services:
    - Celery Workers: 8 workers
    - Redis: 1 instance
    - PostgreSQL: 1 instance
    - Elasticsearch: 3-node cluster
    - Admin Panel: 1 instance
    - Nginx: Reverse proxy
```

### Network Configuration

```yaml
Request Network Firewall:
  Inbound:
    - 443/tcp (HTTPS API)
    - 80/tcp (HTTP redirect)
  
  Outbound:
    - Blocked (except updates)

Response Network Firewall:
  Inbound:
    - 443/tcp (Admin panel only)
  
  Outbound:
    - Elasticsearch cluster (internal)
    - Blocked external

File Transfer:
  - USB drive با encryption
  - یا secure isolated transfer station
```

---

## 🧪 Testing Strategy

### Unit Tests
- Coverage target: >80%
- Test frameworks: pytest, pytest-asyncio
- Mocking: pytest-mock
- API tests: httpx.AsyncClient

### Integration Tests
- Database transactions
- Redis operations
- Elasticsearch queries
- File encryption/decryption
- End-to-end workflows

### Performance Tests
- Load testing: Locust
- Target: 200 req/min sustained
- Spike test: 500 req/min for 1 minute
- Latency: p95 < 500ms, p99 < 1000ms

### Security Tests
- OWASP Top 10 checks
- SQL injection prevention
- XSS prevention
- Rate limiting validation
- Encryption verification

---

## 📝 Configuration Management

### Environment Variables

```bash
# Request Network
DATABASE_URL=postgresql://user:pass@localhost:5432/requests_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<strong-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
API_HOST=0.0.0.0
API_PORT=8000
EXPORT_DIR=/app/export
IMPORT_DIR=/app/import
ENCRYPTION_KEY=<base64-encoded-key>
LOG_LEVEL=INFO

# Response Network
DATABASE_URL=postgresql://user:pass@localhost:5432/responses_db
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=<password>
IMPORT_DIR=/app/import
EXPORT_DIR=/app/export
ENCRYPTION_KEY=<same-as-request-network>
WORKER_COUNT=8
QUERY_TIMEOUT=30
CACHE_TTL=300
LOG_LEVEL=INFO
```

---

## 🔄 Data Flow Diagram

### Request Submission Flow

```
User → FastAPI → Validation → Rate Check (Redis)
                                    ↓
                            PostgreSQL Insert
                                    ↓
                            Status: 'pending'
                                    ↓
                            Return request_id
```

### Export Flow (Request Network)

```
Celery Beat → Export Job
                  ↓
         Query pending requests
                  ↓
         Generate JSONL batch
                  ↓
         Encrypt with AES-256
                  ↓
         Calculate SHA-256
                  ↓
         Save to /export/
                  ↓
         Update status: 'exported'
```

### Import & Process Flow (Response Network)

```
File in /import/ → Import Job → Decrypt → Validate
                                              ↓
                                    Insert to incoming_requests
                                              ↓
                                    Push to Redis queue (priority)
                                              ↓
                                    Worker picks task
                                              ↓
                                    Check cache
                                       ↙     ↘
                               Cache hit    Cache miss
                                    ↓           ↓
                              Return data   Execute ES query
                                    ↓           ↓
                                    ↓      Store result
                                    ↓           ↓
                                    └───────────┘
                                          ↓
                                    Save to query_results
```

### Export Results Flow (Response Network)

```
Celery Beat → Export Job
                  ↓
         Query completed results
                  ↓
         Generate JSONL batch
                  ↓
         Encrypt file
                  ↓
         Save to /export/
                  ↓
         Update exported_at
```

### Import Results Flow (Request Network)

```
File in /import/ → Import Job → Decrypt → Parse
                                              ↓
                                    Insert to responses
                                              ↓
                                    Update request status: 'completed'
                                              ↓
                                    Cache result (Redis)
                                              ↓
                                    Trigger notification (optional)
```

---

## 📈 Scalability Considerations

### Horizontal Scaling

```yaml
API Layer:
  - Multiple FastAPI instances behind load balancer
  - Stateless design
  - Shared Redis for sessions

Workers:
  - Scale Celery workers based on queue length
  - Auto-scaling با Kubernetes (future)
  - Priority queues for different workloads

Database:
  - PostgreSQL read replicas (future)
  - Connection pooling (PgBouncer)
  - Partitioning large tables by date

Redis:
  - Redis Cluster for high availability (future)
  - Separate instances for cache vs. queue

Elasticsearch:
  - Multi-node cluster
  - Shard optimization
  - Index lifecycle management
```

### Vertical Scaling Limits

```
API: تا 16 cores / 32GB RAM
Workers: تا 32 cores / 64GB RAM
PostgreSQL: تا 32 cores / 128GB RAM
Redis: تا 8 cores / 64GB RAM
Elasticsearch: تا 32 cores / 128GB RAM
```

---

## 🎯 Success Metrics (KPIs)

```yaml
Performance:
  - API Response Time: p95 < 200ms
  - Query Execution Time: p95 < 500ms
  - End-to-End Latency: p95 < 5 minutes
  - Throughput: > 200 req/min sustained

Reliability:
  - Uptime: > 99.5%
  - Error Rate: < 0.1%
  - Data Loss: 0%

Efficiency:
  - Cache Hit Rate: > 60%
  - Resource Utilization: 60-80%
  - Export/Import Cycle: < 5 minutes
```

---

## 🚨 CRITICAL SETUP MISTAKES TO AVOID

### ❌ Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| **Creating user in Request Network** | Users should ONLY be created in Response Network | Always create users in Response Network first |
| **Not starting Celery workers** | Import/export tasks won't run | Start both Worker and Beat in both networks |
| **Starting Request Network before Response Network** | No users to import, sync will fail | ALWAYS setup Response Network first |
| **Skipping admin user creation** | No way to login to Response Network | Run `python create_admin_user.py` after migrations |
| **Wrong database selected** | Data corruption, sync failures | Check DB_HOST, DB_PORT, DB_NAME in .env |
| **Not copying files between networks** | Users won't sync to Request Network | Manually copy exports/users/latest.json to imports/users/ |
| **Multiple admin users** | Security risk, confusion | Only one admin user per Response Network |
| **Changing user passwords in Request Network** | Changes will be overwritten on next sync | All password changes MUST be in Response Network |
| **Docker services not healthy** | Connections fail, tasks error out | Check `docker-compose ps` and `docker-compose logs` |
| **Port conflicts** | Services can't start | Change ports in docker-compose.yml or .env |

### ✅ Correct Setup Order (MANDATORY)

```
STEP 1: Docker Setup
  └─ docker-compose up -d
  └─ Wait for all services healthy
  └─ Check: docker-compose ps

STEP 2: Response Network (MUST BE FIRST)
  ├─ cd response-network/api
  ├─ python -m alembic upgrade head
  ├─ python create_admin_user.py         ⭐ Creates admin user
  └─ Start services:
     ├─ python -m uvicorn main:app --port 8000
     ├─ python -m celery -A workers.celery_app worker
     └─ python -m celery -A workers.celery_app beat

STEP 3: Manual User Export (Automatic via Celery)
  ├─ Wait 5 minutes for export_users_to_request_network() task
  ├─ Check: response-network/api/exports/users/latest.json exists
  └─ File contains all admin and users

STEP 4: Manual File Copy
  ├─ Copy: response-network/api/exports/users/latest.json
  └─ To: request-network/api/imports/users/latest.json

STEP 5: Request Network (AFTER Response Network works)
  ├─ cd request-network/api
  ├─ python -m alembic upgrade head
  ├─ python init_setup.py
  └─ Start services:
     ├─ python -m uvicorn main:app --port 8001
     ├─ python -m celery -A workers.celery_app worker
     └─ python -m celery -A workers.celery_app beat

STEP 6: Verify User Sync
  ├─ Wait 1 minute for import_users_from_response_network() task
  ├─ Check Request Network logs: "Imported X users, Updated Y users"
  └─ Verify login works with admin credentials
```

### 📊 Expected Behavior After Correct Setup

```
Timeline:
─────────

T+0 min:
  ✓ Response Network running
  ✓ Admin user created in DB
  ✓ Celery workers started

T+5 min:
  ✓ export_users_to_request_network() runs
  ✓ File created: response-network/api/exports/users/latest.json
  ✓ Celery log: "✓ Admin user exported"

T+5 min - Manual:
  ✓ Administrator copies file to Request Network

T+6 min:
  ✓ Request Network running
  ✓ Celery workers started

T+7 min:
  ✓ import_users_from_response_network() runs
  ✓ Celery log: "✓ Imported 1 users, Updated 0 users"
  ✓ Admin user now in Request Network database

T+7 min+:
  ✓ Request Network API accessible
  ✓ Admin login works
  ✓ Rate limiting active
  ✓ Ready for request submissions
```

---

## 🔐 Security Checklist

- [ ] AES-256 encryption برای فایل‌ها
- [ ] SHA-256 checksums برای integrity
- [ ] JWT authentication با secure secret
- [ ] Rate limiting در همه endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Input validation با Pydantic
- [ ] CORS configuration
- [ ] HTTPS/TLS در production
- [ ] Secrets management (environment variables)
- [ ] Regular security updates
- [ ] Audit logging کامل
- [ ] Role-based access control
- [ ] API key rotation policy
- [ ] Database encryption at rest (optional)
- [ ] Network isolation (air-gap)

---

## 📚 Documentation Requirements

```yaml
Code Documentation:
  - Docstrings for all functions/classes
  - Type hints (Python typing)
  - API documentation (OpenAPI/Swagger)
  - Database schema diagrams

Operational Documentation:
  - Deployment guide
  - Configuration guide
  - Troubleshooting guide
  - Backup/restore procedures
  - Disaster recovery plan

User Documentation:
  - API usage guide
  - Admin panel manual
  - Rate limiting guide
  - Query syntax examples
```

---

## 🛣️ Future Enhancements (Roadmap)

### Phase 1 (MVP) - Month 1-2
- [x] Basic architecture design
- [ ] Core API implementation
- [ ] Database setup
- [ ] Basic admin panel
- [ ] File encryption/decryption
- [ ] Celery jobs

### Phase 2 (Production Ready) - Month 3
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Comprehensive testing
- [ ] Monitoring & logging
- [ ] Docker deployment
- [ ] Documentation

### Phase 3 (Optimization) - Month 4-5
- [ ] Caching optimization
- [ ] Performance tuning
- [ ] Advanced admin features
- [ ] Query builder UI
- [ ] Alerts & notifications
- [ ] Backup automation

### Phase 4 (Advanced Features) - Month 6+
- [ ] Query templates
- [ ] Scheduled queries
- [ ] Data export features
- [ ] Advanced analytics
- [ ] Multi-tenancy support
- [ ] Kubernetes deployment
- [ ] High availability setup

---

## 🤝 Development Workflow

```yaml
Git Branching:
  - main: Production-ready code
  - develop: Integration branch
  - feature/*: Feature branches
  - hotfix/*: Critical fixes

Commit Convention:
  - feat: New feature
  - fix: Bug fix
  - docs: Documentation
  - style: Formatting
  - refactor: Code restructuring
  - test: Tests
  - chore: Maintenance

Code Review:
  - Required for all PRs
  - Automated checks (linting, tests)
  - At least 1 approval
```

---

## 📞 Support & Maintenance

```yaml
Backup Schedule:
  - Database: Daily full + hourly incremental
  - Redis: Daily snapshot
  - Elasticsearch: Daily snapshot
  - Files: Continuous sync
  - Retention: 30 days

Log Rotation:
  - Application logs: Daily, keep 14 days
  - Access logs: Weekly, keep 30 days
  - Audit logs: Monthly, keep 1 year

Monitoring Alerts:
  - High error rate (> 1%)
  - High latency (> 1s)
  - Disk space (> 80%)
  - Memory usage (> 90%)
  - Queue backlog (> 1000)
  - Failed exports/imports
```

---

## ✅ Pre-Deployment Checklist

```yaml
Infrastructure:
  - [ ] Servers provisioned
  - [ ] Network configured
  - [ ] Firewalls configured
  - [ ] SSL certificates installed
  - [ ] DNS configured

Application:
  - [ ] Environment variables set
  - [ ] Database migrations run (Response Network first!)
  - [ ] Redis configured
  - [ ] Elasticsearch indexed
  - [ ] Encryption keys generated
  - [ ] Admin user created (Response Network)

User Sync Setup:
  - [ ] Response Network: Celery workers running
  - [ ] Response Network: Admin user created with create_admin_user.py
  - [ ] Response Network: export_users_to_request_network() task scheduled
  - [ ] Verify: response-network/api/exports/users/latest.json created
  - [ ] Manual: Copy users file to Request Network imports directory
  - [ ] Request Network: Celery workers running
  - [ ] Request Network: import_users_from_response_network() task scheduled
  - [ ] Verify: Users successfully imported into Request Network
  - [ ] Test: Admin login works in both networks

Security:
  - [ ] Security scan completed
  - [ ] Penetration test done
  - [ ] Secrets rotated
  - [ ] Backups tested
  - [ ] Disaster recovery tested
  - [ ] Air-gap network isolation verified

Documentation:
  - [ ] API docs published
  - [ ] Admin manual complete
  - [ ] Runbooks ready
  - [ ] Setup guide (SETUP_GUIDE.md) reviewed
  - [ ] Contact list updated
```

---

## 📋 Glossary

- **Air-Gap**: فیزیکی یا logical isolation بین دو شبکه
- **JSONL**: JSON Lines - هر خط یک JSON object
- **JWT**: JSON Web Token - برای authentication
- **Rate Limiting**: محدود کردن تعداد درخواست در بازه زمانی
- **Celery**: Distributed task queue برای Python
- **Beat**: Celery scheduler برای تاسک‌های تکراری
- **Redis**: In-memory data store برای caching و queuing
- **Batch**: مجموعه‌ای از درخواست‌ها یا پاسخ‌ها که با هم منتقل می‌شوند
- **Export**: فرآیند تبدیل داده به فایل برای انتقال
- **Import**: فرآیند خواندن فایل و ذخیره در database
- **Worker**: Process که task ها را از queue می‌خواند و اجرا می‌کند
- **Response Network**: شبکه اصلی (Master) - منبع حقیقت داده‌ها
- **Request Network**: شبکه دوم (Replica) - فقط خواندن کاربران
- **Delta Sync**: تنها تغییرات از آخرین sync منتقل می‌شوند (نه همه داده)
- **Checksum**: SHA-256 hash برای تأیید عدم تغییر فایل
- **Master/Slave**: Response Network = Master, Request Network = Slave
- **Source of Truth**: Response Network تنها منبع اطلاعات صحیح است

---

**تاریخ آخرین به‌روزرسانی:** 2025-11-23  
**نسخه معماری:** 2.0  
**وضعیت:** Comprehensive with Admin Setup Guidelines  
**نویسندگان:** Architecture Team  
**مسئول:** DevOps & Backend Team