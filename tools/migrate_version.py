#!/usr/bin/env python3
"""
Migration script to move version information from YAML files to SQLite database.
This script will:
1. Read the current version from version.yml
2. Store it in the app_version table in the database
3. Optionally backup the existing version files
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime

def find_root_directory():
    """Find the root directory of the Aphrodite installation"""
    # Start with the current directory
    current_dir = Path(os.path.abspath(__file__)).parent
    
    # Check if this is the root directory
    if os.path.exists(current_dir / 'version.yml'):
        return current_dir
    
    # Check parent directories
    for _ in range(3):  # Look up to 3 levels
        parent_dir = current_dir.parent
        if os.path.exists(parent_dir / 'version.yml'):
            return parent_dir
        current_dir = parent_dir
    
    # Fall back to the current directory
    return Path(os.path.abspath(__file__)).parent

def migrate_version_to_database(base_dir, db_path=None, backup=False, verbose=False):
    """Migrate version information from YAML to database"""
    
    print(f"Migrating version information from {base_dir}")
    
    # Import settings service
    sys.path.append(str(base_dir))
    try:
        from app.services.settings_service import SettingsService
    except ImportError:
        print("Error: Failed to import SettingsService")
        print("Make sure you're running this script from the Aphrodite directory")
        return False
    
    # Determine database path
    if db_path is None:
        db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize settings service
    settings_service = SettingsService(db_path)
    
    # Check if version info already exists in database
    existing_version_info = settings_service.get_app_version_info()
    if existing_version_info:
        print(f"Database already contains version info: {existing_version_info['current_version']}")
        return True
    
    # Read version from YAML files
    version_files = [
        base_dir / 'version.yml',
        base_dir / 'config' / 'version.yml'
    ]
    
    current_version = None
    version_file_used = None
    
    for version_file in version_files:
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    version_data = yaml.safe_load(f)
                    current_version = version_data.get('version')
                    version_file_used = version_file
                    if verbose:
                        print(f"Found version {current_version} in {version_file}")
                    break
            except Exception as e:
                if verbose:
                    print(f"Error reading {version_file}: {e}")
                continue
    
    if not current_version:
        print("Error: No version found in YAML files")
        return False
    
    # Check for existing version cache file
    cache_file = base_dir / 'version_cache.json'
    version_cache_data = None
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                version_cache_data = cache_data.get('data', {})
                if verbose:
                    print(f"Found cached version data: {version_cache_data}")
        except Exception as e:
            if verbose:
                print(f"Error reading version cache: {e}")
    
    # Create version info for database
    version_info = {
        'current_version': current_version,
        'latest_version': version_cache_data.get('latest_version') if version_cache_data else None,
        'update_available': version_cache_data.get('update_available', False) if version_cache_data else False,
        'release_notes': version_cache_data.get('release_notes') if version_cache_data else None,
        'release_url': version_cache_data.get('release_url') if version_cache_data else None,
        'published_at': version_cache_data.get('published_at') if version_cache_data else None,
        'check_successful': version_cache_data.get('check_successful', False) if version_cache_data else False,
        'error': version_cache_data.get('error') if version_cache_data else None,
        'last_checked': version_cache_data.get('last_checked', datetime.now().isoformat()) if version_cache_data else datetime.now().isoformat()
    }
    
    # Store in database
    try:
        settings_service.set_app_version_info(version_info)
        print(f"Successfully migrated version {current_version} to database")
        
        if verbose:
            print(f"Version info stored: {version_info}")
        
    except Exception as e:
        print(f"Error storing version in database: {e}")
        return False
    
    # Create backups if requested
    if backup:
        backup_dir = base_dir / 'backups' / 'version'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup version files
        import shutil
        if version_file_used and version_file_used.exists():
            backup_file = backup_dir / f"{version_file_used.name}.bak"
            shutil.copy2(version_file_used, backup_file)
            print(f"Created backup of {version_file_used.name} at {backup_file}")
        
        # Backup cache file
        if cache_file.exists():
            backup_cache = backup_dir / "version_cache.json.bak"
            shutil.copy2(cache_file, backup_cache)
            print(f"Created backup of version_cache.json at {backup_cache}")
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Migrate Aphrodite version information from YAML to SQLite")
    parser.add_argument("--yaml-dir", help="Directory containing YAML files")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    parser.add_argument("--backup", action="store_true", help="Create backups of YAML files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Find root directory
    if args.yaml_dir:
        base_dir = Path(args.yaml_dir)
    else:
        base_dir = find_root_directory()
    
    # Check if version.yml exists
    version_file = base_dir / 'version.yml'
    config_version_file = base_dir / 'config' / 'version.yml'
    
    if not version_file.exists() and not config_version_file.exists():
        print(f"Error: No version.yml file found in {base_dir} or {base_dir / 'config'}")
        sys.exit(1)
    
    print(f"Using base directory: {base_dir}")
    
    # Migrate version information
    success = migrate_version_to_database(
        base_dir, 
        args.db_path, 
        args.backup, 
        args.verbose
    )
    
    if success:
        print("\nVersion migration completed successfully!")
        print("The version information is now stored in the SQLite database.")
        print("The version system will now use the database instead of YAML files.")
        sys.exit(0)
    else:
        print("\nVersion migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
