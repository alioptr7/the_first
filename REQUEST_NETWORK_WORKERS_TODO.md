# وضعیت Request Network Worker Tasks

## مسئله فعلی

Request Network Worker tasks ثبت نمی‌کند. لاگ نشان میدهد:
```
[tasks]
(خالی - کوئی task موجود نیست)
```

اما Response Network Worker correctly tasks را دارد:
```
[tasks]
  . workers.tasks.password_sync.sync_password_to_request_network
  . workers.tasks.profile_types_exporter.export_profile_types_to_request_network
  . workers.tasks.settings_exporter.export_settings_to_request_network
  . workers.tasks.users_exporter.export_users_to_request_network
```

## Request Network Tasks موجود

فایل: `request-network/api/workers/tasks/settings_importer.py`

```python
@shared_task
def import_settings_from_response_network():
    """Import settings from response network"""
```

## راه حل لازم

1. **workers/tasks/__init__.py** - باید این را import کند:
```python
from . import settings_importer  # noqa
```

2. **workers/celery_app.py** - باید schedule تنظیم شود:
```python
beat_schedule={
    "import-settings-every-60s": {
        "task": "workers.tasks.settings_importer.import_settings_from_response_network",
        "schedule": 60.0,
    },
}
```

## چک کردن

زمانی که Worker شروع شود، باید بگوید:
```
[tasks]
  . workers.tasks.settings_importer.import_settings_from_response_network
```

## مراحل بعدی

1. ✅ Request Network Worker را شروع کنید با Redis 6379
2. ⏳ منتظر بمانید 60 ثانیه
3. ⏳ دیکھیں آیا tasks import شوند
4. ✅ Database میں users دیکھیں
