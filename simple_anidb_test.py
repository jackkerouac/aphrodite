#!/usr/bin/env python3
# simple_anidb_test.py - Check AniDB settings loading

import sys
import os
import yaml

def test_anidb_settings():
    print("🧪 Testing AniDB settings loading...")
    
    # Load settings file directly
    try:
        with open('settings.yaml', 'r') as f:
            settings = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return
    
    print(f"✅ Settings loaded successfully")
    
    # Check API keys structure
    api_keys = settings.get("api_keys", {})
    print(f"🔍 API keys available: {list(api_keys.keys())}")
    
    # Check AniDB specifically
    anidb_config = api_keys.get("aniDB", [])
    print(f"🔍 AniDB config type: {type(anidb_config)}")
    print(f"🔍 AniDB config length: {len(anidb_config)}")
    print(f"🔍 AniDB config: {anidb_config}")
    
    if anidb_config:
        anidb_settings = anidb_config[0] if isinstance(anidb_config, list) else anidb_config
        print(f"🔍 AniDB settings: {anidb_settings}")
        print(f"🔍 AniDB client_name: {anidb_settings.get('client_name', 'Not found')}")
        print(f"🔍 AniDB username: {anidb_settings.get('username', 'Not found')}")
    else:
        print("❌ No AniDB configuration found")

if __name__ == "__main__":
    test_anidb_settings()
