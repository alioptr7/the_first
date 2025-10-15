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
        "workers.tasks.cleanup",
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

# Celery Beat schedule (for periodic tasks)
celery_app.conf.beat_schedule = {
    "export-pending-requests-every-2-minutes": {
        "task": "workers.tasks.export_requests.export_pending_requests",
        "schedule": settings.EXPORT_SCHEDULE_SECONDS,
    },
    "import-response-files-every-30-seconds": {
        "task": "workers.tasks.import_results.import_response_files",
        "schedule": settings.IMPORT_POLL_SECONDS,
    },
}