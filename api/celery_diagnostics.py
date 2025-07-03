#!/usr/bin/env python3
"""
Comprehensive Celery diagnostics script
"""

import sys
import os
import time
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_redis_connection():
    """Test Redis connection"""
    print("🔍 Testing Redis connection...")
    
    try:
        import redis
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Test broker connection
        print(f"📋 Broker URL: {settings.celery_broker_url}")
        broker_client = redis.from_url(settings.celery_broker_url)
        broker_client.ping()
        print("✅ Broker (Redis) connection successful")
        
        # Test result backend connection
        print(f"📋 Result Backend URL: {settings.celery_result_backend}")
        backend_client = redis.from_url(settings.celery_result_backend)
        backend_client.ping()
        print("✅ Result backend (Redis) connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_app():
    """Test Celery app creation and configuration"""
    print("\n🔍 Testing Celery app...")
    
    try:
        from celery_app import celery_app
        
        print(f"✅ Celery app created successfully")
        print(f"📋 App name: {celery_app.main}")
        print(f"📋 Broker URL: {celery_app.conf.broker_url}")
        print(f"📋 Result Backend: {celery_app.conf.result_backend}")
        print(f"📋 Task serializer: {celery_app.conf.task_serializer}")
        print(f"📋 Worker pool: {celery_app.conf.worker_pool}")
        print(f"📋 Worker concurrency: {celery_app.conf.worker_concurrency}")
        print(f"📋 Includes: {celery_app.conf.include}")
        print(f"📋 Imports: {celery_app.conf.imports}")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_registration():
    """Test task registration"""
    print("\n🔍 Testing task registration...")
    
    try:
        from celery_app import celery_app
        
        # List all registered tasks
        print(f"📋 Registered tasks ({len(celery_app.tasks)}):")
        for task_name in sorted(celery_app.tasks.keys()):
            print(f"  - {task_name}")
        
        # Check for our specific task
        target_task = 'app.services.workflow.workers.batch_worker.process_batch_job'
        if target_task in celery_app.tasks:
            print(f"✅ Target task found: {target_task}")
            task_obj = celery_app.tasks[target_task]
            print(f"📋 Task object: {task_obj}")
            print(f"📋 Task module: {task_obj.__module__}")
        else:
            print(f"❌ Target task NOT found: {target_task}")
            
            # Try importing the task manually
            print("🔄 Attempting manual import...")
            try:
                from app.services.workflow.workers.batch_worker import process_batch_job
                print(f"✅ Manual import successful: {process_batch_job}")
                print(f"📋 Task name: {getattr(process_batch_job, 'name', 'No name attribute')}")
                
                # Check if it's now registered
                if target_task in celery_app.tasks:
                    print(f"✅ Task now registered after import")
                else:
                    print(f"❌ Task still not registered after import")
                    print(f"📋 Current registered tasks: {list(celery_app.tasks.keys())}")
                    
            except Exception as import_error:
                print(f"❌ Manual import failed: {import_error}")
                import traceback
                traceback.print_exc()
        
        return target_task in celery_app.tasks
        
    except Exception as e:
        print(f"❌ Task registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_worker_inspection():
    """Test worker inspection"""
    print("\n🔍 Testing worker inspection...")
    
    try:
        from celery_app import celery_app
        
        inspector = celery_app.control.inspect()
        
        # Get active workers
        active_workers = inspector.active()
        print(f"📊 Active workers: {active_workers}")
        
        if active_workers:
            print("✅ Workers are active")
            
            # Get registered tasks on workers
            registered_tasks = inspector.registered()
            print(f"📋 Registered tasks on workers: {registered_tasks}")
            
            # Get worker stats
            stats = inspector.stats()
            print(f"📈 Worker stats: {stats}")
            
        else:
            print("⚠️  No active workers found")
        
        return bool(active_workers)
        
    except Exception as e:
        print(f"❌ Worker inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_dispatch():
    """Test dispatching a dummy task"""
    print("\n🔍 Testing task dispatch...")
    
    try:
        from celery_app import celery_app
        
        task_name = 'app.services.workflow.workers.batch_worker.process_batch_job'
        dummy_job_id = f"test-{int(time.time())}"
        
        print(f"🚀 Dispatching test task with job ID: {dummy_job_id}")
        
        # Send task
        result = celery_app.send_task(task_name, args=[dummy_job_id])
        
        print(f"✅ Task dispatched successfully")
        print(f"📋 Task ID: {result.id}")
        print(f"📋 Task state: {result.state}")
        
        # Wait a bit and check state
        print("⏳ Waiting 5 seconds to check task state...")
        time.sleep(5)
        
        print(f"📋 Task state after 5s: {result.state}")
        
        if result.state == 'PENDING':
            print("⚠️  Task is still pending - worker might not be running or task might not be registered")
        elif result.state in ['STARTED', 'RETRY']:
            print("✅ Task was picked up by worker!")
        elif result.state == 'SUCCESS':
            print("✅ Task completed successfully!")
            print(f"📋 Result: {result.result}")
        elif result.state == 'FAILURE':
            print(f"❌ Task failed: {result.result}")
        
        return result.state not in ['PENDING']
        
    except Exception as e:
        print(f"❌ Task dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive diagnostics"""
    print("🧪 Comprehensive Celery Diagnostics")
    print("=" * 50)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📂 Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Celery App", test_celery_app),
        ("Task Registration", test_task_registration),
        ("Worker Inspection", test_worker_inspection),
        ("Task Dispatch", test_task_dispatch)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Summary:")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Recommendations
    if not results.get("Redis Connection", False):
        print("\n💡 Redis connection failed. Check:")
        print("  - Is Redis running?")
        print("  - Are Redis URL settings correct?")
        print("  - Is there a network connectivity issue?")
    
    if not results.get("Task Registration", False):
        print("\n💡 Task registration failed. Check:")
        print("  - Are imports working correctly?")
        print("  - Is the task decorated properly?")
        print("  - Are there circular import issues?")
    
    if not results.get("Worker Inspection", False):
        print("\n💡 No active workers found. Check:")
        print("  - Is the Celery worker process running?")
        print("  - Is the worker using the same Redis broker?")
        print("  - Are there any worker startup errors?")
    
    if not results.get("Task Dispatch", False):
        print("\n💡 Task dispatch failed. Check:")
        print("  - All of the above issues")
        print("  - Worker logs for specific errors")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
