# 🚀 Response Network - How to Run

## ⚡ Quick Start (All in One)

```bash
# در response-network/api directory
python quick_start.py
```

این خودکار می‌کند:
1. ✅ Redis queue را پاک می‌کند (حذف tasks معلق)
2. ✅ Beat Scheduler را شروع می‌کند
3. ✅ Worker را شروع می‌کند  
4. ✅ FastAPI را شروع می‌کند

---

## 📋 Manual Start (3 Terminal Tabs)

اگر می‌خواهید هر کدام را جداگانه شروع کنید:

### Terminal 1 - Beat Scheduler
```bash
cd c:\Users\win\the_first\response-network\api
python start_beat.py
```
**نتیجه:**
```
[02:22:00,981: INFO/MainProcess] Scheduler: Sending due task export-settings-every-minute
[02:23:00,993: INFO/MainProcess] Scheduler: Sending due task export-settings-every-minute
```

### Terminal 2 - Worker
```bash
cd c:\Users\win\the_first\response-network\api
python start_worker.py
```
**نتیجه:**
```
[02:29:01,020: INFO/MainProcess] Task ... received
[02:29:01,480: INFO/MainProcess] Task ... succeeded in 0.453s ✅
```

### Terminal 3 - FastAPI
```bash
cd c:\Users\win\the_first\response-network\api
python -m uvicorn main:app --reload
```
**نتیجه:**
```
Uvicorn running on http://127.0.0.1:8000
```

---

## 🧹 Clear Redis Queue

اگر tasks معلق دارید (قدیمی):

```bash
python -c "import redis; r = redis.from_url('redis://localhost:6380/0'); r.delete('celery'); print('✅ Queue cleared!')"
```

---

## 🔍 Monitor Task Execution

### Real-time Monitor
```bash
# در یک terminal جداگانه
celery -A workers.celery_app inspect active
```

### Check Active Workers
```bash
celery -A workers.celery_app inspect stats
```

### View Task Results
```bash
python -c "
import redis
r = redis.from_url('redis://localhost:6380/1')
for key in r.keys('*'):
    print(key, '=', r.get(key))
"
```

---

## 📊 Expected Output

### Beat (هر 60 ثانیه)
```
[02:22:00,981: INFO/MainProcess] Scheduler: Sending due task export-settings-every-minute
[02:22:00,985: DEBUG/MainProcess] bare_execute: <Task: workers.tasks.settings_exporter.export_settings_to_request_network (...)>
```

### Worker (دریافت و اجرا)
```
[02:29:01,020: INFO/MainProcess] Task workers.tasks.settings_exporter.export_settings_to_request_network received
[02:29:01,480: INFO/MainProcess] Task workers.tasks.settings_exporter.export_settings_to_request_network succeeded in 0.453s
```

### Export File Created
```
exports/settings/settings_20251112_102901.json
exports/settings/latest.json (symlink)
```

---

## ⚠️ Common Issues

### Problem: Worker doesn't see Beat messages
**Solution:** Clear Redis queue
```bash
python quick_start.py  # یا دستی clear کن
```

### Problem: `--pool=solo` needed on Windows
**Solution:** Already handled in `start_worker.py` ✅

### Problem: Redis not responding
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Problem: Import errors in tasks
**Solution:** Make sure `workers/tasks/__init__.py` exists

---

## 📈 Architecture Overview

```
┌─────────────────────────────────────────┐
│  Beat Scheduler (Every 60 seconds)      │
│  - Creates: export_settings message     │
└──────────┬──────────────────────────────┘
           │
           │ Message → Redis Queue
           ▼
┌─────────────────────────────────────────┐
│  Redis (Broker & Result Backend)        │
│  - localhost:6380/0 (tasks)             │
│  - localhost:6380/1 (results)           │
└──────────┬──────────────────────────────┘
           │
           │ Pickup: export_settings message
           ▼
┌─────────────────────────────────────────┐
│  Worker (--pool=solo on Windows)        │
│  - Executes: settings_exporter.py       │
│  - Creates: JSON export files           │
└─────────────────────────────────────────┘
```

---

## 🎯 What Each Does

| Component | Role | Command |
|-----------|------|---------|
| **Beat** | Scheduler - creates messages every 60s | `python start_beat.py` |
| **Worker** | Executor - runs tasks from queue | `python start_worker.py` |
| **FastAPI** | API Server - receives HTTP requests | `python -m uvicorn main:app --reload` |
| **Redis** | Message Broker - stores queue | Must be running (docker/external) |

