#!/usr/bin/env python3
"""
Test creating a schedule via API to make sure everything works
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import aiohttp

async def test_create_schedule():
    """Test creating a schedule"""
    
    base_url = "http://localhost:8000"
    
    test_schedule = {
        "name": "Test Daily Schedule",
        "timezone": "UTC",
        "cron_expression": "0 2 * * *",
        "badge_types": ["resolution", "audio"],
        "reprocess_all": False,
        "enabled": True,
        "target_libraries": []
    }
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing schedule creation...")
        
        try:
            async with session.post(
                f"{base_url}/api/v1/schedules",
                json=test_schedule,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    schedule = await response.json()
                    print(f"✅ Created schedule: {schedule['name']} (ID: {schedule['id'][:8]}...)")
                    
                    # Test getting the schedule
                    async with session.get(f"{base_url}/api/v1/schedules/{schedule['id']}") as get_response:
                        if get_response.status == 200:
                            retrieved = await get_response.json()
                            print(f"✅ Retrieved schedule: {retrieved['name']}")
                        else:
                            print(f"❌ Failed to retrieve schedule: HTTP {get_response.status}")
                    
                    # Clean up - delete the test schedule
                    async with session.delete(f"{base_url}/api/v1/schedules/{schedule['id']}") as delete_response:
                        if delete_response.status == 200:
                            print("✅ Test schedule deleted successfully")
                        else:
                            print(f"❌ Failed to delete test schedule: HTTP {delete_response.status}")
                    
                else:
                    print(f"❌ Failed to create schedule: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_create_schedule())
