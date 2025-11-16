# 📋 فرایند کامل Celery + Unicorn + Redis

## 🎯 خلاصه
سیستم از **3 کامپوننت اصلی** تشکیل شده:
1. **Unicorn API** - وب سرور (Fastapi)
2. **Celery Beat** - برنامه‌ریز (زمان‌بندی)
3. **Celery Worker** - اجراگر (پردازش‌گر)

تمام ارتباطات از طریق **Redis** انجام می‌شود.

---

## 🚀 مراحل شروع (در Windows)

### 1️⃣ Redis شروع شود
```bash
# اگر Docker نیست
redis-server --port 6380
```

### 2️⃣ Unicorn API شروع شود
```bash
# در Terminal 1
cd response-network/api
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Output:
# INFO:     Started server process [1234]
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3️⃣ Celery Beat شروع شود
```bash
# در Terminal 2
cd response-network/api
python -m celery -A workers.celery_app beat --loglevel=info

# Output:
# celery beat v5.3.0 (sun)
# [*] Scheduler: celery.beat.PersistentScheduler
# [*] Synchronizing schedule
# [*] Schedule entry 'export-settings-every-minute': export_settings_to_request_network 60.00s
```

### 4️⃣ Celery Worker شروع شود
```bash
# در Terminal 3
cd response-network/api
python -m celery -A workers.celery_app worker --pool=solo --loglevel=info

# Output:
# celery@DESKTOP-XXXX ready. [*] celery@DESKTOP-XXXX ready. [*] ...
# [*] pool: solo
# [*] concurrency: 1
```

---

## 📍 معماری فیزیکی

```
┌─────────────────────────────────────────────────────────┐
│                                                           │
│  Windows Machine (127.0.0.1)                            │
│                                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │  Unicorn API   │  │ Celery Beat    │  │  Worker   │ │
│  │  :8000         │  │  (Scheduler)   │  │ (Executor)│ │
│  │                │  │                │  │           │ │
│  │ FastAPI        │  │ Timer-based    │  │ Process   │ │
│  │                │  │                │  │ Tasks     │ │
│  └────────────────┘  └────────────────┘  └───────────┘ │
│        ▲                   │                     ▲       │
│        │                   │                     │       │
│        └───────────────────┼─────────────────────┘       │
│                            │ (Queue / Commands)          │
│        ┌──────────────────────────────────────────┐     │
│        │      Redis (localhost:6380)              │     │
│        │                                          │     │
│        │  Queue: celery                          │     │
│        │  ├─ Task 1: export_settings             │     │
│        │  ├─ Task 2: export_users                │     │
│        │  └─ Task 3: settings_importer           │     │
│        │                                          │     │
│        │  Backend: Result Storage                 │     │
│        │  ├─ task_id_1: "success"                │     │
│        │  └─ task_id_2: "failed"                 │     │
│        └──────────────────────────────────────────┘     │
│                                                           │
│  File System:                                           │
│  └─ response-network/exports/                          │
│     ├─ settings/settings_latest.json                   │
│     ├─ users/users_queue.json                          │
│     └─ password_changes/password_changes_queue.json    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 فرایند کامل (مثال: export_settings)

### 📝 مرحله 1: تعریف Task
**فایل:** `response-network/api/workers/tasks/settings_exporter.py`

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def export_settings_to_request_network(self):
    """
    ایجاد فایل settings_latest.json و settings_queue.json
    """
    # 1. اتصال به Database
    db = next(get_db_sync())
    
    # 2. دریافت تمام settings
    settings = db.query(SettingsModel).all()
    
    # 3. ذخیره فایل
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_PATH / "settings_latest.json", "w") as f:
        json.dump([...], f)
    
    # 4. نتیجه برگردان
    return {"status": "success", "count": len(settings)}
