# 🚀 راه‌اندازی Response Network - دستور دقیق

## ✅ چه چیزها نیاز دارید:

1. ✅ Docker Services (PostgreSQL, Redis, Elasticsearch)
2. ✅ FastAPI Server
3. ✅ Celery Worker (اجراکننده تسک‌ها)
4. ✅ Celery Beat (برنامه‌ریز)

---

## 📋 مرحله به مرحله:

### **مرحله 1: Docker Services**

```powershell
# Terminal 1
docker-compose -f docker-compose.dev.yml --profile response up -d

# بررسی
docker ps -f label=project.group=response-network
```

**نتیجه انتظار:**
```
STATUS: Up (healthy)
- postgres-response-db (5433)
- redis-response (6380)
- elasticsearch (9200)
```

---

### **مرحله 2: FastAPI Server**

```powershell
# Terminal 2
cd c:\Users\win\the_first\response-network\api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# آدرس: http://127.0.0.1:8000/docs
```

**انتظار:**
```
INFO:     Application startup complete
Uvicorn running on http://127.0.0.1:8000
```

---

### **مرحله 3: Celery Beat (برنامه‌ریز)**

```powershell
# Terminal 3
cd c:\Users\win\the_first\response-network\api
celery -A workers.celery_app beat --loglevel=info

# انتظار
[... INFO/MainProcess] beat: Starting...
```

**وظیفه:**
```
هر 60 ثانیه: export_settings را برنامه‌ریز می‌کند
هر 120 ثانیه: export_results را برنامه‌ریز می‌کند
...
```

---

### **مرحله 4: Celery Worker (اجراکننده)**

```powershell
# Terminal 4
cd c:\Users\win\the_first\response-network\api
celery -A workers.celery_app worker --loglevel=info --concurrency=4

# انتظار
[... INFO/MainProcess] celery@pc ready.
[... INFO/MainProcess] Connected to redis://localhost:6380/0
```

**وظیفه:**
```
Task‌های درخواست شده را اجرا می‌کند
```

---

## 📊 هر 4 Terminal:

```
Terminal 1: docker-compose up                      ← Docker
Terminal 2: uvicorn main:app                       ← FastAPI (Port 8000)
Terminal 3: celery beat                            ← Celery Scheduler
Terminal 4: celery worker                          ← Celery Processor
```

---

## 🧪 تست:

### **تست 1: API در دسترس است؟**

```bash
curl http://127.0.0.1:8000/docs
# نتیجه: Swagger UI باز می‌شود ✅
```

### **تست 2: Beat فعال است؟**

```bash
# در Terminal 3 بابین:
[2025-11-12 XX:XX:XX] Scheduler: Sending due task 
    export_settings_to_request_network
```

### **تست 3: Worker اجرا می‌کند؟**

```bash
# در Terminal 4 ببینید:
[2025-11-12 XX:XX:XX] INFO Task workers.tasks.settings_exporter
    .export_settings_to_request_network started
[2025-11-12 XX:XX:05] INFO Task completed successfully
```

### **تست 4: Manual Task درخواست کنید**

```bash
# در Swagger:
POST /api/v1/settings/export/now

# نتیجه:
{
  "message": "درخواست اکسپورت به صف اضافه شد",
  "task_id": "abc123...",
  "status": "pending"
}

# سپس Task Status را ببینید:
GET /api/v1/settings/export/status/abc123...
```

---

## 🆘 اگر مشکل پیش آمد:

### **خطا: "Cannot connect to redis"**
```
✅ بررسی: docker ps | grep redis
✅ شروع: docker-compose up -d redis-response
```

### **خطا: "beat: ConnectionRefusedError"**
```
✅ بررسی: Redis فعال است؟
✅ بررسی: پورت 6380 درست است؟
```

### **خطا: "Worker not consuming tasks"**
```
✅ بررسی: Worker به Redis متصل است؟
✅ بررسی: Beat task‌ها میفرستد؟
✅ بررسی: celery status
   celery -A workers.celery_app inspect active
```

---

## 📝 خلاصه دستورات:

```powershell
# تمام مرحله‌ها:

# 1️⃣ Docker
docker-compose -f docker-compose.dev.yml --profile response up -d

# 2️⃣ FastAPI
cd c:\Users\win\the_first\response-network\api; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 3️⃣ Beat
cd c:\Users\win\the_first\response-network\api; celery -A workers.celery_app beat --loglevel=info

# 4️⃣ Worker
cd c:\Users\win\the_first\response-network\api; celery -A workers.celery_app worker --loglevel=info --concurrency=4
```

---

## ✅ نشانه‌های صحیح کار:

| مورد | نشانه صحیح |
|------|-----------|
| **Docker** | `docker ps` → 3 service up |
| **FastAPI** | `http://127.0.0.1:8000/docs` → Swagger باز می‌شود |
| **Beat** | `Scheduler: Sending due task...` در log |
| **Worker** | `celery@pc ready` در log |

---

## 🎯 نتیجه نهایی:

```
✅ تسک‌های Scheduled خودکار اجرا می‌شوند
✅ API درخواست‌های Manual دریافت می‌کند
✅ تمام نظارت در Swagger دیده می‌شود
✅ داده‌ها در database ذخیره می‌شوند
```

