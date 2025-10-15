from celery import Celery
from .config import settings

# Create the Celery application instance for the Response Network
celery_app = Celery(
    "response_network_worker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "workers.tasks.import_requests",
        "workers.tasks.query_executor",
        "workers.tasks.export_results",
        "workers.tasks.cache_maintenance",
        "workers.tasks.system_monitoring",
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
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Celery Beat schedule for the Response Network
celery_app.conf.beat_schedule = {
    "import-request-files-every-30-seconds": {
        "task": "workers.tasks.import_requests.import_request_files",
        "schedule": settings.IMPORT_REQUESTS_POLL_SECONDS,
    },
    "export-completed-results-every-2-minutes": {
        "task": "workers.tasks.export_results.export_completed_results",
        "schedule": settings.EXPORT_RESULTS_SCHEDULE_SECONDS,
    },
    "maintain-cache-every-hour": {
        "task": "workers.tasks.cache_maintenance.maintain_cache",
        "schedule": settings.CACHE_MAINTENANCE_SCHEDULE_SECONDS,
    },
    "run-system-health-check-every-5-minutes": {
        "task": "workers.tasks.system_monitoring.system_health_check",
        "schedule": settings.SYSTEM_MONITORING_SCHEDULE_SECONDS,
    },
}