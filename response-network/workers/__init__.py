"""Response-network workers package initializer.

Expose `celery_app` at package level so `import workers; workers.celery_app` works
when PYTHONPATH points to `response-network`.
"""
from .celery_app import celery_app  # noqa: F401

__all__ = ["celery_app"]
