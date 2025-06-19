#!/usr/bin/env python3
"""
Test the schedule configuration endpoints to verify fixes
"""

import asyncio
import aiohttp
import json

async def test_schedule_config():
    """Test schedule configuration endpoints"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Schedule Configuration Endpoints")
        print("=" * 50)
        
        # Test badge types endpoint
        print("\n1. Testing Badge Types API...")
        try:
            async with session.get(f"{base_url}/api/v1/schedules/config/badge-types") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Response: {json.dumps(data, indent=2)}")
                    badge_types = data.get('badge_types', [])
                    print(f"   ✅ Badge types count: {len(badge_types)}")
                else:
                    text = await response.text()
                    print(f"   ❌ Error: {text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test libraries endpoint 
        print("\n2. Testing Libraries API...")
        try:
            async with session.get(f"{base_url}/api/v1/schedules/config/libraries") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Response: {json.dumps(data, indent=2)}")
                    libraries = data.get('libraries', [])
                    print(f"   ✅ Libraries count: {len(libraries)}")
                    if libraries:
                        print("   ✅ Sample library:", libraries[0])
                elif response.status == 500:
                    text = await response.text()
                    print(f"   ⚠️  500 Error (expected if Jellyfin not configured): {text}")
                else:
                    text = await response.text()
                    print(f"   ❌ Unexpected error: {text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test cron presets endpoint
        print("\n3. Testing Cron Presets API...")
        try:
            async with session.get(f"{base_url}/api/v1/schedules/config/cron-presets") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Response: {json.dumps(data, indent=2)}")
                    presets = data.get('presets', {})
                    print(f"   ✅ Presets count: {len(presets)}")
                else:
                    text = await response.text()
                    print(f"   ❌ Error: {text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Test completed!")
        print("\nNext steps:")
        print("1. Start the frontend: npm run dev")
        print("2. Go to: http://localhost:3000/schedules")
        print("3. Click the 'Create Schedule' tab")
        print("4. Verify badge types and libraries load correctly")

if __name__ == "__main__":
    asyncio.run(test_schedule_config())
