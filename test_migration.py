#!/usr/bin/env python3

import os
import sys
import yaml

# Add paths for imports
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'aphrodite-web'))

try:
    from app.services.settings_service import SettingsService
    print("Successfully imported SettingsService")
except ImportError as e:
    print(f"Error importing SettingsService: {e}")
    sys.exit(1)

# Initialize settings service
db_path = os.path.join(root_dir, 'data', 'aphrodite.db')
print(f"Using database path: {db_path}")

settings_service = SettingsService(db_path)

# Check current version
current_version = settings_service.get_current_version()
print(f"Current database version: {current_version}")

# Load settings.yaml
settings_path = os.path.join(root_dir, 'settings.yaml')
print(f"Loading settings from: {settings_path}")

try:
    with open(settings_path, 'r') as f:
        settings = yaml.safe_load(f)
    print("Successfully loaded settings.yaml")
    print(f"API keys found: {list(settings.get('api_keys', {}).keys())}")
except Exception as e:
    print(f"Error loading settings.yaml: {e}")
    sys.exit(1)

# If version is 0, run migration
if current_version == 0:
    print("Running migration...")
    
    # Migrate API keys
    if 'api_keys' in settings:
        api_keys = settings['api_keys']
        for service, service_keys in api_keys.items():
            print(f"Migrating {service} API keys...")
            if isinstance(service_keys, list):
                settings_service.update_api_keys(service, service_keys)
                print(f"Successfully migrated {service} API keys")
            else:
                print(f"Warning: Unexpected format for {service} API keys")
    
    # Migrate other settings categories
    categories = ['tv_series', 'metadata_tagging', 'scheduler']
    
    for category in categories:
        if category in settings:
            print(f"Migrating {category} settings...")
            settings_service.import_from_yaml(settings, category)
            print(f"Successfully migrated {category} settings")
    
    # Set version to 1
    settings_service.set_version(1)
    print("Migration completed successfully!")
else:
    print("Database already has settings, skipping migration")

# Verify the migration worked
print("\nVerifying migration...")
new_version = settings_service.get_current_version()
print(f"New database version: {new_version}")

# Test retrieving some settings
api_keys = settings_service.get_api_keys()
print(f"API keys in database: {list(api_keys.keys())}")

print("Migration test completed!")
