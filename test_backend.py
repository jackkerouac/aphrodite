#!/usr/bin/env python3
import requests
import sys

def test_backend():
    base_url = "http://localhost:5000"
    
    print("Testing Flask backend...")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/api/test", timeout=5)
        print(f"✅ Backend is running: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False
    
    # Test if preview endpoints exist
    endpoints_to_test = [
        "/api/preview/badge-types",
        "/api/preview/poster-types"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {e}")
    
    return True

if __name__ == "__main__":
    test_backend()
