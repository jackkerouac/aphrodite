# tools/migrate_settings.py

import os
import sys
import yaml
import json
from pathlib import Path
import sqlite3

# Add parent directory to path to import settings service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aphrodite-web'))

try:
    from app.services.settings_service import SettingsService
except ImportError as e:
    print(f"Error importing SettingsService: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)

def migrate_yaml_to_sqlite(yaml_dir, db_path, interactive=True):
    """Migrate settings from YAML files to SQLite database"""
    print(f"Migrating settings from {yaml_dir} to {db_path}")
    
    # Initialize settings service
    settings_service = SettingsService(db_path)
    
    # Check if the database already has settings
    current_version = settings_service.get_current_version()
    if current_version > 0:
        if interactive:
            confirm = input("Database already contains settings. Overwrite? (y/N): ")
            if confirm.lower() != 'y':
                print("Migration aborted.")
                return False
        else:
            print("Database already contains settings. Skipping migration.")
            return False
    
    # Load main settings.yaml
    settings_path = os.path.join(yaml_dir, 'settings.yaml')
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading settings.yaml: {e}")
        return False
    
    # Migrate API keys
    if 'api_keys' in settings:
        api_keys = settings['api_keys']
        for service, service_keys in api_keys.items():
            if isinstance(service_keys, list):
                settings_service.update_api_keys(service, service_keys)
                print(f"Migrated {service} API keys")
            else:
                # Handle non-list format (unexpected)
                print(f"Warning: Unexpected format for {service} API keys")
    
    # Migrate other settings categories
    categories = [
        'tv_series',
        'metadata_tagging',
        'scheduler'
    ]
    
    for category in categories:
        if category in settings:
            settings_service.import_from_yaml(settings, category)
            print(f"Migrated {category} settings")
    
    # Migrate badge settings
    badge_files = {
        'audio': 'badge_settings_audio.yml',
        'resolution': 'badge_settings_resolution.yml',
        'review': 'badge_settings_review.yml',
        'awards': 'badge_settings_awards.yml'
    }
    
    for badge_type, filename in badge_files.items():
        badge_path = os.path.join(yaml_dir, filename)
        if os.path.exists(badge_path):
            try:
                with open(badge_path, 'r') as f:
                    badge_settings = yaml.safe_load(f)
                settings_service.update_badge_settings(badge_type, badge_settings)
                print(f"Migrated {badge_type} badge settings")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    # Set the version to 1 to indicate successful migration
    settings_service.set_version(1)
    
    print("Migration completed successfully!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Aphrodite settings from YAML to SQLite")
    parser.add_argument("--yaml-dir", default=None, help="Directory containing YAML files")
    parser.add_argument("--db-path", default=None, help="Path to SQLite database file")
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompts")
    
    args = parser.parse_args()
    
    # Determine default paths
    if args.yaml_dir is None:
        # Use the parent directory (where settings.yaml should be)
        args.yaml_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if args.db_path is None:
        # Use the default database path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    success = migrate_yaml_to_sqlite(args.yaml_dir, args.db_path, not args.non_interactive)
    sys.exit(0 if success else 1)
