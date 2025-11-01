"""تنظیمات Celery برای شبکه پاسخ"""
from celery import Celery
from celery.schedules import crontab

from workers.config import settings

celery_app = Celery(
    "response_network",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# تنظیمات Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# برنامه زمان‌بندی تسک‌ها
celery_app.conf.beat_schedule = {
    "export_settings": {
        "task": "export_settings_to_request_network",
        "schedule": crontab(minute="*/5"),  # هر 5 دقیقه
    }
}

# بارگذاری تسک‌ها
celery_app.autodiscover_tasks([
    "workers.tasks.settings_exporter"
])