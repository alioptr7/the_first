from celery import Celery
from celery.schedules import schedule as _schedule
from .config import settings

# Create the Celery application instance for the Response Network
celery_app = Celery(
    "response_network_worker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "api.workers.tasks.import_requests",
        "api.workers.tasks.query_executor",
        "api.workers.tasks.export_results",
        "api.workers.tasks.cache_maintenance",
        "api.workers.tasks.system_monitoring",
        "api.workers.tasks.settings_exporter",
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
        "task": "api.workers.tasks.import_requests.import_request_files",
        "schedule": _schedule(settings.IMPORT_REQUESTS_POLL_SECONDS),
    },
    "export-completed-results-every-2-minutes": {
        "task": "api.workers.tasks.export_results.export_completed_results",
        "schedule": _schedule(settings.EXPORT_RESULTS_SCHEDULE_SECONDS),
    },
    "maintain-cache-every-hour": {
        "task": "api.workers.tasks.cache_maintenance.maintain_cache",
        "schedule": _schedule(settings.CACHE_MAINTENANCE_SCHEDULE_SECONDS),
    },
    "run-system-health-check-every-5-minutes": {
        "task": "api.workers.tasks.system_monitoring.system_health_check",
        "schedule": _schedule(settings.SYSTEM_MONITORING_SCHEDULE_SECONDS),
    },
    "export-settings-every-minute": {
        "task": "api.workers.tasks.settings_exporter.export_settings_to_request_network",
        "schedule": 60.0,  # 1 minute
    },
}