# Admin Panel Backend API - مستندات

**تاریخ**: 2025-11-25  
**نسخه**: 1.0  
**فاز**: 7 (Admin Panel Backend)

---

## 📋 خلاصه

Admin Panel Backend API برای **Response Network** مجموعه‌ای از endpoints است برای:
- 🔍 مانیتورینگ سیستم
- 📊 نمایش آمار و metrics
- 🔧 مدیریت کش و صف‌های Celery
- 👥 مدیریت کاربران
- 📈 پیگیری درخواست‌ها

---

## 🏗️ Architecture

```
Admin Panel Frontend (Next.js)
         ↓
Admin Panel Backend API (FastAPI)
         ↓
Database + Redis + Elasticsearch
```

---

## 🔐 Authentication

تمام endpoints admin-only هستند (به جز health check):
- **Header**: `Authorization: Bearer {jwt_token}`
- **Role**: فقط `admin` role

---

## 📡 API Endpoints

### 1. Health Check Endpoints

#### `GET /admin/health`
**وضعیت عمومی سیستم**

```bash
curl http://localhost:8000/admin/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-25T12:00:00",
  "services": {
    "database": "✅ online",
    "redis": "✅ online",
    "elasticsearch": "✅ online"
  }
}
```

---

#### `GET /admin/health/detailed`
**سلامت تفصیلی تمام services**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/health/detailed
```

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "database": {
    "status": "✅ online",
    "version": "PostgreSQL 14.0",
    "active_connections": 5
  },
  "redis": {
    "status": "✅ online",
    "used_memory": "256MB",
    "peak_memory": "512MB",
    "connected_clients": 10,
    "total_commands": 50000,
    "keyspace_hits": 45000,
    "keyspace_misses": 5000
  },
  "elasticsearch": {
    "status": "✅ online",
    "version": "8.0.0",
    "cluster_name": "response-network"
  }
}
```

---

### 2. System Statistics

#### `GET /admin/stats/system`
**آمار کلی سیستم**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/stats/system
```

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "users": {
    "total": 150,
    "active": 125
  },
  "requests": {
    "total": 10000,
    "processing": 25,
    "completed": 9500,
    "failed": 475
  },
  "results": {
    "total": 9500
  },
  "database": {
    "size": "2.5GB"
  }
}
```

---

### 3. Queue Monitoring

#### `GET /admin/stats/queues`
**آمار صف‌های Celery**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/stats/queues
```

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "queues": {
    "default": 50,
    "high": 10,
    "medium": 25,
    "low": 5
  },
  "total_pending": 90
}
```

---

### 4. Cache Management

#### `GET /admin/stats/cache`
**آمار کش Redis**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/stats/cache
```

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "status": "✅ connected",
  "memory": {
    "used": "256MB",
    "peak": "512MB",
    "max": "1GB",
    "fragmentation": 1.1
  },
  "performance": {
    "hits": 450000,
    "misses": 50000,
    "total_commands": 500000,
    "hit_ratio": "90.00%"
  },
  "keys": {
    "total": 25000
  },
  "clients": {
    "connected": 10
  }
}
```

---

#### `DELETE /admin/cache/clear`
**پاک کردن تمام کش**

```bash
curl -X DELETE -H "Authorization: Bearer {token}" http://localhost:8000/admin/cache/clear
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-11-25T12:00:00",
  "cleared": 25000,
  "message": "Cache cleared: 25000 keys removed"
}
```

---

#### `POST /admin/cache/optimize`
**بهینه‌سازی کش**

```bash
curl -X POST -H "Authorization: Bearer {token}" http://localhost:8000/admin/cache/optimize
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-11-25T12:00:00",
  "actions": [
    "Background save initiated"
  ],
  "memory_before": "256MB"
}
```

---

### 5. User Management

#### `GET /admin/users/list`
**لیست تمام کاربران**

```bash
curl -H "Authorization: Bearer {token}" "http://localhost:8000/admin/users/list?skip=0&limit=100"
```

