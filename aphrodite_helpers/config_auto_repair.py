#!/usr/bin/env python3
# aphrodite_helpers/config_auto_repair.py

import yaml
import os
from pathlib import Path
from typing import Dict, Any

def get_default_settings_structure() -> Dict[str, Any]:
    """Return the complete default settings structure with all required sections."""
    return {
        "api_keys": {
            "Jellyfin": [
                {
                    "url": "https://your-jellyfin-server.com",
                    "api_key": "YOUR_JELLYFIN_API_KEY", 
                    "user_id": "YOUR_JELLYFIN_USER_ID"
                }
            ],
            "OMDB": [
                {
                    "api_key": "YOUR_OMDB_API_KEY",
                    "cache_expiration": 60
                }
            ],
            "TMDB": [
                {
                    "api_key": "YOUR_TMDB_API_KEY",
                    "cache_expiration": 60,
                    "language": "en",
                    "region": "US"
                }
            ],
            "aniDB": [
                {
                    "username": "YOUR_ANIDB_USERNAME",
                    "password": "YOUR_ANIDB_PASSWORD",
                    "version": 5,
                    "client_name": "aphrodite",
                    "language": "en",
                    "cache_expiration": 60
                }
            ]
        },
        "tv_series": {
            "show_dominant_badges": True,
            "max_episodes_to_analyze": 5,
            "episode_timeout": 25
        },
        "metadata_tagging": {
            "enabled": True,
            "tag_name": "aphrodite-overlay",
            "tag_on_success_only": True
        },
        "scheduler": {
            "enabled": True,
            "timezone": "UTC",
            "max_concurrent_jobs": 1,
            "job_history_limit": 50
        }
    }

def deep_merge_settings(existing: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge existing settings with defaults, preserving existing values
    but adding any missing sections or keys.
    """
    result = existing.copy()
    
    for key, default_value in defaults.items():
        if key not in result:
            # Key is completely missing, add the entire default
            result[key] = default_value
            print(f"✅ Added missing settings section: {key}")
        elif isinstance(default_value, dict) and isinstance(result[key], dict):
            # Both are dictionaries, merge recursively
            result[key] = deep_merge_settings(result[key], default_value)
        elif isinstance(default_value, list) and isinstance(result[key], list):
            # Handle list merging (for API keys structure)
            if key == "Jellyfin" or key == "OMDB" or key == "TMDB" or key == "aniDB":
                # For API keys, ensure we have at least one entry with all required fields
                if len(result[key]) == 0:
                    result[key] = default_value
                    print(f"✅ Added default {key} API configuration")
                else:
                    # Merge missing fields into existing entries
                    for i, entry in enumerate(result[key]):
                        if isinstance(entry, dict) and isinstance(default_value[0], dict):
                            for default_field, default_val in default_value[0].items():
                                if default_field not in entry:
                                    entry[default_field] = default_val
                                    print(f"✅ Added missing field '{default_field}' to {key} configuration")
        # If existing value exists and types don't match or it's a simple value, keep existing
    
    return result

def validate_and_repair_settings(settings_path: str = "settings.yaml") -> bool:
    """
    Validate the settings file and repair any missing sections or keys.
    
    Args:
        settings_path: Path to the settings file
        
    Returns:
        bool: True if settings are valid/repaired, False if critical error
    """
    # Determine the correct path
    if not os.path.isabs(settings_path):
        # If relative path, look relative to the script's directory
        script_dir = Path(__file__).parent.parent
        full_path = script_dir / settings_path
    else:
        full_path = Path(settings_path)
    
    print(f"🔧 Validating settings file: {full_path}")
    
    # Get default structure
    defaults = get_default_settings_structure()
    
    # Load existing settings or start with empty dict
    existing_settings = {}
    if full_path.exists():
        try:
            with open(full_path, 'r') as f:
                existing_settings = yaml.safe_load(f) or {}
            print(f"📖 Loaded existing settings with {len(existing_settings)} top-level sections")
        except yaml.YAMLError as e:
            print(f"❌ Error parsing existing settings: {e}")
            print("🔧 Creating new settings file from defaults")
            existing_settings = {}
        except Exception as e:
            print(f"❌ Error reading settings file: {e}")
            return False
    else:
        print(f"📝 Settings file not found, creating new one")
    
    # Merge with defaults
    print(f"🔧 Merging settings with defaults...")
    repaired_settings = deep_merge_settings(existing_settings, defaults)
    
    # Check if anything changed
    settings_changed = repaired_settings != existing_settings
    
    if settings_changed:
        print(f"💾 Settings were modified, saving updated file...")
        try:
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the repaired settings
            with open(full_path, 'w') as f:
                yaml.dump(repaired_settings, f, default_flow_style=False, sort_keys=False, indent=2)
            
            print(f"✅ Settings file successfully repaired and saved")
            
            # Log what sections exist now
            sections = list(repaired_settings.keys())
            print(f"📋 Settings now contains sections: {', '.join(sections)}")
            
            # Validate key sections
            if 'tv_series' in repaired_settings:
                tv_settings = repaired_settings['tv_series']
                show_dominant = tv_settings.get('show_dominant_badges', False)
                print(f"📺 TV series dominant badges: {show_dominant}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing repaired settings: {e}")
            return False
    else:
        print(f"✅ Settings file is already complete, no changes needed")
        
        # Still log current state for debugging
        sections = list(repaired_settings.keys())
        print(f"📋 Current settings sections: {', '.join(sections)}")
        
        if 'tv_series' in repaired_settings:
            tv_settings = repaired_settings['tv_series']
            show_dominant = tv_settings.get('show_dominant_badges', False)
            print(f"📺 TV series dominant badges: {show_dominant}")
        
        return True

def repair_settings_cli():
    """Command line interface for settings repair."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate and repair Aphrodite settings file")
    parser.add_argument("--settings-path", "-s", default="settings.yaml", 
                       help="Path to settings file (default: settings.yaml)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("🔧 Starting settings validation and repair...")
    
    success = validate_and_repair_settings(args.settings_path)
    
    if success:
        print("✅ Settings validation and repair completed successfully")
        exit(0)
    else:
        print("❌ Settings validation and repair failed")
        exit(1)

if __name__ == "__main__":
    repair_settings_cli()
