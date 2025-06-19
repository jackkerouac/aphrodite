#!/usr/bin/env python3
"""
Windows Compatible Worker

Minimal Celery worker that works reliably on Windows.
"""

from celery import Celery
import time

# Create minimal Celery app
app = Celery('windows_worker')

# Minimal configuration for Windows
app.conf.broker_url = 'redis://localhost:6380/0'
app.conf.result_backend = 'redis://localhost:6380/0'

@app.task
def simple_task(message):
    """Super simple task"""
    print(f"Processing: {message}")
    time.sleep(1)
    print(f"Completed: {message}")
    return f"Done: {message}"

if __name__ == '__main__':
    print("Starting Windows Compatible Worker...")
    print("Redis: redis://localhost:6380/0")
    print("Pool: solo (Windows compatible)")
    print("=" * 40)
    
    # Run with minimal arguments
    app.worker_main([
        'worker',
        '--pool=solo'
    ])
