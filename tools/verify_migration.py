#!/usr/bin/env python3
# tools/verify_migration.py

import os
import sys
from pathlib import Path

# Add parent directory to path to import settings service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aphrodite-web'))

try:
    from app.services.settings_service import SettingsService
except ImportError as e:
    print(f"Error importing SettingsService: {e}")
    sys.exit(1)

def verify_migration(db_path):
    """Verify that migration was successful"""
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    settings_service = SettingsService(db_path)
    
    print(f"Verifying migration in database: {db_path}")
    print("=" * 50)
    
    # Check version
    version = settings_service.get_current_version()
    print(f"Database version: {version}")
    
    if version == 0:
        print("❌ No migration detected (version is 0)")
        return False
    
    # Check API keys
    print("\n📋 API Keys:")
    api_keys = settings_service.get_api_keys()
    for service, keys in api_keys.items():
        print(f"  {service}: {len(keys)} configuration(s)")
        for i, config in enumerate(keys):
            print(f"    Config {i}: {list(config.keys())}")
    
    # Check general settings
    print("\n⚙️  General Settings:")
    categories = ['tv_series', 'metadata_tagging', 'scheduler']
    for category in categories:
        settings = settings_service.get_settings_by_category(category)
        if settings:
            print(f"  {category}: {len(settings)} setting(s)")
            for key, value in settings.items():
                short_key = key.replace(f"{category}.", "")
                print(f"    {short_key}: {value}")
        else:
            print(f"  {category}: No settings")
    
    # Check badge settings
    print("\n🏷️  Badge Settings:")
    badge_types = ['audio', 'resolution', 'review', 'awards']
    for badge_type in badge_types:
        settings = settings_service.get_badge_settings(badge_type)
        if settings:
            print(f"  {badge_type}: {len(settings)} setting(s)")
            # Show just the top-level keys to avoid too much output
            for key in settings.keys():
                print(f"    {key}")
        else:
            print(f"  {badge_type}: No settings")
    
    print("\n✅ Migration verification complete!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Aphrodite settings migration")
    parser.add_argument("--db-path", default=None, help="Path to SQLite database file")
    
    args = parser.parse_args()
    
    if args.db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
    
    success = verify_migration(args.db_path)
    sys.exit(0 if success else 1)
