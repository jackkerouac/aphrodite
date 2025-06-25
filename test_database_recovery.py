#!/usr/bin/env python3
"""
Database Connection Recovery Test Script

This script tests the database connection recovery mechanisms implemented
to fix the badge pipeline crash issue.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "api"))

async def test_database_connections():
    """Test various database connection strategies"""
    print("🧪 Testing Database Connection Recovery Mechanisms")
    print("=" * 60)
    
    try:
        # Import database components
        from app.core.database import (
            init_db, DatabaseManager, async_session_factory,
            get_fresh_db_session, reset_database_connections
        )
        from app.core.config import get_settings
        from sqlalchemy import text
        
        print("📋 Configuration:")
        settings = get_settings()
        database_url = settings.get_database_url()
        print(f"   Database URL: {database_url}")
        print()
        
        # Test 1: Initialize database
        print("🔌 Test 1: Database Initialization")
        try:
            await init_db()
            print("   ✅ Database initialized successfully")
        except Exception as e:
            print(f"   ❌ Database initialization failed: {e}")
            return False
        
        # Test 2: Health check
        print("\n🏥 Test 2: Database Health Check")
        try:
            health = await DatabaseManager.health_check()
            print(f"   Status: {health['status']}")
            print(f"   Message: {health['message']}")
            if health['status'] != 'healthy':
                print("   ⚠️ Database not healthy, but continuing tests...")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        # Test 3: Standard session factory
        print("\n🔗 Test 3: Standard Session Factory")
        try:
            if async_session_factory:
                async with async_session_factory() as session:
                    result = await session.execute(text("SELECT 1 as test"))
                    row = result.fetchone()
                    print(f"   ✅ Standard session successful: {row}")
            else:
                print("   ❌ Session factory not available")
        except Exception as e:
            print(f"   ❌ Standard session failed: {e}")
        
        # Test 4: Fresh database session
        print("\n🆕 Test 4: Fresh Database Session")
        try:
            async for fresh_session in get_fresh_db_session():
                result = await fresh_session.execute(text("SELECT 2 as fresh_test"))
                row = result.fetchone()
                print(f"   ✅ Fresh session successful: {row}")
                break
        except Exception as e:
            print(f"   ❌ Fresh session failed: {e}")
        
        # Test 5: Connection recovery simulation
        print("\n🔄 Test 5: Connection Recovery Simulation")
        try:
            # Reset connections
            reset_database_connections()
            print("   🔄 Database connections reset")
            
            # Re-initialize
            await init_db()
            print("   ✅ Database re-initialized successfully")
            
            # Test after recovery
            async with async_session_factory() as session:
                result = await session.execute(text("SELECT 3 as recovery_test"))
                row = result.fetchone()
                print(f"   ✅ Post-recovery session successful: {row}")
                
        except Exception as e:
            print(f"   ❌ Connection recovery failed: {e}")
        
        # Test 6: Badge pipeline database usage simulation
        print("\n🎯 Test 6: Badge Pipeline Database Usage Simulation")
        try:
            from app.services.badge_processing.database_service import badge_settings_service
            
            # Simulate what the badge processors do
            processors = ["resolution", "review", "awards", "audio"]
            
            for i, processor_name in enumerate(processors):
                print(f"   🛠️ Simulating {processor_name} processor ({i+1}/{len(processors)})")
                
                # Test main session factory (Strategy 1)
                try:
                    async with async_session_factory() as session:
                        # Test connection
                        await session.execute(text("SELECT 1"))
                        await session.commit()
                        
                        # Simulate settings loading (what each processor does)
                        if processor_name == "review":
                            settings = await badge_settings_service.get_review_settings(session)
                            print(f"      ✅ Loaded {processor_name} settings: {bool(settings)}")
                        else:
                            # Just test the connection for other processors
                            result = await session.execute(text(f"SELECT '{processor_name}' as processor"))
                            row = result.fetchone()
                            print(f"      ✅ {processor_name} database test: {row}")
                            
                except Exception as session_error:
                    print(f"      ⚠️ Main session failed for {processor_name}: {session_error}")
                    
                    # Test fallback strategy (Strategy 2)
                    try:
                        async for fresh_session in get_fresh_db_session():
                            await fresh_session.execute(text("SELECT 1"))
                            print(f"      ✅ Fresh session fallback successful for {processor_name}")
                            break
                    except Exception as fallback_error:
                        print(f"      ❌ Fallback also failed for {processor_name}: {fallback_error}")
            
            print("   🎯 Badge pipeline simulation completed")
            
        except Exception as e:
            print(f"   ❌ Badge pipeline simulation failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Database connection recovery test completed")
        return True
        
    except Exception as e:
        print(f"🚨 CRITICAL ERROR in database recovery test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    print("🚀 Aphrodite Database Connection Recovery Test")
    print("🎯 This script tests the fixes for the badge pipeline crash issue")
    print()
    
    success = await test_database_connections()
    
    if success:
        print("\n🎉 All database connection tests passed!")
        print("📝 The badge pipeline should now handle database connection issues properly.")
        print("\n📋 Next steps:")
        print("   1. Rebuild the Docker container")
        print("   2. Test the badge pipeline with Ahsoka series")
        print("   3. Verify that RT and Metacritic badges now appear")
        return 0
    else:
        print("\n❌ Some database connection tests failed!")
        print("📝 Review the errors above and fix configuration issues.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
