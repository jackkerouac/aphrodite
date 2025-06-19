"""
Celery Configuration

Celery app configuration for background processing.
"""

from celery import Celery
from app.services.workflow.workers.batch_worker import celery_app

# Export the celery app for worker startup
__all__ = ['celery_app']
