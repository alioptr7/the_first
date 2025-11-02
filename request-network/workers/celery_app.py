"""تنظیمات Celery برای شبکه درخواست"""
from celery import Celery
from celery.schedules import crontab

from workers.config import settings

celery_app = Celery(
    "request_network",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL)
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
        "task": "workers.tasks.request_processor.process_request_from_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    },
    "process_responses": {
        "task": "workers.tasks.response_processor.process_response_from_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    }
}

# بارگذاری تسک‌ها
celery_app.autodiscover_tasks([
    "workers.tasks"
])