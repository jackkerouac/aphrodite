#!/usr/bin/env python3
"""
Test consecutive preview generations to identify the file naming issue
"""

import requests
import json
import time
from pathlib import Path

def test_consecutive_previews():
    """Test multiple preview generations in sequence"""
    
    base_url = "http://localhost:8000"
    preview_dir = Path("E:/programming/aphrodite/api/static/preview")
    
    print("🔍 Testing Consecutive Preview Generations")
    print("=" * 50)
    
    for i in range(1, 4):
        print(f"\n🧪 Generation #{i}")
        print("-" * 25)
        
        # Check files before
        before_files = set(f.name for f in preview_dir.glob("*") if f.is_file())
        
        # Generate preview
        payload = {"badgeTypes": ["audio", "resolution"]}
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/preview/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            print(f"📋 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                poster_url = data.get('posterUrl', '')
                print(f"📦 Poster URL: {poster_url}")
                
                # Extract filename from URL
                url_filename = poster_url.split('/')[-1] if poster_url else ''
                print(f"📝 URL Filename: {url_filename}")
                
                # Check what files were actually created
                after_files = set(f.name for f in preview_dir.glob("*") if f.is_file())
                new_files = after_files - before_files
                
                print(f"📁 New files created: {list(new_files)}")
                
                # Check if URL filename matches created file
                if url_filename in new_files:
                    print("✅ URL filename matches created file")
                    
                    # Test if file is accessible
                    try:
                        test_response = requests.head(poster_url, timeout=10)
                        print(f"🌐 URL accessibility: {test_response.status_code}")
                    except Exception as e:
                        print(f"❌ URL test failed: {e}")
                else:
                    print("❌ URL filename does NOT match created files!")
                    print(f"Expected: {url_filename}")
                    print(f"Created: {list(new_files)}")
                    
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait between tests
        if i < 3:
            print("⏳ Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n🏁 Test completed")

if __name__ == "__main__":
    test_consecutive_previews()
