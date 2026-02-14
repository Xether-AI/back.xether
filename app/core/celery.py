"""Celery configuration for background task processing."""

from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "xether_worker",
    broker=settings.redis_url_str,
    backend=settings.redis_url_str,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

if __name__ == "__main__":
    celery_app.start()
