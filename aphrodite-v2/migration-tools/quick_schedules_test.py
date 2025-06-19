#!/usr/bin/env python3
"""
Quick API test to verify schedules endpoints are working
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import aiohttp


async def quick_test():
    """Quick test of the schedules API"""
    
    base_url = "http://localhost:8000"
    
    print(f"🧪 Quick test of schedules API at {base_url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test if API server is running
            print("\n1. Testing API server connection...")
            try:
                async with session.get(f"{base_url}/health") as response:
                    if response.status == 200:
                        print("   ✅ API server is running")
                    else:
                        print(f"   ⚠️  API server responded with status {response.status}")
            except Exception as e:
                print(f"   ❌ Cannot connect to API server: {e}")
                print("   Make sure the API server is running with: python main.py")
                return
            
            # Test badge types endpoint
            print("\n2. Testing badge types endpoint...")
            try:
                async with session.get(f"{base_url}/api/v1/schedules/config/badge-types") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Badge types: {data.get('badge_types', [])}")
                    else:
                        print(f"   ❌ Badge types failed: HTTP {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text[:200]}...")
            except Exception as e:
                print(f"   ❌ Badge types error: {e}")
            
            # Test get schedules endpoint
            print("\n3. Testing schedules list endpoint...")
            try:
                async with session.get(f"{base_url}/api/v1/schedules") as response:
                    if response.status == 200:
                        schedules = await response.json()
                        print(f"   ✅ Schedules endpoint works: {len(schedules)} schedules found")
                    else:
                        print(f"   ❌ Schedules failed: HTTP {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text[:200]}...")
            except Exception as e:
                print(f"   ❌ Schedules error: {e}")
            
            # Test cron presets endpoint
            print("\n4. Testing cron presets endpoint...")
            try:
                async with session.get(f"{base_url}/api/v1/schedules/config/cron-presets") as response:
                    if response.status == 200:
                        data = await response.json()
                        presets = data.get('presets', {})
                        print(f"   ✅ Cron presets: {len(presets)} presets available")
                    else:
                        print(f"   ❌ Cron presets failed: HTTP {response.status}")
            except Exception as e:
                print(f"   ❌ Cron presets error: {e}")
            
            print("\n🏁 Quick test completed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(quick_test())
        print("\n✅ Test script completed!")
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
