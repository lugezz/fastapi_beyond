from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "fastapi_beyond",
    broker=settings.broker_url,
    backend=settings.result_url,
    include=["app.tasks.celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