```

**کلید مهم:** `@shared_task` = Celery میتواند این تابع را صف‌بندی کند

---

### ⏰ مرحله 2: برنامه‌زمانی (Beat)
**فایل:** `response-network/api/workers/celery_app.py`

```python
celery_app.conf.beat_schedule = {
    "export-settings-every-minute": {
        "task": "workers.tasks.settings_exporter.export_settings_to_request_network",
        "schedule": 60.0,  # هر 60 ثانیه
    },
}
```

**معنی:**
- **Task:** نام تسک کامل (مسیر ماژول + نام تابع)
- **Schedule:** هر چند ثانیه

---

### ⏱️ مرحله 3: Beat منتظر است

**زمان: 14:30:00**

Beat در حال نظارت است:
```
Beat Scheduler (Running...)
├─ Current Time: 14:30:00
├─ Next Task (export-settings): 14:30:00  👈 TIME MATCHED!
└─ Check schedule every second...
```

---

### 📤 مرحله 4: Task به صف اضافه شود

**زمان: 14:30:00 (دقیقاً)**

Beat عمل می‌کند:

```python
# Beat internally does:
task = export_settings_to_request_network.delay()  # یا apply_async()
```

**نتیجه: Redis Queue تغییر می‌کند:**

```
Redis Before:
┌──────────────────┐
│ celery (queue)   │
│                  │
│ (خالی)           │
└──────────────────┘

Redis After:
┌──────────────────────────────────────┐
│ celery (queue)                        │
│                                      │
│ Message 1:                           │
│ {                                    │
│   "id": "abc123def456",             │
│   "task": "workers.tasks...",       │
│   "args": [],                       │
│   "kwargs": {},                     │
│   "retries": 0,                     │
│   "eta": null                       │
│ }                                    │
└──────────────────────────────────────┘
```

**Log در Beat:**
```
[2025-11-13 14:30:00,000: INFO/MainProcess] Scheduler: Sending due task export-settings-every-minute
[2025-11-13 14:30:00,010: DEBUG/MainProcess] Task sent: export_settings_to_request_network[abc123def456]
```

---

### 👷 مرحله 5: Worker task را می‌گیرد

**زمان: 14:30:00.5 (بلافاصله بعد)**

Worker مسلسل Redis را بررسی می‌کند:

```python
# Worker internally does (in loop):
while True:
    message = redis_queue.pop()  # از سمت چپ صف می‌گیرد
    if message:
        task_id = message['id']
        task_name = message['task']
        
        # Run task
        result = execute_task(task_name, task_id)
        
        # Store result
        redis_backend.set(task_id, result)
```

**Worker Log:**
```
[2025-11-13 14:30:00,020: INFO/MainProcess] Received task: export_settings_to_request_network[abc123def456]
[2025-11-13 14:30:00,030: DEBUG/MainProcess] Task started, id=abc123def456
```

---

### ⚙️ مرحله 6: Task اجرا می‌شود

**زمان: 14:30:00.5 تا 14:30:02**

Worker کد تسک را اجرا می‌کند:

```python
# تسک اجرا می‌شود...

# Step 1: اتصال به Database
db = next(get_db_sync())  # 200ms

# Step 2: Query کردن Settings
settings = db.query(SettingsModel).all()  # 400ms (اگر 1000 record باشد)

# Step 3: ایجاد JSON
settings_data = [
    {
        "id": "uuid-1",
        "key": "app.title",
        "value": "My App",
        "created_at": "2025-11-13T14:30:00"
    },
    ...
]  # 50ms

# Step 4: ذخیره فایل
EXPORT_PATH.mkdir(parents=True, exist_ok=True)
export_file = EXPORT_PATH / "settings_latest.json"
with open(export_file, "w") as f:
    json.dump(settings_data, f)  # 100ms

# Step 5: Queue فایل
queue_file = EXPORT_PATH / "settings_queue.json"
if queue_file.exists():
    with open(queue_file, "r") as f:
        queue = json.load(f)
else:
    queue = []

queue.append({
    "timestamp": "2025-11-13T14:30:02",
    "file": "settings_latest.json"
})

with open(queue_file, "w") as f:
    json.dump(queue, f)  # 50ms

# Total: ~800ms
```

**Worker Log:**
```
[2025-11-13 14:30:00,050: DEBUG/solo] Executing task
[2025-11-13 14:30:00,250: INFO/solo] DB connected successfully
[2025-11-13 14:30:00,650: DEBUG/solo] Query completed: 1234 settings
[2025-11-13 14:30:00,750: DEBUG/solo] File written: /exports/settings_latest.json
[2025-11-13 14:30:00,850: INFO/solo] Task completed successfully
```

**فایل سیستم بروزرسانی می‌شود:**
```
response-network/exports/
├─ settings/
│  ├─ settings_latest.json           👈 نوشته شد
│  └─ settings_queue.json             👈 بروزرسانی شد
│
├─ users/
│  └─ users_latest.json
│
└─ password_changes/
   └─ password_changes_latest.json
