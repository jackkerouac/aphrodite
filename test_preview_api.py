import requests
import json

def test_preview_endpoints():
    base_url = "http://localhost:5000"
    
    # Test the basic API
    try:
        response = requests.get(f"{base_url}/api/test")
        print(f"API Test: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"API Test failed: {e}")
    
    # Test preview badge types
    try:
        response = requests.get(f"{base_url}/api/preview/badge-types")
        print(f"Badge Types: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Badge Types failed: {e}")
    
    # Test preview poster types
    try:
        response = requests.get(f"{base_url}/api/preview/poster-types")
        print(f"Poster Types: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Poster Types failed: {e}")

if __name__ == "__main__":
    test_preview_endpoints()
