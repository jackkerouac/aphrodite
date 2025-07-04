#!/usr/bin/env python3
"""
Quick database table checker
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, '/app/api')

async def check_database_tables():
    """Check if batch_jobs table exists and is accessible"""
    try:
        from app.core.database import async_session_factory, get_fresh_db_session
        from sqlalchemy import text
        
        print("🔍 Checking database table access...")
        
        # Strategy 1: Try session factory
        if async_session_factory:
            try:
                async with async_session_factory() as db:
                    # Check if batch_jobs table exists
                    result = await db.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'batch_jobs'
                    """))
                    table_exists = result.fetchone() is not None
                    
                    print(f"📊 batch_jobs table exists: {table_exists}")
                    
                    if table_exists:
                        # Try to count rows
                        result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                        count = result.fetchone()[0]
                        print(f"📈 batch_jobs count: {count}")
                        return True
                    else:
                        print("❌ batch_jobs table does not exist!")
                        return False
                        
            except Exception as e:
                print(f"❌ Session factory failed: {e}")
        
        # Strategy 2: Try fresh session
        try:
            async for db in get_fresh_db_session():
                # Check if batch_jobs table exists
                result = await db.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'batch_jobs'
                """))
                table_exists = result.fetchone() is not None
                
                print(f"📊 batch_jobs table exists (fresh): {table_exists}")
                
                if table_exists:
                    # Try to count rows
                    result = await db.execute(text("SELECT COUNT(*) FROM batch_jobs"))
                    count = result.fetchone()[0]
                    print(f"📈 batch_jobs count (fresh): {count}")
                    return True
                else:
                    print("❌ batch_jobs table does not exist (fresh)!")
                    return False
                break
                
        except Exception as e:
            print(f"❌ Fresh session also failed: {e}")
            return False
            
    except Exception as e:
        print(f"💥 Database check failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_database_tables())
    print(f"\n🏁 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