**Parameters:**
- `skip`: تعداد پرش
- `limit`: تعداد نتایج (max 100)

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 100,
  "users": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe",
      "email": "john@example.com",
      "is_active": true,
      "created_at": "2025-11-20T10:00:00"
    },
    ...
  ]
}
```

---

#### `GET /admin/users/{user_id}`
**جزئیات کاربر**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/users/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2025-11-20T10:00:00",
  "statistics": {
    "total_requests": 500
  }
}
```

---

### 6. Request Monitoring

#### `GET /admin/requests/recent`
**آخرین درخواست‌ها**

```bash
curl -H "Authorization: Bearer {token}" "http://localhost:8000/admin/requests/recent?limit=20"
```

**Parameters:**
- `limit`: تعداد درخواست‌ها (default 20)

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "count": 20,
  "requests": [
    {
      "id": "req123",
      "user_id": "user456",
      "status": "completed",
      "created_at": "2025-11-25T11:59:00",
      "completed_at": "2025-11-25T11:59:30"
    },
    ...
  ]
}
```

---

#### `GET /admin/requests/stats`
**آمار درخواست‌ها**

```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/admin/requests/stats
```

**Response:**
```json
{
  "timestamp": "2025-11-25T12:00:00",
  "total": 10000,
  "by_status": {
    "pending": 50,
    "processing": 25,
    "completed": 9500,
    "failed": 425
  },
  "percentages": {
    "pending": "0.5%",
    "processing": "0.2%",
    "completed": "95.0%",
    "failed": "4.2%"
  }
}
```

---

## 🔄 Real-Time Updates

### Server-Sent Events (SSE)

برای real-time updates، از SSE استفاده می‌کنیم:

```javascript
const eventSource = new EventSource('/admin/stream/stats');

eventSource.onmessage = (event) => {
  const stats = JSON.parse(event.data);
  console.log('Updated stats:', stats);
};

eventSource.onerror = () => {
  console.error('Connection error');
};
```

---

## 💻 Client Integration Examples

### Python

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8000"
TOKEN = "your_jwt_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Health check
health = requests.get(f"{API_URL}/admin/health", headers=headers).json()
print(f"System status: {health['status']}")

# System stats
stats = requests.get(f"{API_URL}/admin/stats/system", headers=headers).json()
print(f"Total users: {stats['users']['total']}")
print(f"Completed requests: {stats['requests']['completed']}")

# Cache stats
cache = requests.get(f"{API_URL}/admin/stats/cache", headers=headers).json()
print(f"Cache hit ratio: {cache['performance']['hit_ratio']}")

# List users
users = requests.get(f"{API_URL}/admin/users/list?limit=10", headers=headers).json()
for user in users['users']:
    print(f"  - {user['username']}: {user['email']}")

# Request stats
req_stats = requests.get(f"{API_URL}/admin/requests/stats", headers=headers).json()
print(f"Processing: {req_stats['by_status']['processing']}")
print(f"Failed: {req_stats['by_status']['failed']}")
```

---

### JavaScript/TypeScript

```typescript
interface AdminStats {
  users: { total: number; active: number };
  requests: { total: number; processing: number; completed: number; failed: number };
  database: { size: string };
}

async function getSystemStats(token: string): Promise<AdminStats> {
  const response = await fetch('/admin/stats/system', {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

async function getCacheStats(token: string) {
  const response = await fetch('/admin/stats/cache', {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  return response.json();
}

// استفاده
const stats = await getSystemStats(token);
console.log(`Users: ${stats.users.total}`);
console.log(`Pending: ${stats.requests.processing}`);
```

---

## 🛠️ Admin Dashboard Features

### Dashboard Home
- ✅ System health overview
- ✅ Key metrics (users, requests, cache)
- ✅ Recent activity
- ✅ Alerts and warnings

