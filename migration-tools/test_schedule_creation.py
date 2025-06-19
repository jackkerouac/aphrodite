#!/usr/bin/env python3
"""
Test schedule creation to verify UUID fixes
"""

import asyncio
import aiohttp
import json

async def test_schedule_creation():
    """Test creating a schedule"""
    
    base_url = "http://localhost:8000"
    
    # Test schedule data
    test_schedule = {
        "name": "Test Schedule",
        "timezone": "UTC",
        "cron_expression": "0 2 * * *",
        "badge_types": ["resolution", "audio"],
        "reprocess_all": False,
        "enabled": True,
        "target_libraries": []
    }
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Schedule Creation")
        print("=" * 40)
        
        # Create a schedule
        print("1. Creating test schedule...")
        try:
            async with session.post(
                f"{base_url}/api/v1/schedules",
                json=test_schedule,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Schedule created successfully!")
                    print(f"   📄 Response: {json.dumps(data, indent=2, default=str)}")
                    schedule_id = data.get('id')
                    print(f"   🆔 Schedule ID: {schedule_id}")
                    
                    # Test getting the schedule
                    if schedule_id:
                        print("\n2. Retrieving created schedule...")
                        async with session.get(f"{base_url}/api/v1/schedules/{schedule_id}") as get_response:
                            print(f"   Status: {get_response.status}")
                            if get_response.status == 200:
                                get_data = await get_response.json()
                                print(f"   ✅ Schedule retrieved successfully!")
                                print(f"   📄 Retrieved data: {json.dumps(get_data, indent=2, default=str)}")
                            else:
                                get_text = await get_response.text()
                                print(f"   ❌ Failed to retrieve: {get_text}")
                    
                    # Test listing schedules
                    print("\n3. Listing all schedules...")
                    async with session.get(f"{base_url}/api/v1/schedules") as list_response:
                        print(f"   Status: {list_response.status}")
                        if list_response.status == 200:
                            list_data = await list_response.json()
                            print(f"   ✅ Schedules listed successfully!")
                            print(f"   📊 Found {len(list_data)} schedules")
                        else:
                            list_text = await list_response.text()
                            print(f"   ❌ Failed to list: {list_text}")
                            
                    # Clean up - delete the test schedule
                    if schedule_id:
                        print(f"\n4. Cleaning up test schedule {schedule_id}...")
                        async with session.delete(f"{base_url}/api/v1/schedules/{schedule_id}") as delete_response:
                            print(f"   Status: {delete_response.status}")
                            if delete_response.status == 200:
                                print("   ✅ Test schedule deleted successfully!")
                            else:
                                delete_text = await delete_response.text()
                                print(f"   ⚠️  Failed to delete: {delete_text}")
                    
                else:
                    text = await response.text()
                    print(f"   ❌ Failed to create schedule: {text}")
                    
        except Exception as e:
            print(f"   ❌ Exception during creation: {e}")
        
        print("\n" + "=" * 40)
        print("🏁 Schedule creation test completed!")

if __name__ == "__main__":
    asyncio.run(test_schedule_creation())
