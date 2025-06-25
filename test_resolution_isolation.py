#!/usr/bin/env python3
"""
Resolution Processor Thread Isolation Test

Tests that the resolution processor v1 aggregator isolation fix works correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "api"))

async def test_resolution_processor_isolation():
    """Test the resolution processor v1 aggregator isolation"""
    print("🧪 Testing Resolution Processor V1 Aggregator Isolation")
    print("=" * 60)
    
    try:
        # Initialize database first
        from app.core.database import init_db
        await init_db()
        print("✅ Database initialized")
        
        # Import resolution processor
        from app.services.badge_processing.resolution_processor import ResolutionBadgeProcessor
        
        # Create processor
        processor = ResolutionBadgeProcessor()
        print("✅ ResolutionBadgeProcessor created")
        
        # Test the problematic TV series call that was corrupting database connections
        test_poster_path = "/tmp/test_poster.jpg"
        ahsoka_jellyfin_id = "e89693a94849aed9fb0cb2e8cc180f1b"  # The series that was failing
        
        print(f"📺 Testing TV series resolution detection:")
        print(f"   Jellyfin ID: {ahsoka_jellyfin_id}")
        print(f"   This call was previously corrupting database connections...")
        print()
        
        # Call the method that was causing the database corruption
        try:
            resolution = await processor._get_resolution_from_jellyfin_id(ahsoka_jellyfin_id)
            print(f"✅ Resolution detection successful: {resolution}")
            print("✅ No database connection corruption detected!")
            
        except Exception as resolution_error:
            print(f"❌ Resolution detection failed: {resolution_error}")
            return False
        
        # Test that database is still healthy after the v1 aggregator call
        print("\n🏥 Testing database health after v1 aggregator call:")
        try:
            from app.core.database import DatabaseManager
            health = await DatabaseManager.health_check()
            print(f"   Status: {health['status']}")
            print(f"   Message: {health['message']}")
            
            if health['status'] == 'healthy':
                print("✅ Database remains healthy after v1 aggregator call!")
                return True
            else:
                print("❌ Database corrupted after v1 aggregator call")
                return False
                
        except Exception as health_error:
            print(f"❌ Database health check failed: {health_error}")
            return False
        
    except Exception as e:
        print(f"🚨 CRITICAL ERROR in resolution processor test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    print("🚀 Resolution Processor Database Isolation Test")
    print("🎯 Testing the fix for v1 aggregator database corruption")
    print()
    
    success = await test_resolution_processor_isolation()
    
    if success:
        print("\n🎉 Resolution processor isolation test PASSED!")
        print("\n📝 Expected behavior:")
        print("   ✅ V1 aggregator runs in isolated thread")
        print("   ✅ Database connections remain healthy")
        print("   ✅ Review processor should now run after resolution processor")
        print("\n📋 Next steps:")
        print("   1. Rebuild Docker container with this fix")
        print("   2. Test badge pipeline with Ahsoka series")
        print("   3. Verify review processor runs and RT/Metacritic badges appear")
        return 0
    else:
        print("\n❌ Resolution processor isolation test FAILED!")
        print("📝 The v1 aggregator may still be corrupting database connections.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