```

---

### ✅ مرحله 7: نتیجه به Redis برگردد

**زمان: 14:30:02**

Worker نتیجه را ذخیره می‌کند:

```python
# Worker internally:
result = {
    "status": "success",
    "count": 1234,
    "file": "/exports/settings_latest.json",
    "exported_at": "2025-11-13T14:30:02"
}

# Store in Redis backend
redis_backend.set(
    f"celery-task-meta-abc123def456",
    json.dumps({
        "status": "SUCCESS",
        "result": result,
        "traceback": None
    }),
    ex=3600  # 1 ساعت
)
```

**Worker Log:**
```
[2025-11-13 14:30:02,100: INFO/solo] Task successful: export_settings_to_request_network[abc123def456]
[2025-11-13 14:30:02,110: DEBUG/solo] Result stored in backend
```

**Redis Backend:**
```
Before:
celery-task-meta-abc123def456: (not exists)

After:
celery-task-meta-abc123def456: {
  "status": "SUCCESS",
  "result": {"status": "success", "count": 1234, ...},
  "traceback": null
}
```

---

### 🔄 مرحله 8: تکرار (هر 60 ثانیه)

**زمان: 14:31:00**

Beat دوباره نظارت می‌کند:

```
Beat Scheduler (Running...)
├─ Current Time: 14:31:00
├─ Next Task (export-settings): 14:31:00  👈 TIME MATCHED AGAIN!
└─ Send to Queue again...
```

**Redis Queue:**
```
celery (queue)
├─ Message 1 (14:30:00): ✅ COMPLETED
├─ Message 2 (14:31:00): 📤 QUEUED
└─ Message 3 (14:32:00): ⏳ WAITING...
```

---

## 🌐 نقش Request Network

### در Request Network
```python
# request-network/workers/celery_app.py

celery_app.conf.beat_schedule = {
    "import-settings-and-passwords-every-minute": {
        "task": "workers.tasks.settings_importer.import_settings_and_passwords",
        "schedule": 60.0,
    },
}
```

**هر 60 ثانیه:**

1. ✅ `settings_importer` اجرا می‌شود
2. ✅ فایل‌ها را از `response-network/exports/` می‌خواند
3. ✅ Database Request Network را بروزرسانی می‌کند

```python
# Task Step by Step:

# 1. بررسی password_changes_queue.json
PASSWORD_CHANGES_PATH = "./exports/password_changes"
queue_file = PASSWORD_CHANGES_PATH / "password_changes_queue.json"

if queue_file.exists():
    # 2. فایل را بخوان
    with open(queue_file, "r") as f:
        password_changes = json.load(f)  # List of changes
    
    # 3. برای هر پسورد
    for change in password_changes:
        user = db.query(User).filter(User.id == change['user_id']).first()
        
        # 4. بروزرسانی
        user.hashed_password = change['hashed_password']
        user.synced_at = datetime.utcnow()
        db.add(user)
    
    # 5. Commit
    db.commit()
    
    # 6. حذف queue
    queue_file.unlink()
