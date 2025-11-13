from celery import Celery
from core.config import settings

# Initialize celery app
celery_app = Celery(
    "response_network",
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
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Windows-specific configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Ensure tasks stay in queue if worker goes down
    result_expires=3600,  # 1 hour
)

# Auto-discover tasks BEFORE setting beat_schedule
celery_app.autodiscover_tasks(["workers.tasks"], force=True)

# Celery Beat schedule for the Response Network
celery_app.conf.beat_schedule = {
    "export-settings-every-minute": {
        "task": "workers.tasks.settings_exporter.export_settings_to_request_network",
        "schedule": 60.0,  # هر 60 ثانیه
    },
    "export-users-every-minute": {
        "task": "workers.tasks.users_exporter.export_users_to_request_network",
        "schedule": 60.0,  # هر 60 ثانیه
    },
    "export-profile-types-every-minute": {
        "task": "workers.tasks.profile_types_exporter.export_profile_types_to_request_network",
        "schedule": 60.0,  # هر 60 ثانیه
    },
}