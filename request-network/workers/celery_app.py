"""تنظیمات Celery برای شبکه درخواست"""
from celery import Celery
from celery.schedules import crontab

from workers.config import settings

celery_app = Celery(
    "request_network",
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
    "process_requests": {
        "task": "process_request_from_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    },
    "process_responses": {
        "task": "process_response_from_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    }
}

# بارگذاری تسک‌ها
celery_app.autodiscover_tasks([
    "workers.tasks.request_processor",
    "workers.tasks.response_processor"
])