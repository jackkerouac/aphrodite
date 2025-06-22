#!/usr/bin/env python3
"""
Test script for preview API endpoint
"""

import requests
import json
import sys
from typing import Dict, Any

def test_preview_generation():
    """Test the preview generation endpoint"""
    
    # API configuration
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/preview/generate"
    
    # Test payload
    payload = {
        "badgeTypes": ["audio", "resolution"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Preview Generation API")
    print(f"📍 Endpoint: {endpoint}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print("-" * 50)
        
        # Parse response
        try:
            response_data = response.json()
            print(f"📝 Response JSON:")
            print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response")
            print(f"📝 Raw Response: {response.text}")
            
        print("-" * 50)
        
        # Check if successful
        if response.status_code == 200:
            if response_data.get('success'):
                print("✅ Preview generation successful!")
                
                # Check for poster URL
                poster_url = response_data.get('posterUrl')
                if poster_url:
                    print(f"🖼️ Poster URL: {poster_url}")
                    
                    # Test if poster URL is accessible
                    try:
                        poster_response = requests.head(poster_url, timeout=10)
                        print(f"🔍 Poster URL Status: {poster_response.status_code}")
                        print(f"📏 Content Length: {poster_response.headers.get('content-length', 'Unknown')}")
                        print(f"📄 Content Type: {poster_response.headers.get('content-type', 'Unknown')}")
                    except Exception as e:
                        print(f"❌ Failed to check poster URL: {e}")
                else:
                    print("⚠️ No poster URL in response")
                    
                applied_badges = response_data.get('appliedBadges', [])
                processing_time = response_data.get('processingTime', 0)
                
                print(f"🏷️ Applied Badges: {applied_badges}")
                print(f"⏱️ Processing Time: {processing_time:.2f}s")
                
            else:
                print(f"❌ API returned success=false: {response_data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_badge_types():
    """Test the badge types endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/preview/badge-types"
    
    print("\n🧪 Testing Badge Types API")
    print(f"📍 Endpoint: {endpoint}")
    print("-" * 50)
    
    try:
        response = requests.get(endpoint, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📝 Available Badge Types:")
            for badge_type in data.get('badgeTypes', []):
                print(f"  • {badge_type.get('id')}: {badge_type.get('name')} - {badge_type.get('description')}")
        else:
            print(f"❌ Failed to get badge types: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing badge types: {e}")

if __name__ == "__main__":
    print("🚀 Starting Preview API Tests")
    print("=" * 50)
    
    # Test badge types first
    test_badge_types()
    
    # Test preview generation
    test_preview_generation()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed")
