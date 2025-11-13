# Response Network Setup Guide

## 📁 دایرکتوری Setup

دایرکتوری `setup` برای **راه‌اندازی خودکار** سامانه است.

### فایل‌های موجود:

| فایل | توضیح |
|------|-------|
| **config_template.py** | الگو تنظیمات (Database, Redis, ES, Admin, etc.) |
| **init_setup.py** | اسکریپت راه‌اندازی جامع |
| **update_config.py** | بروزرسانی تنظیمات پویا |
| **cleanup_alembic.py** | تمیزکاری وضعیت Alembic |
| **setup_worker_settings.py** | تنظیمات Worker |

---

## 🚀 راه‌اندازی کامل

### **مرحله 1: اجرای اسکریپت راه‌اندازی**

```powershell
cd c:\Users\win\the_first\response-network\api
python setup\init_setup.py
```

این اسکریپت به ترتیب:
1. ✅ ایجاد/بروزرسانی `.env` فایل
2. ✅ اجرای مایگریشن‌های دیتابیس
3. ✅ ایجاد کاربر Admin
4. ✅ تنظیم Worker های پایه

---

### **مرحله 2: شروع Docker Services**

```powershell
docker-compose -f docker-compose.dev.yml --profile response up -d
```

سرویس‌های شروع شده:
- PostgreSQL (5433)
- Redis (6380)
- Elasticsearch (9200)

---

### **مرحله 3: شروع FastAPI Server**

```powershell
cd c:\Users\win\the_first\response-network\api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### **مرحله 4: شروع Celery Worker (اختیاری)**

```powershell
cd c:\Users\win\the_first\response-network\api
celery -A workers.celery_app worker --loglevel=info
```

---

## 🔧 تغییر تنظیمات

### **اگر آدرس Docker تغییر کند:**

```powershell
# نمایش تنظیمات فعلی
python setup\update_config.py --show

# بروزرسانی Redis
python setup\update_config.py --redis-host redis-server --redis-port 6380

# بروزرسانی Database
python setup\update_config.py --db-host postgres-server --db-port 5432

# بروزرسانی Elasticsearch
python setup\update_config.py --es-host elasticsearch --es-port 9200

# اعتبارسنجی تنظیمات
python setup\update_config.py --validate
```

---

## 📋 تنظیمات پیش‌فرض

### **Admin کاربر:**
- Username: `admin`
- Email: `admin@response-network.local`
- Password: `admin123`

### **Database:**
- Host: `localhost`
- Port: `5433`
- Database: `response_db`
- User: `user`
- Password: `password`

### **Redis:**
- Host: `localhost`
- Port: `6380`

### **Elasticsearch:**
- Host: `localhost`
- Port: `9200`

---

## ⚙️ سفارشی‌کردن `config_template.py`

برای تغییر تنظیمات پیش‌فرض، فایل `config_template.py` را ویرایش کنید:

```python
ADMIN_USER_CONFIG = {
    "username": "admin",
    "email": "admin@youromain.com",
    "password": "your_secure_password",
}

DATABASE_CONFIG = {
    "RESPONSE_DB_HOST": "your-db-host",
    ...
}
```

سپس دوباره `init_setup.py` را اجرا کنید.

---

## ✅ اعتبارسنجی

```powershell
# بررسی وضعیت سرویس‌ها
docker ps -f label=project.group=response-network

# تست API
curl http://127.0.0.1:8000/docs

# تست Database
docker exec postgres-response-db psql -U user -d response_db -c "SELECT 1"

# تست Redis
docker exec redis-response redis-cli ping

# تست Elasticsearch
curl http://localhost:9200
```

---

## 🐛 مشکلات رایج

### **"Port already in use"**
```powershell
# عوض کردن پورت در docker-compose.dev.yml یا:
docker-compose -f docker-compose.dev.yml down
```

### **"Connection refused to PostgreSQL"**
```powershell
# بررسی اگر database شروع شده
docker logs postgres-response-db

# یا اجرای setup دوباره بعد از PostgreSQL آماده شود
```

### **"Migration failed"**
```powershell
# تمیزکاری وضعیت Alembic
python setup/cleanup_alembic.py

# سپس دوباره setup
python setup/init_setup.py
```

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│  init_setup.py (راه‌اندازی)          │
├─────────────────────────────────────┤
│ 1. create_env_file()                │
│    └─ config_template.py            │
│ 2. run_migrations()                 │
│    └─ alembic upgrade head          │
│ 3. create_admin_user()              │
│    └─ INSERT INTO users             │
│ 4. setup_base_worker_settings()     │
│    └─ INSERT INTO worker_settings   │
└─────────────────────────────────────┘

update_config.py (بروزرسانی پویا)
├─ --show (نمایش تنظیمات)
├─ --validate (اعتبارسنجی)
└─ --redis-host, --db-host, --es-host (تغییر)
```

---

## 🎯 Quick Start

```powershell
# 1. اجرای راه‌اندازی کامل
python c:\Users\win\the_first\response-network\api\setup\init_setup.py

# 2. شروع Docker
docker-compose -f c:\Users\win\the_first\docker-compose.dev.yml --profile response up -d

# 3. شروع Server
cd c:\Users\win\the_first\response-network\api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 4. باز کردن Swagger
# http://127.0.0.1:8000/docs
```

---
