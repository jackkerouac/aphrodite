#!/usr/bin/env python3
"""
Quick Jellyfin Test Script

Test if Jellyfin connectivity is working and badge processing will succeed.
Run this inside your Docker container to diagnose issues.
"""

import asyncio
import sys
import os

async def test_jellyfin_quick():
    """Quick test of Jellyfin connectivity and badge processing readiness"""
    print("🔧 Aphrodite Jellyfin Quick Test")
    print("=" * 50)
    
    try:
        # Test 1: Jellyfin Service Import
        print("📦 Testing imports...")
        from app.services.jellyfin_service import get_jellyfin_service
        from app.core.database import async_session_factory
        from sqlalchemy import select
        print("✅ Imports successful")
        
        # Test 2: Jellyfin Connection
        print("\n🌐 Testing Jellyfin connection...")
        jellyfin_service = get_jellyfin_service()
        success, message = await jellyfin_service.test_connection()
        
        if success:
            print(f"✅ Connection: {message}")
        else:
            print(f"❌ Connection failed: {message}")
            return False
        
        # Test 3: Get Libraries
        print("\n📚 Testing library access...")
        libraries = await jellyfin_service.get_libraries()
        print(f"✅ Found {len(libraries)} libraries")
        for lib in libraries[:3]:
            print(f"   • {lib.get('Name', 'Unknown')}")
        
        # Test 4: Test a sample item if database has items
        print("\n🎬 Testing sample media item...")
        try:
            if async_session_factory:
                async with async_session_factory() as session:
                    from app.models.media import MediaItemModel
                    stmt = select(MediaItemModel).limit(1)
                    result = await session.execute(stmt)
                    sample_item = result.scalar_one_or_none()
                    
                    if sample_item:
                        print(f"📽️  Testing: {sample_item.title} ({sample_item.jellyfin_id})")
                        
                        # Test user-specific API (this should work)
                        media_data = await jellyfin_service.get_media_item_by_id(sample_item.jellyfin_id)
                        if media_data:
                            print(f"✅ User API works: {media_data.get('Name', 'Unknown')}")
                        else:
                            print("❌ User API failed")
                        
                        # Test poster availability
                        poster_url = await jellyfin_service.get_poster_url(sample_item.jellyfin_id)
                        if poster_url:
                            print("✅ Poster URL accessible")
                        else:
                            print("❌ Poster URL failed")
                    else:
                        print("ℹ️  No media items in database yet")
            else:
                print("⚠️  Database not available")
        except Exception as db_error:
            print(f"⚠️  Database test failed: {db_error}")
        
        print("\n🎉 Quick test completed!")
        print("\n💡 Next steps:")
        print("   1. Try badge processing from the web interface")
        print("   2. If issues persist, check the Diagnostics page")
        print("   3. Verify your Jellyfin settings in Settings > Configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'jellyfin_service' in locals():
            await jellyfin_service.close()

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_jellyfin_quick())
    sys.exit(0 if result else 1)
