#!/usr/bin/env python3
"""
Quick health check for Celery configuration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def check_celery_config():
    """Check Celery configuration"""
    print("🔍 Checking Celery configuration...")
    
    try:
        from celery_app import celery_app
        print(f"✅ Celery app created successfully")
        print(f"📋 Broker URL: {celery_app.conf.broker_url}")
        print(f"📋 Result Backend: {celery_app.conf.result_backend}")
        print(f"📋 Includes: {celery_app.conf.include}")
        print(f"📋 Imports: {celery_app.conf.imports}")
        
        return True
    except Exception as e:
        print(f"❌ Celery configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_task_import():
    """Check if task can be imported"""
    print("\n🔍 Checking task import...")
    
    try:
        from app.services.workflow.workers.batch_worker import process_batch_job
        print(f"✅ Task imported successfully: {process_batch_job}")
        print(f"📋 Task name: {process_batch_job.name}")
        return True
    except Exception as e:
        print(f"❌ Task import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_config():
    """Check database configuration"""
    print("\n🔍 Checking database configuration...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print(f"✅ Settings loaded successfully")
        print(f"📋 Database URL: {settings.database_url}")
        return True
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all checks"""
    print("🧪 Aphrodite Celery Health Check")
    print("=" * 40)
    
    checks = [
        ("Celery Config", check_celery_config),
        ("Task Import", check_task_import),  
        ("Database Config", check_database_config)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    print("\n📋 Summary:")
    for name, success in results.items():
        print(f"{name}: {'✅' if success else '❌'}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ All checks passed' if all_passed else '❌ Some checks failed'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
