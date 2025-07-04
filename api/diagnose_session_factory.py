#!/usr/bin/env python3
"""
Database Session Factory Diagnostic Script

Run this inside the Docker container to diagnose session factory issues.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the correct paths for the Docker container
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/api')
os.chdir('/app')

# Set the Python path environment variable
os.environ['PYTHONPATH'] = '/app:/app/api'

async def diagnose_session_factory():
    """Comprehensive session factory diagnosis"""
    print("🔍 Database Session Factory Diagnosis")
    print("=" * 50)
    
    try:
        # Import components
        from app.core.database import async_session_factory, init_db, get_session_factory_status
        from app.core.config import get_settings
        from sqlalchemy import text
        
        print("✅ Successfully imported database components")
        
        # Check initial state
        print("\n1. Initial Session Factory State:")
        if async_session_factory:
            print(f"   ✅ Session factory exists: {id(async_session_factory)}")
        else:
            print("   ❌ Session factory is None")
            
        status = get_session_factory_status()
        print(f"   Status: {status}")
        
        # Test database settings
        print("\n2. Database Configuration:")
        settings = get_settings()
        try:
            db_url = settings.get_database_url()
            print(f"   ✅ Database URL: {db_url.split('@')[1] if '@' in db_url else 'hidden'}")
        except Exception as e:
            print(f"   ❌ Database URL error: {e}")
            
        # Test initialization
        print("\n3. Database Initialization Test:")
        try:
            await init_db()
            print("   ✅ Database initialization successful")
        except Exception as e:
            print(f"   ❌ Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
            
        # Test session factory after init
        print("\n4. Session Factory After Init:")
        if async_session_factory:
            print(f"   ✅ Session factory exists: {id(async_session_factory)}")
            
            # Test session creation
            try:
                session = async_session_factory()
                print(f"   ✅ Session creation successful: {session}")
                
                # Test database query
                async with session as db:
                    result = await db.execute(text("SELECT 1 as test"))
                    row = result.fetchone()
                    print(f"   ✅ Database query successful: {row[0] if row else None}")
                    
                    # Test batch_jobs table
                    result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                    count = result.fetchone()[0] if result else 0
                    print(f"   ✅ Batch jobs table accessible: {count} jobs found")
                    
            except Exception as e:
                print(f"   ❌ Session/query failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ❌ Session factory is still None after init")
            
        # Test API context simulation
        print("\n5. API Context Simulation:")
        try:
            # Simulate what the API diagnostics does
            from app.core.database import get_db_session
            
            async for db in get_db_session():
                result = await db.execute(text("SELECT 1 as api_test"))
                row = result.fetchone()
                print(f"   ✅ API context database access: {row[0] if row else None}")
                break
                
        except Exception as e:
            print(f"   ❌ API context failed: {e}")
            import traceback
            traceback.print_exc()
            
        print("\n" + "=" * 50)
        print("🎯 Diagnosis complete!")
        
    except Exception as e:
        print(f"💥 Critical error during diagnosis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_session_factory())
