from celery import Celery
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
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["workers.tasks"], force=True)