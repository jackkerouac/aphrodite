#!/usr/bin/env python3
"""
Debug preview generation URLs
"""

import requests
import json
from pathlib import Path
import os
from datetime import datetime

def debug_preview_generation():
    """Debug what happens during preview generation"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Debug: Preview Generation URLs")
    print("=" * 50)
    
    # Check current preview files before generation
    preview_dir = Path("E:/programming/aphrodite/api/static/preview")
    before_files = set(f.name for f in preview_dir.glob("*") if f.is_file())
    print(f"Files before generation: {len(before_files)}")
    
    # Generate preview
    payload = {"badgeTypes": ["audio", "resolution"]}
    
    try:
        print("📤 Sending preview generation request...")
        response = requests.post(
            f"{base_url}/api/v1/preview/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📋 Response Data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
            
            # Check what files were created
            after_files = set(f.name for f in preview_dir.glob("*") if f.is_file())
            new_files = after_files - before_files
            
            print(f"\n📁 New files created: {len(new_files)}")
            for filename in new_files:
                file_path = preview_dir / filename
                stat = file_path.stat()
                size_mb = stat.st_size / 1024 / 1024
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"  {filename} ({size_mb:.2f} MB, {mod_time})")
            
            # Test the specific URL returned
            poster_url = data.get('posterUrl')
            if poster_url:
                print(f"\n🌐 Testing returned URL: {poster_url}")
                try:
                    url_response = requests.head(poster_url, timeout=10)
                    print(f"  Status: {url_response.status_code}")
                    print(f"  Content-Type: {url_response.headers.get('content-type')}")
                    print(f"  Content-Length: {url_response.headers.get('content-length')}")
                    
                    if url_response.status_code == 200:
                        print("  ✅ URL is accessible")
                    else:
                        print(f"  ❌ URL returned error: {url_response.status_code}")
                        
                        # Try to get the actual response
                        full_response = requests.get(poster_url, timeout=10)
                        print(f"  Full response: {full_response.text[:200]}")
                        
                except Exception as e:
                    print(f"  ❌ Error testing URL: {e}")
            else:
                print("  ⚠️ No posterUrl in response")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_preview_generation()
