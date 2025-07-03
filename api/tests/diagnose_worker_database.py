#!/usr/bin/env python3
"""
Database diagnostic script for Aphrodite Worker

This script helps diagnose database connection issues for the Celery worker.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the API directory to the path
api_dir = Path(__file__).parent.parent
sys.path.insert(0, str(api_dir))

async def diagnose_database_issue():
    """Comprehensive database connection diagnosis"""
    print("🔍 Aphrodite Worker Database Diagnosis")
    print("=" * 50)
    
    # Print environment info
    print("\n📋 Environment Variables:")
    env_vars = [
        'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 
        'POSTGRES_USER', 'POSTGRES_PASSWORD', 'DATABASE_URL'
    ]
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        if 'PASSWORD' in var and value != 'Not set':
            value = '*' * len(value)  # Mask password
        print(f"  {var}: {value}")
    
    # Test settings loading
    print("\n⚙️ Testing Settings Loading:")
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print(f"  ✅ Settings loaded successfully")
        print(f"  🔗 Database URL: {settings.get_database_url()}")
        
        # Test if we're in Docker
        is_docker = os.path.exists('/.dockerenv')
        print(f"  🐳 Docker environment: {is_docker}")
        
    except Exception as e:
        print(f"  ❌ Settings loading failed: {e}")
        return False
    
    # Test direct database connection
    print("\n🗄️ Testing Database Connection:")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # Test with the exact same configuration as the worker
        engine = create_async_engine(
            settings.get_database_url(),
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True
        )
        
        async with engine.begin() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  ✅ Connection successful!")
            print(f"  📊 PostgreSQL Version: {version}")
            
            # Test if tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"  📋 Tables found: {', '.join(tables) if tables else 'No tables'}")
            
            # Check if alembic_version table exists
            if 'alembic_version' in tables:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version_num = result.scalar()
                print(f"  🔄 Alembic version: {version_num}")
            else:
                print(f"  ⚠️ No alembic_version table found")
            
            # Check if workflow tables exist
            workflow_tables = [t for t in tables if 'batch_job' in t or 'poster_processing' in t]
            if workflow_tables:
                print(f"  📝 Workflow tables: {', '.join(workflow_tables)}")
            else:
                print(f"  ⚠️ No workflow tables found")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Celery configuration
    print("\n🥬 Testing Celery Configuration:")
    try:
        from celery_app import celery_app
        print(f"  ✅ Celery app loaded successfully")
        print(f"  📡 Broker URL: {celery_app.conf.broker_url}")
        print(f"  💾 Result Backend: {celery_app.conf.result_backend}")
        
        # Check if the worker task is registered
        if 'app.services.workflow.workers.batch_worker.process_batch_job' in celery_app.tasks:
            print(f"  ✅ Batch worker task registered")
        else:
            print(f"  ❌ Batch worker task NOT registered")
            print(f"  📋 Registered tasks: {list(celery_app.tasks.keys())}")
            
    except Exception as e:
        print(f"  ❌ Celery configuration failed: {e}")
        return False
    
    # Test importing the batch worker
    print("\n🔧 Testing Batch Worker Import:")
    try:
        from app.services.workflow.workers.batch_worker import process_batch_job
        print(f"  ✅ Batch worker imported successfully")
        
        # Test the worker database connection method
        print("  🔍 Testing worker database connection logic...")
        from app.services.workflow.workers.batch_worker import _process_batch_job_async
        
        # We won't actually run the async function, just check if it imports
        print(f"  ✅ Worker async function imported successfully")
        
    except Exception as e:
        print(f"  ❌ Batch worker import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Database Diagnosis Complete!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = asyncio.run(diagnose_database_issue())
    if success:
        print("\n✅ All checks passed! Worker should be able to connect to database.")
    else:
        print("\n❌ Some checks failed. Please review the errors above.")
    sys.exit(0 if success else 1)
