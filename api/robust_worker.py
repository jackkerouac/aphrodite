#!/usr/bin/env python3
"""
Robust Celery Worker Startup Script

Ensures proper task registration and provides better error handling.
"""

import os
import sys
import time
import signal
import logging
from typing import Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('aphrodite.worker.startup')

def setup_environment():
    """Setup environment for worker"""
    logger.info("🔧 Setting up worker environment...")
    
    # Ensure Python path includes app directory
    app_dir = '/app'
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Set environment variables for worker
    os.environ.setdefault('PYTHONPATH', '/app')
    os.environ.setdefault('WORKER_STARTUP', 'true')
    
    logger.info(f"📂 Python path: {sys.path[:3]}...")
    logger.info(f"📂 Working directory: {os.getcwd()}")

def verify_dependencies():
    """Verify all dependencies are available"""
    logger.info("🔍 Verifying dependencies...")
    
    try:
        # Test database connectivity
        from app.core.config import get_settings
        settings = get_settings()
        logger.info(f"✅ Settings loaded - DB: {settings.database_url[:50]}...")
        
        # Test Redis connectivity
        import redis
        redis_client = redis.from_url(settings.celery_broker_url)
        redis_client.ping()
        logger.info("✅ Redis connection successful")
        
        # Test Celery app creation
        from celery_app import celery_app
        logger.info(f"✅ Celery app loaded - {celery_app.main}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dependency verification failed: {e}")
        return False

def register_tasks():
    """Explicitly register tasks"""
    logger.info("📋 Registering tasks...")
    
    try:
        # Import task modules to ensure registration
        from app.services.workflow.workers.batch_worker import process_batch_job
        from celery_app import celery_app
        
        logger.info(f"✅ Imported batch worker task: {process_batch_job.name}")
        
        # Verify task is registered
        registered_tasks = list(celery_app.tasks.keys())
        target_task = 'app.services.workflow.workers.batch_worker.process_batch_job'
        
        if target_task in registered_tasks:
            logger.info(f"✅ Task properly registered: {target_task}")
        else:
            logger.warning(f"⚠️  Task not found in registered tasks: {target_task}")
            logger.info(f"📋 Available tasks: {registered_tasks}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Task registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_worker():
    """Start the Celery worker with proper configuration"""
    logger.info("🚀 Starting Celery worker...")
    
    try:
        from celery_app import celery_app
        
        # Worker configuration
        worker_args = [
            'worker',
            '--loglevel=info',
            '--pool=solo',
            '--concurrency=1',
            '--without-gossip',
            '--without-mingle',
            '--without-heartbeat',
            # Add explicit task routes
            '--queues=default',
            # Increase task timeout
            '--task-time-limit=3600',  # 1 hour
            '--task-soft-time-limit=3300',  # 55 minutes
        ]
        
        logger.info(f"📋 Worker args: {worker_args}")
        
        # Start the worker
        celery_app.start(worker_args)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Worker shutdown requested")
    except Exception as e:
        logger.error(f"❌ Worker startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"📨 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

def main():
    """Main worker startup sequence"""
    logger.info("🔄 Starting Aphrodite Celery Worker")
    logger.info("=" * 50)
    
    # Setup
    setup_signal_handlers()
    setup_environment()
    
    # Verification steps
    if not verify_dependencies():
        logger.error("❌ Dependencies not available, exiting")
        sys.exit(1)
    
    if not register_tasks():
        logger.error("❌ Task registration failed, exiting")
        sys.exit(1)
    
    # Wait a moment for everything to settle
    logger.info("⏳ Waiting 2 seconds for initialization...")
    time.sleep(2)
    
    # Start the worker
    start_worker()

if __name__ == "__main__":
    main()