```

---

## 🔗 تعامل Unicorn + Celery + Redis

### یک کاربر "پسورد تغییر میدهد"

```
┌─────────────────────────────────────────────────────────────┐
│ کاربر (Browser)                                              │
└─────────────────────────────────────────────────────────────┘
         │ POST /users/{id}/reset-password
         │ {"new_password": "NewPass123"}
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Unicorn API (:8000)                                          │
│                                                              │
│ @router.post("/{user_id}/reset-password")                  │
│ async def reset_user_password(user_id, request_body, db):   │
│     # 1. Validate
│     user = await db.get(User, user_id)
│                                                              │
│     # 2. Hash password
│     hashed = get_password_hash(request_body["new_password"])│
│                                                              │
│     # 3. Update DB
│     user.hashed_password = hashed
│     await db.commit()
│                                                              │
│     # 4. 🎯 CALL CELERY TASK
│     from workers.tasks.password_sync import \              │
│         sync_password_to_request_network                    │
│     task = sync_password_to_request_network.delay(          │
│         user_id=str(user.id),                               │
│         hashed_password=hashed                              │
│     )                                                        │
│                                                              │
│     return {
│         "success": True,
│         "sync_task_id": task.id
│     }
└─────────────────────────────────────────────────────────────┘
         │ Queue message sent to Redis
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Redis (localhost:6380/0)                                     │
│                                                              │
│ celery (queue):                                             │
│ [                                                            │
│   {                                                          │
│     "id": "task_xyz789",                                    │
│     "task": "workers.tasks.password_sync...",              │
│     "args": [],                                             │
│     "kwargs": {                                             │
│       "user_id": "user-uuid-123",                          │
│       "hashed_password": "$2b$12$..."                      │
│     }                                                        │
│   }                                                          │
│ ]                                                            │
└─────────────────────────────────────────────────────────────┘
         │ Worker reads from queue
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Celery Worker (Process)                                      │
│                                                              │
│ def sync_password_to_request_network(user_id, hashed):      │
│                                                              │
│     # 1. Create export directory
│     EXPORT_PATH.mkdir(parents=True, exist_ok=True)          │
│                                                              │
│     # 2. Read queue file
│     queue_file = EXPORT_PATH / "password_changes_queue"     │
│     if queue_file.exists():
│         queue_data = json.load(queue_file)                  │
│     else:
│         queue_data = []
│                                                              │
│     # 3. Add password change
│     queue_data.append({
│         "user_id": user_id,
│         "hashed_password": hashed,
│         "changed_at": now()
│     })
│                                                              │
│     # 4. Write queue file
│     with open(queue_file, "w") as f:                        │
│         json.dump(queue_data, f)
│                                                              │
│     # 5. Return result
│     return {"status": "success"}
└─────────────────────────────────────────────────────────────┘
         │ Result stored in Redis backend
         ▼
┌─────────────────────────────────────────────────────────────┐
│ File System (exports/)                                       │
│                                                              │
│ response-network/exports/                                   │
│ └─ password_changes/                                        │
│    └─ password_changes_queue.json   👈 نوشته شد             │
│       [                                                      │
│         {                                                    │
│           "user_id": "user-uuid-123",                       │
│           "hashed_password": "$2b$12$...",                 │
│           "changed_at": "2025-11-13T14:30:00"              │
│         }                                                    │
│       ]                                                      │
└─────────────────────────────────────────────────────────────┘
         │ هر 60 ثانیه Request Network import می‌کند
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Request Network Worker (Beat + Worker)                       │
│                                                              │
│ def import_settings_and_passwords():                        │
│     queue_file = "./exports/password_changes_queue.json"    │
│     if queue_file.exists():
│         changes = json.load(queue_file)                     │
│         for change in changes:
│             user = db.get(User, change['user_id'])          │
│             user.hashed_password = change['hashed_password']│
│             user.synced_at = now()
│             db.add(user)
│         db.commit()
│         queue_file.unlink()  # حذف بعد از درآمد
└─────────────────────────────────────────────────────────────┘
         │ Request Network DB بروز شد
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Request Network Database                                     │
│                                                              │
│ users:                                                       │
│ ├─ id: user-uuid-123                                       │
│ ├─ username: john                                          │
│ ├─ hashed_password: "$2b$12$..." 👈 SYNCED                │
│ └─ synced_at: 2025-11-13T14:31:00                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Redis Data Structure

### Queue (messages waiting)
```
Key: celery
Type: List (FIFO)
├─ [0] = Task message 1
├─ [1] = Task message 2
└─ [2] = Task message 3

Commands:
- RPUSH celery <message>  # Add to queue
- LPOP celery             # Get from queue
- LLEN celery             # Queue length
```

### Backend (task results)
```
Key: celery-task-meta-<task_id>
Type: String (JSON)
Value: {
  "status": "SUCCESS" | "FAILURE" | "PENDING",
  "result": {...},
  "traceback": null
}

Commands:
- SET key value EX 3600  # Store result (1 hour)
- GET key                # Retrieve result
- DEL key                # Delete result
```

---

## 🔍 Monitoring Commands

### 1. بررسی Queue Length
```bash
redis-cli -p 6380
> LLEN celery
(integer) 5  # 5 tasks in queue

> LPOP celery  # Get first task
"{\"id\": \"abc123...\"}"
```

### 2. بررسی Active Workers
```bash
celery -A workers.celery_app inspect active

{
  "celery@DESKTOP-ABC123": {
    "active": [
      {
        "id": "abc123def456",
        "name": "workers.tasks.export_settings...",
        "args": [],
        "kwargs": {},
        "time_start": 1234567890.123
      }
    ]
  }
}
```

