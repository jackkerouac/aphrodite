"""
Celery Configuration

Celery app configuration for background processing.
"""

from celery import Celery
from app.core.config import get_settings

# Get settings
settings = get_settings()

# Create the Celery app
celery_app = Celery('aphrodite_worker')

# Configuration
celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Windows compatibility
    worker_pool='solo',
    worker_concurrency=1,
    # Use the v2 batch worker instead of unified_worker
    include=['app.services.workflow.workers.batch_worker']
)

__all__ = ['celery_app']
