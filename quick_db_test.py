#!/usr/bin/env python3
"""
Quick Database Session Test

Simple test to see what's happening with session factory.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api"))

# Set environment for testing
os.environ['ENVIRONMENT'] = 'development'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'aphrodite'
os.environ['POSTGRES_USER'] = 'aphrodite'
os.environ['POSTGRES_PASSWORD'] = 'aphrodite123'

async def quick_test():
    """Quick test to see session factory behavior"""
    print("🔍 Quick Database Session Factory Test")
    
    # Import the module
    import api.app.core.database as db_module
    from api.app.core.database import init_db, get_session_factory_status
    
    print("Step 1: Check initial state")
    status = get_session_factory_status()
    print(f"Initial status: {status}")
    print(f"Module factory: {db_module.async_session_factory}")
    
    print("\nStep 2: Initialize database")
    await init_db()
    
    print("\nStep 3: Check state after init")
    status = get_session_factory_status()
    print(f"After init status: {status}")
    print(f"Module factory: {db_module.async_session_factory}")
    
    print("\nStep 4: Test session creation")
    if db_module.async_session_factory:
        try:
            session = db_module.async_session_factory()
            print(f"✅ Session created: {session}")
            await session.close()
        except Exception as e:
            print(f"❌ Session creation failed: {e}")
    else:
        print("❌ No session factory available")

if __name__ == "__main__":
    asyncio.run(quick_test())
