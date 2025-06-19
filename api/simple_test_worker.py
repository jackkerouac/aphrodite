#!/usr/bin/env python3
"""
Simple Test Worker

Basic Celery worker for testing the setup - Windows compatible.
"""

from celery import Celery
import time

# Create simple Celery app for testing
celery_app = Celery('aphrodite_test_worker')
celery_app.conf.update(
    broker_url='redis://localhost:6380/0',
    result_backend='redis://localhost:6380/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    # Windows compatibility
    worker_pool='solo',  # Use solo pool for Windows
    worker_concurrency=1,
)

@celery_app.task
def test_task(message):
    """Simple test task"""
    print(f"🔄 Processing test task: {message}")
    time.sleep(2)
    print(f"✅ Test task completed: {message}")
    return f"Processed: {message}"

if __name__ == '__main__':
    print("🚀 Starting Test Worker...")
    print("Redis: redis://localhost:6380/0")
    
    # Start worker with Windows-compatible settings
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Force solo pool for Windows
        '--concurrency=1'
    ])
