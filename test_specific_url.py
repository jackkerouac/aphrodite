#!/usr/bin/env python3
"""
Test the exact URL that should be working
"""

import requests

def test_specific_url():
    """Test the specific URL from the debug output"""
    
    # The URL from your debug output
    url = "http://localhost:8000/api/v1/static/preview/preview_4ada1470_jellyfin_ac6878ad821a3ade0185de92e38d45b4_285fe0f8.jpg"
    
    print("🧪 Testing Specific Preview URL")
    print("=" * 50)
    print(f"URL: {url}")
    
    try:
        # Test with different methods
        print("\n📋 HEAD Request:")
        head_response = requests.head(url, timeout=10)
        print(f"  Status: {head_response.status_code}")
        print(f"  Headers: {dict(head_response.headers)}")
        
        print("\n📋 GET Request:")
        get_response = requests.get(url, timeout=10)
        print(f"  Status: {get_response.status_code}")
        print(f"  Content Length: {len(get_response.content)} bytes")
        print(f"  Content Type: {get_response.headers.get('content-type')}")
        
        if get_response.status_code == 200:
            # Save the image to verify it's valid
            with open("test_download.jpg", "wb") as f:
                f.write(get_response.content)
            print(f"  ✅ Image saved as test_download.jpg")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_url()
