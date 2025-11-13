# Request Network vs Response Network Worker Architecture

## 🎯 معماری صحیح

### **Response Network Workers** (Beat Scheduler دارد)
```
Celery Beat (Scheduler)
    ├─ export_settings → هر 60 ثانیه
    ├─ export_results → هر 120 ثانیه
    ├─ cache_maintenance → هر 3600 ثانیه
    └─ system_monitoring → هر 300 ثانیه

Celery Worker (Processor)
    └─ اجرای تسک‌های درخواست شده توسط Beat
```

**مسئولیت:** ⏰ **برنامه‌زمانی و تنظیمات**

---

### **Request Network Workers** (بدون Beat!)
```
❌ Celery Beat ندارد

Celery Worker (Processor)
    ├─ تسک‌های reactive (واکنشی):
    │   ├─ import_settings_from_response_network()
    │   ├─ export_pending_requests()
    │   └─ import_response_files()
    │
    └─ تسک‌های triggered by events:
        └─ از Request Network API یا سیستم خارجی
```

**مسئولیت:** 📥📤 **Import/Export درخواست‌ها و نتایج**

---

## 📊 فلو درست

```
Response Network (Control Panel)
    │
    ├─ Beat: "export settings every 60s"
    │   └─ worker.tasks.settings_exporter.export_settings_to_request_network()
    │       └─ ایجاد فایل settings در /exports/settings
    │
    └─ Beat: "export results every 120s"
        └─ worker.tasks.export_results.export_completed_results()
            └─ ایجاد فایل results در /exports/results


Request Network (Processing)
    │
    ├─ Worker: "import settings" (reactive)
    │   └─ Triggered by: فایل جدید در /imports/settings
    │
    ├─ Worker: "process requests" (reactive)
    │   └─ Triggered by: API call یا scheduled task از Response Network
    │
    └─ Worker: "export requests" (reactive)
        └─ Triggered by: new pending requests در database
```

---

## ✅ تنظیمات صحیح

### Response Network
```python
# response-network/workers/celery_app.py

celery_app.conf.beat_schedule = {
    "export-settings-every-minute": {
        "task": "workers.tasks.settings_exporter.export_settings_to_request_network",
        "schedule": 60.0,
    },
    "export-results-every-2-minutes": {
        "task": "workers.tasks.export_results.export_completed_results",
        "schedule": 120.0,
    },
}
```

### Request Network
```python
# request-network/workers/celery_app.py

# ❌ بدون beat_schedule!
# فقط reactive tasks

# Tasks:
# - import_settings_from_response_network() → when needed
# - export_pending_requests() → when needed  
# - import_response_files() → when needed
```

---

## 🚀 اجرای صحیح

### Response Network (دارای Beat)
```powershell
# Terminal 1: Beat Scheduler (تنها یکی اجرا شود!)
cd response-network
celery -A workers.celery_app beat --loglevel=info

# Terminal 2: Workers (می‌تواند چند instance باشد)
cd response-network
celery -A workers.celery_app worker --loglevel=info --concurrency=4
```

### Request Network (بدون Beat)
```powershell
# فقط Worker (بدون Beat!)
cd request-network
celery -A workers.celery_app worker --loglevel=info --concurrency=4

# Tasks به صورت reactive اجرا می‌شوند
```

---

## 📋 توضیح Tasks

### Response Network (Proactive/Scheduled)
| Task | Schedule | کار |
|------|----------|-----|
| export_settings | 60s | ایجاد فایل تنظیمات برای import |
| export_results | 120s | ایجاد فایل نتایج برای import |
| system_monitoring | 300s | نظارت بر سیستم |
| cache_maintenance | 3600s | تمیز‌کاری کش |

### Request Network (Reactive/On-Demand)
| Task | Trigger | کار |
|------|---------|-----|
| import_settings | فایل جدید | خواندن تنظیمات export شده |
| export_requests | API call | ایجاد فایل درخواست‌ها |
| import_results | فایل جدید | خواندن نتایج export شده |

---

## 🎓 خلاصه

**Response Network = Control Center (دارای برنامه‌زمانی)**
- تصمیم می‌گیرد: چه زمانی export کند
- ایجاد می‌کند: فایل‌های export برای request network

**Request Network = Processing Center (بدون برنامه‌زمانی)**
- منتظر می‌ماند: فایل‌های export شده
- پردازش می‌کند: درخواست‌ها
- ایجاد می‌کند: نتایج

