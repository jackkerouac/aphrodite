#!/usr/bin/env python3
"""
Quick debug script to check what Jellyfin libraries API returns
"""

import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import from api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from app.services.jellyfin_service import get_jellyfin_service

async def debug_libraries():
    """Debug what the libraries API actually returns"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        print("🔍 Testing Jellyfin libraries API...")
        
        # Test connection first
        is_connected, message = await jellyfin_service.test_connection()
        print(f"📡 Connection: {'✅' if is_connected else '❌'} {message}")
        
        if not is_connected:
            print("❌ Cannot proceed without Jellyfin connection")
            return
        
        # Get libraries and inspect the raw data
        print("\n🔍 Fetching libraries...")
        libraries = await jellyfin_service.get_libraries()
        
        print(f"📊 Found {len(libraries)} libraries")
        
        if libraries:
            print("\n📋 Raw library data structure:")
            for i, lib in enumerate(libraries[:3]):  # Show first 3 libraries
                print(f"\n--- Library {i+1} ---")
                print(f"Raw data: {lib}")
                print(f"Keys: {list(lib.keys())}")
                
                # Check common field names
                potential_id_fields = ['Id', 'id', 'ID', 'ItemId', 'LibraryId']
                potential_name_fields = ['Name', 'name', 'DisplayName', 'Title']
                potential_type_fields = ['CollectionType', 'Type', 'type', 'LibraryType']
                
                print("🔍 Looking for ID field:")
                for field in potential_id_fields:
                    if field in lib:
                        print(f"  ✅ {field}: {lib[field]}")
                
                print("🔍 Looking for Name field:")
                for field in potential_name_fields:
                    if field in lib:
                        print(f"  ✅ {field}: {lib[field]}")
                
                print("🔍 Looking for Type field:")
                for field in potential_type_fields:
                    if field in lib:
                        print(f"  ✅ {field}: {lib[field]}")
        
        await jellyfin_service.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_libraries())
