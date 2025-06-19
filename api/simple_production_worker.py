#!/usr/bin/env python3
"""
Simple Production Worker

Celery worker for Aphrodite v2 background processing - Windows compatible.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from celery_app import celery_app
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.worker.startup")

# Configure for Windows compatibility
celery_app.conf.update(
    worker_pool='solo',  # Use solo pool for Windows
    worker_concurrency=1,
)

if __name__ == '__main__':
    print("🚀 Starting Simple Production Worker...")
    print("=" * 50)
    print(f"Redis: redis://localhost:6380/0")
    print(f"Processing: Aphrodite batch jobs")
    print(f"Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start worker with Windows-compatible settings
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Force solo pool for Windows
        '--concurrency=1'
    ])