### System Monitoring
- ✅ Service status (Database, Redis, Elasticsearch)
- ✅ Resource usage (Memory, CPU, Disk)
- ✅ Queue depth
- ✅ Cache performance

### User Management
- ✅ User list with search/filter
- ✅ User details and statistics
- ✅ Activate/Deactivate users
- ✅ User activity logs

### Request Monitoring
- ✅ Request status breakdown
- ✅ Recent requests
- ✅ Request details
- ✅ Failed request analysis

### Cache Management
- ✅ Cache hit ratio
- ✅ Memory usage
- ✅ Clear cache (emergency)
- ✅ Cache optimization

---

## 📊 Metrics Dashboards

### 1. System Dashboard
```
┌─────────────────────────────┐
│ System Status: ✅ OK         │
├─────────────────────────────┤
│ Users:    150 (125 active)  │
│ Requests: 10,000 total      │
│ - Processing: 25            │
│ - Completed: 9,500          │
│ - Failed: 475               │
│ Database Size: 2.5GB        │
└─────────────────────────────┘
```

### 2. Performance Dashboard
```
┌─────────────────────────────┐
│ Cache Hit Ratio: 90%        │
│ Avg Response Time: 45ms     │
│ Queue Depth: 90 tasks       │
│ Memory Usage: 256MB / 1GB   │
└─────────────────────────────┘
```

### 3. User Activity Dashboard
```
┌──────────────────────────────────┐
│ Active Users (24h): 95           │
│ New Users (24h): 12              │
│ Requests per User: 66 avg        │
│ Failed Queries: 2.1%             │
└──────────────────────────────────┘
```

---

## 🔒 Security Considerations

1. **Admin-Only Access**: تمام endpoints به JWT admin token نیاز دارند
2. **Rate Limiting**: Admin endpoints محدود نشده‌اند
3. **Audit Logging**: تمام admin actions لاگ می‌شوند
4. **HTTPS**: Production میں HTTPS الزامی است

---

## ⚠️ Error Handling

### Common Errors

| Code | Message | Solution |
|------|---------|----------|
| 401 | Unauthorized | JWT token اضافه کنید |
| 403 | Forbidden | Admin role الزامی است |
| 500 | Server Error | لاگ‌های server بررسی کنید |
| 503 | Service Unavailable | Service down است |

---

## 🚀 Best Practices

1. **مانیتورینگ منظم**
   ```python
   # هر 5 دقیقه چک کنید
   GET /admin/health/detailed
   ```

2. **Alert Thresholds**
   - Queue > 500: ⚠️ Warning
   - Cache hit ratio < 70%: ⚠️ Warning
   - Failed requests > 5%: 🔴 Alert

3. **Cache Management**
   - Weekly optimization
   - Monthly deep analysis
   - Clear only if necessary

4. **User Monitoring**
   - Track new signups
   - Monitor inactive users
   - Identify power users

---

## 📈 Monitoring Strategy

### Short-term (Real-time)
- Queue depth
- Active connections
- Recent errors

### Medium-term (Hourly)
- Cache hit ratio
- Request success rate
- Response times

### Long-term (Daily)
- User growth
- System capacity
- Trend analysis

---

## 🔧 Configuration

تمام endpoints از `.env` تنظیمات استفاده می‌کنند:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/response_db

# Redis
REDIS_URL=redis://localhost:6379

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Admin API
ADMIN_API_PORT=8000
ADMIN_API_HOST=0.0.0.0
```

---

## 📞 Support

برای مشکلات:

1. بررسی کنید که تمام services online هستند
   ```bash
   GET /admin/health/detailed
   ```

2. Admin token درست است
   ```bash
   curl -H "Authorization: Bearer {token}" /admin/health
   ```

3. لاگ‌های server:
   ```bash
   tail -f /var/log/response-network.log
   ```

---

**نسخه**: 1.0  
**آخرین به‌روزرسانی**: 2025-11-25  
**فاز**: 7 (Complete ✅)
