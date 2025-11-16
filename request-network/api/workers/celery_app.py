from celery import Celery
from celery.schedules import crontab
from core.config import settings

# Initialize celery app
celery_app = Celery(
    "request_network",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_scheduler="celery.beat:PersistentScheduler",
    beat_schedule={
        "import-settings-every-60s": {
            "task": "workers.tasks.settings_importer.import_settings_from_response_network",
            "schedule": 60.0,  # هر 60 ثانیه
        },
    },
)

# Auto-discover tasks from this package
celery_app.autodiscover_tasks(["workers.tasks"], force=True)

# Import tasks explicitly to ensure they are registered
try:
    from workers.tasks import settings_importer  # noqa
except ImportError:
    pass