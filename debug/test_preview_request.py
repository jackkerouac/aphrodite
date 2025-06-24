#!/usr/bin/env python3
"""
Debug script to test the preview generation API directly
"""

import requests
import json

# Test the badge types endpoint first
print("🔍 Testing badge types endpoint...")
try:
    response = requests.get("http://localhost:8000/api/v1/preview/badge-types")
    print(f"Badge types response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Badge types data: {json.dumps(data, indent=2)}")
    else:
        print(f"Badge types error: {response.text}")
except Exception as e:
    print(f"Badge types request failed: {e}")

print("\n" + "="*50 + "\n")

# Test the preview generation with all badges
print("🎨 Testing preview generation with ALL badges...")
try:
    request_data = {
        "badgeTypes": ["audio", "resolution", "review", "awards"]
    }
    
    print(f"Request data: {json.dumps(request_data, indent=2)}")
    
    response = requests.post(
        "http://localhost:8000/api/v1/preview/generate",
        headers={"Content-Type": "application/json"},
        json=request_data
    )
    
    print(f"Preview generation response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Preview generation data: {json.dumps(data, indent=2)}")
    else:
        print(f"Preview generation error: {response.text}")
        
except Exception as e:
    print(f"Preview generation request failed: {e}")

print("\n" + "="*50 + "\n")

# Test with just audio badge
print("🎵 Testing preview generation with ONLY audio badge...")
try:
    request_data = {
        "badgeTypes": ["audio"]
    }
    
    print(f"Request data: {json.dumps(request_data, indent=2)}")
    
    response = requests.post(
        "http://localhost:8000/api/v1/preview/generate",
        headers={"Content-Type": "application/json"},
        json=request_data
    )
    
    print(f"Audio only response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Audio only data: {json.dumps(data, indent=2)}")
    else:
        print(f"Audio only error: {response.text}")
        
except Exception as e:
    print(f"Audio only request failed: {e}")
