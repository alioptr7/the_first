"""تنظیمات Celery برای شبکه پاسخ"""
from celery import Celery
from celery.schedules import crontab

from workers.config import settings

celery_app = Celery(
    "response_network",
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
    "import_requests": {
        "task": "workers.tasks.import_requests.import_requests_from_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    },
    "export_responses": {
        "task": "workers.tasks.export_responses.export_responses_to_redis",
        "schedule": 30.0,  # هر 30 ثانیه
    }
}

# بارگذاری تسک‌ها
celery_app.autodiscover_tasks([
    "workers.tasks"
])