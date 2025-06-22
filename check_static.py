#!/usr/bin/env python3
"""
Check preview files and static serving
"""

import os
import requests
from pathlib import Path

def check_preview_files():
    """Check what preview files exist"""
    
    preview_dir = Path("E:/programming/aphrodite/api/static/preview")
    
    print("🔍 Checking Preview Files")
    print("=" * 40)
    print(f"Preview directory: {preview_dir}")
    print(f"Directory exists: {preview_dir.exists()}")
    
    if preview_dir.exists():
        files = list(preview_dir.glob("*"))
        print(f"Files in directory: {len(files)}")
        
        for file in files[-10:]:  # Show last 10 files
            stat = file.stat()
            size_mb = stat.st_size / 1024 / 1024
            print(f"  {file.name} ({size_mb:.2f} MB)")
            
            # Test if this file is accessible via HTTP
            filename = file.name
            url = f"http://localhost:8000/api/v1/static/preview/{filename}"
            
            try:
                response = requests.head(url, timeout=5)
                print(f"    HTTP Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"    Error: {response.text}")
            except Exception as e:
                print(f"    HTTP Error: {e}")
    
    print("\n" + "=" * 40)

def test_static_routes():
    """Test different static routes"""
    
    base_url = "http://localhost:8000"
    
    routes_to_test = [
        "/api/v1/static/",
        "/api/v1/static/preview/",
        "/api/v1/static/processed/",
    ]
    
    print("🌐 Testing Static Routes")
    print("=" * 40)
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            print(f"{route}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}")
        except Exception as e:
            print(f"{route}: Error - {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    check_preview_files()
    test_static_routes()
