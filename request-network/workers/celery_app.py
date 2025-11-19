from celery import Celery
from .config import settings

# Create the Celery application instance
celery_app = Celery(
    "request_network_worker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "workers.tasks.export_requests",
        "workers.tasks.import_results",
        "workers.tasks.settings_importer",
        "workers.tasks.users_importer",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Configure retry behavior
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Celery Beat schedule - Import settings and passwords every 60 seconds
celery_app.conf.beat_schedule = {
    "import-settings-and-passwords-every-minute": {
        "task": "workers.tasks.settings_importer.import_settings_and_passwords",
        "schedule": 60.0,  # Every 60 seconds
    },
}
# Request Network only has reactive tasks (triggered when needed)