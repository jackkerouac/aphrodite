#!/usr/bin/env python3
"""
Test script to verify the settings fix is working correctly.

This script tests:
1. Backend system config GET endpoint
2. Backend system config PUT endpoint  
3. Database storage verification
4. Frontend API settings loading (simulated)
"""

import aiohttp
import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

API_BASE_URL = "http://localhost:8000"

async def test_system_config_endpoints():
    """Test the system config endpoints"""
    print("=" * 60)
    print("TESTING APHRODITE V2 SETTINGS FIX")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: GET system config (should work even if empty)
        print("\n1. Testing GET /api/v1/config/system")
        print("-" * 40)
        try:
            async with session.get(f"{API_BASE_URL}/api/v1/config/system") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    print("   ✅ GET system config - SUCCESS")
                else:
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
                    print("   ❌ GET system config - FAILED")
        except Exception as e:
            print(f"   ❌ GET system config - ERROR: {e}")
        
        # Test 2: PUT system config with Jellyfin data
        print("\n2. Testing PUT /api/v1/config/system")
        print("-" * 40)
        test_config = {
            "jellyfin_url": "http://test-jellyfin.example.com",
            "jellyfin_api_key": "test-api-key-12345",
            "jellyfin_user_id": "test-user-id-67890"
        }
        
        try:
            async with session.put(
                f"{API_BASE_URL}/api/v1/config/system",
                headers={"Content-Type": "application/json"},
                json=test_config
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    print("   ✅ PUT system config - SUCCESS")
                else:
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
                    print("   ❌ PUT system config - FAILED")
        except Exception as e:
            print(f"   ❌ PUT system config - ERROR: {e}")
        
        # Test 3: GET system config again to verify data was saved
        print("\n3. Testing GET /api/v1/config/system (after save)")
        print("-" * 40)
        try:
            async with session.get(f"{API_BASE_URL}/api/v1/config/system") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    
                    # Verify the data was saved correctly
                    config = data.get("config", {})
                    if (config.get("jellyfin_url") == test_config["jellyfin_url"] and
                        config.get("jellyfin_api_key") == test_config["jellyfin_api_key"] and
                        config.get("jellyfin_user_id") == test_config["jellyfin_user_id"]):
                        print("   ✅ Data verification - SUCCESS")
                    else:
                        print("   ❌ Data verification - FAILED")
                        print(f"   Expected: {test_config}")
                        print(f"   Got: {config}")
                else:
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
                    print("   ❌ GET system config (verification) - FAILED")
        except Exception as e:
            print(f"   ❌ GET system config (verification) - ERROR: {e}")
        
        # Test 4: Test Jellyfin connection endpoint
        print("\n4. Testing POST /api/v1/config/test-jellyfin")
        print("-" * 40)
        jellyfin_test_data = {
            "url": "http://test-jellyfin.example.com",
            "api_key": "test-api-key-12345",
            "user_id": "test-user-id-67890"
        }
        
        try:
            async with session.post(
                f"{API_BASE_URL}/api/v1/config/test-jellyfin",
                headers={"Content-Type": "application/json"},
                json=jellyfin_test_data
            ) as response:
                print(f"   Status: {response.status}")
                data = await response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                if response.status in [200, 400, 408]:  # 400/408 expected for test server
                    print("   ✅ Jellyfin test endpoint - SUCCESS (endpoint working)")
                else:
                    print("   ❌ Jellyfin test endpoint - FAILED")
        except Exception as e:
            print(f"   ❌ Jellyfin test endpoint - ERROR: {e}")

        # Test 5: Verify CORS headers
        print("\n5. Testing CORS headers")
        print("-" * 40)
        try:
            async with session.options(f"{API_BASE_URL}/api/v1/config/system") as response:
                print(f"   Status: {response.status}")
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
                if cors_headers['Access-Control-Allow-Origin']:
                    print("   ✅ CORS headers - SUCCESS")
                else:
                    print("   ❌ CORS headers - FAILED")
        except Exception as e:
            print(f"   ❌ CORS test - ERROR: {e}")

async def test_frontend_simulation():
    """Simulate frontend API calls"""
    print("\n" + "=" * 60)
    print("SIMULATING FRONTEND API CALLS")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Simulate frontend loading settings
        print("\n6. Simulating frontend loadSettings()")
        print("-" * 40)
        try:
            async with session.get(f"{API_BASE_URL}/api/v1/config/system") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    config = data.get('config', {})
                    
                    # Simulate frontend processing
                    jellyfin_config = {
                        'url': config.get('jellyfin_url', ''),
                        'api_key': config.get('jellyfin_api_key', ''),
                        'user_id': config.get('jellyfin_user_id', '')
                    }
                    
                    print(f"   Frontend would load: {json.dumps(jellyfin_config, indent=2)}")
                    
                    if any(jellyfin_config.values()):
                        print("   ✅ Frontend load simulation - SUCCESS")
                    else:
                        print("   ⚠️  Frontend load simulation - NO DATA (expected if first run)")
                elif response.status == 404:
                    print("   ⚠️  No config found - frontend would use defaults")
                else:
                    print(f"   ❌ Frontend load simulation - HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Frontend load simulation - ERROR: {e}")
        
        # Simulate frontend saving settings
        print("\n7. Simulating frontend saveSettings()")
        print("-" * 40)
        frontend_save_data = {
            "jellyfin_url": "http://frontend-test.example.com",
            "jellyfin_api_key": "frontend-test-key",
            "jellyfin_user_id": "frontend-test-user"
        }
        
        try:
            async with session.put(
                f"{API_BASE_URL}/api/v1/config/system",
                headers={"Content-Type": "application/json"},
                json=frontend_save_data
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    print("   ✅ Frontend save simulation - SUCCESS")
                else:
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
                    print("   ❌ Frontend save simulation - FAILED")
        except Exception as e:
            print(f"   ❌ Frontend save simulation - ERROR: {e}")

async def run_all_tests():
    """Run all tests"""
    print("Starting Aphrodite v2 Settings Fix Test Suite...")
    print(f"Testing API at: {API_BASE_URL}")
    
    try:
        await test_system_config_endpoints()
        await test_frontend_simulation()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("\nIf you see ✅ SUCCESS messages above, the settings fix is working!")
        print("\nNext steps:")
        print("1. Test in browser: http://192.168.0.110:3000/settings")
        print("2. Go to API tab and verify Jellyfin fields load")
        print("3. Test save functionality")
        print("4. Check Poster Manager works: http://192.168.0.110:3000/poster-manager")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)