### 3. بررسی Task Result
```python
from workers.celery_app import celery_app

# اگر task_id داریم:
task = celery_app.AsyncResult("abc123def456")

print(task.state)     # PENDING, STARTED, SUCCESS, FAILURE
print(task.result)    # نتیجه (اگر complete است)
print(task.info)      # اطلاعات بیشتر
```

### 4. بررسی Beat Schedule
```bash
cd response-network/api
python debug_celery.py

# Output:
# ============================================================
# 🔍 Celery Configuration Debug
# ============================================================
# 
# 1️⃣ Broker & Backend:
#    Broker: redis://localhost:6380/0
#    Backend: redis://localhost:6380/1
# 
# 2️⃣ Beat Schedule:
#    ✅ export-settings-every-minute
#       Task: workers.tasks.settings_exporter.export_settings_to_request_network
#       Schedule: 60.0s
```

---

## ⏸️ مشکل عام: صف خالی نیست

```bash
# اگر صف پر است و tasks انجام نمی‌شوند:

# 1. بررسی کنید Worker فعال است:
celery -A workers.celery_app inspect active
# اگر نتیجه‌ای نیست → Worker خاموش است!

# 2. پاک کنید queue:
redis-cli -p 6380
> DEL celery
(integer) 5  # حذف شد 5 task

# 3. دوباره شروع کنید:
python -m celery -A workers.celery_app worker --pool=solo
```

---

## 🎯 خلاصه فرایند

```
🕐 Beat (ساعتی)
  └─> هر 60 ثانیه → send task to Redis Queue

📤 Redis Queue (صف)
  └─> Task message stored as JSON

👷 Worker (کارگر)
  └─> Get task from queue
      └─> Execute Python function
          └─> Write results to file
              └─> Store result in Redis Backend

✅ Success!
  └─> Task completed
      └─> File exported
          └─> Other network imported

🔄 Repeat every 60 seconds...
```

---

## 📁 فایل‌های کلیدی

| فایل | نقش |
|------|------|
| `response-network/api/workers/celery_app.py` | تعریف Celery app + Beat schedule |
| `response-network/api/workers/tasks/settings_exporter.py` | تسک export settings |
| `response-network/api/workers/tasks/password_sync.py` | تسک export password changes |
| `response-network/api/start_beat.py` | شروع Beat Scheduler |
| `request-network/workers/celery_app.py` | تعریف Celery worker (بدون Beat) |
| `request-network/workers/tasks/settings_importer.py` | تسک import تنظیمات و پسوردها |
| `response-network/exports/` | فایل‌های export (Queue files) |

---

## 🏗️ معماری نهایی

```
Response Network:
  Unicorn API (8000)
    ├─ POST /reset-password → calls celery task
    └─ DB sync

  Celery Beat (Scheduler)
    ├─ export_settings (هر 60s)
    ├─ export_users (هر 60s)
    └─ export_profile_types (هر 60s)

  Celery Worker (Executor)
    ├─ Receives tasks from Queue
    ├─ Executes and exports files
    └─ Stores results


          ↓ (File Export)

response-network/exports/ (Shared Files)
  ├─ settings_latest.json
  ├─ users_queue.json
  └─ password_changes_queue.json


          ↓ (File Import)

Request Network:
  Celery Beat (Scheduler)
    └─ import_settings_and_passwords (هر 60s)

  Celery Worker (Executor)
    ├─ Reads exported files
    ├─ Updates Request Network DB
    └─ Deletes queue files

  Unicorn API (8001)
    └─ Serves synced data
```

---

## ✨ نکات مهم

1. **Beat و Worker باید هر دو فعال باشند**
   - Beat بدون Worker = نمی‌تواند tasks اجرا شود
   - Worker بدون Beat = فقط manual tasks کار می‌کند

2. **Redis باید شغال باشد**
   - Broker: پیام‌های queue
   - Backend: نتایج

3. **Windows استفاده می‌کند `--pool=solo`**
   - تنها یک Worker process در Windows

4. **فایل‌ها در صف جمع می‌شوند**
   - هر 60 ثانیه یک file اضافه می‌شود
   - Request Network هر 60 ثانیه پردازش می‌کند

5. **Sync یک‌طرفه است**
   - Response → Request Network
   - نه برعکس

