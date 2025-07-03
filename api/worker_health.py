#!/usr/bin/env python3
"""
Simple worker health check that doesn't cause import issues
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def worker_health_check():
    """Simple health check for the worker"""
    try:
        # Test basic imports
        import redis
        from app.core.config import get_settings
        
        # Test Redis connection
        settings = get_settings()
        redis_client = redis.from_url(settings.celery_broker_url)
        redis_client.ping()
        
        print("Worker healthy: Redis connection OK")
        return True
        
    except Exception as e:
        print(f"Worker health check failed: {e}")
        return False

if __name__ == "__main__":
    success = worker_health_check()
    sys.exit(0 if success else 1)
