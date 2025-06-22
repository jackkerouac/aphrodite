#!/usr/bin/env python3
"""
Debug script for preview generation after settings changes
"""

import requests
import json
import time

def test_preview_generation_debug():
    """Test preview generation with detailed debugging"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Debug: Preview Generation After Settings Changes")
    print("=" * 60)
    
    # Test multiple generations to see if issue is persistent
    for i in range(1, 4):
        print(f"\n🧪 Test Run #{i}")
        print("-" * 30)
        
        payload = {
            "badgeTypes": ["audio", "resolution", "review"]
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/preview/generate", 
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data.get('success')}")
                print(f"Message: {data.get('message')}")
                print(f"Poster URL: {data.get('posterUrl')}")
                print(f"Applied Badges: {data.get('appliedBadges')}")
                print(f"Processing Time: {data.get('processingTime'):.2f}s")
                
                # Test if poster URL is accessible
                if data.get('posterUrl'):
                    try:
                        poster_response = requests.head(data['posterUrl'], timeout=10)
                        print(f"Poster URL Accessible: {poster_response.status_code == 200}")
                        if poster_response.status_code == 200:
                            print(f"Content Type: {poster_response.headers.get('content-type')}")
                            print(f"Content Length: {poster_response.headers.get('content-length')}")
                        else:
                            print(f"❌ Poster URL returned status: {poster_response.status_code}")
                    except Exception as e:
                        print(f"❌ Error checking poster URL: {e}")
                else:
                    print("⚠️ No poster URL returned")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait between tests
        if i < 3:
            print("⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🏁 Debug tests completed")

def check_static_file_access():
    """Check if static files are accessible"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing Static File Access")
    print("-" * 30)
    
    # Test the static route itself
    try:
        response = requests.get(f"{base_url}/api/v1/static/", timeout=10)
        print(f"Static route status: {response.status_code}")
    except Exception as e:
        print(f"Static route error: {e}")
    
    # Check if preview directory is accessible
    try:
        response = requests.get(f"{base_url}/api/v1/static/preview/", timeout=10)
        print(f"Preview directory status: {response.status_code}")
    except Exception as e:
        print(f"Preview directory error: {e}")

if __name__ == "__main__":
    test_preview_generation_debug()
    check_static_file_access()
