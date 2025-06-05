#!/usr/bin/env python3
"""
Enhanced Command-line Migration Tool for Aphrodite SQLite Migration

This tool provides comprehensive migration functionality including:
- Migration from YAML to SQLite
- Backup and restore capabilities  
- Status checking and verification
- Rollback functionality
- Non-interactive and verbose modes
"""

import os
import sys
import argparse
import yaml
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import settings service
parent_dir = Path(os.path.abspath(__file__)).parent.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / 'aphrodite-web'))

try:
    from app.services.settings_service import SettingsService
except ImportError as e:
    print(f"Error importing SettingsService: {e}")
    print("Make sure you're running this script from the Aphrodite root directory")
    sys.exit(1)

class MigrationCLI:
    """Enhanced command-line interface for settings migration"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.yaml_dir = None
        self.db_path = None
        self.backup_dir = None
        
    def log(self, message, force=False):
        """Log message if verbose mode is enabled or force is True"""
        if self.verbose or force:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def find_root_directory(self):
        """Find the root directory of the Aphrodite installation"""
        # Start with the current directory
        current_dir = Path(os.getcwd())
        
        # Check if this is the root directory
        if (current_dir / 'settings.yaml').exists():
            return current_dir
        
        # Check parent directories up to 3 levels
        for _ in range(3):
            parent_dir = current_dir.parent
            if (parent_dir / 'settings.yaml').exists():
                return parent_dir
            current_dir = parent_dir
        
        # Check the script's parent directory
        script_parent = Path(os.path.abspath(__file__)).parent.parent
        if (script_parent / 'settings.yaml').exists():
            return script_parent
        
        # Fall back to the current directory
        return Path(os.getcwd())
    
    def setup_paths(self, yaml_dir=None, db_path=None):
        """Setup and validate file paths"""
        # Determine YAML directory
        if yaml_dir:
            self.yaml_dir = Path(yaml_dir)
        else:
            self.yaml_dir = self.find_root_directory()
        
        self.log(f"Using YAML directory: {self.yaml_dir}")
        
        # Determine database path
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = self.yaml_dir / 'data' / 'aphrodite.db'
        
        self.log(f"Using database path: {self.db_path}")
        
        # Setup backup directory
        self.backup_dir = self.yaml_dir / 'backups' / 'settings'
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        return True
    
    def check_status(self):
        """Check migration status"""
        print("=== Aphrodite Migration Status ===")
        
        # Check for YAML files
        settings_yaml = self.yaml_dir / 'settings.yaml'
        yaml_exists = settings_yaml.exists()
        
        print(f"YAML Files:")
        print(f"  settings.yaml: {'✓ Found' if yaml_exists else '✗ Not found'}")
        
        badge_files = ['badge_settings_audio.yml', 'badge_settings_resolution.yml', 
                      'badge_settings_review.yml', 'badge_settings_awards.yml']
        
        for badge_file in badge_files:
            badge_path = self.yaml_dir / badge_file
            print(f"  {badge_file}: {'✓ Found' if badge_path.exists() else '✗ Not found'}")
        
        # Check database status
        print(f"\nDatabase:")
        print(f"  Path: {self.db_path}")
        print(f"  Exists: {'✓ Yes' if os.path.exists(self.db_path) else '✗ No'}")
        
        if os.path.exists(self.db_path):
            try:
                settings_service = SettingsService(str(self.db_path))
                version = settings_service.get_current_version()
                print(f"  Version: {version}")
                
                if version > 0:
                    print("  Status: ✓ Migrated")
                    
                    # Count settings
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM settings")
                    settings_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM api_keys")
                    api_keys_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM badge_settings")
                    badge_count = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    print(f"  Settings: {settings_count}")
                    print(f"  API Keys: {api_keys_count}")
                    print(f"  Badge Settings: {badge_count}")
                else:
                    print("  Status: ✗ Not migrated")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Migration recommendation
        print(f"\nRecommendation:")
        if yaml_exists and (not os.path.exists(self.db_path) or 
                           SettingsService(str(self.db_path)).get_current_version() == 0):
            print("  ⚠ Migration needed - run with --migrate")
        elif os.path.exists(self.db_path) and SettingsService(str(self.db_path)).get_current_version() > 0:
            print("  ✓ Already migrated")
        else:
            print("  ℹ No YAML files found - appears to be a new installation")
        
        return True
    
    def create_backup(self, backup_name=None):
        """Create backup of YAML files"""
        if backup_name is None:
            backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
        
        backup_path = self.backup_dir / backup_name
        os.makedirs(backup_path, exist_ok=True)
        
        files_backed_up = []
        
        # Backup main settings
        settings_path = self.yaml_dir / 'settings.yaml'
        if settings_path.exists():
            shutil.copy2(settings_path, backup_path / 'settings.yaml')
            files_backed_up.append('settings.yaml')
            self.log(f"Backed up settings.yaml")
        
        # Backup badge settings
        badge_files = ['badge_settings_audio.yml', 'badge_settings_resolution.yml',
                      'badge_settings_review.yml', 'badge_settings_awards.yml']
        
        for badge_file in badge_files:
            badge_path = self.yaml_dir / badge_file
            if badge_path.exists():
                shutil.copy2(badge_path, backup_path / badge_file)
                files_backed_up.append(badge_file)
                self.log(f"Backed up {badge_file}")
        
        if files_backed_up:
            print(f"✓ Created backup: {backup_path}")
            print(f"  Files backed up: {', '.join(files_backed_up)}")
            return str(backup_path)
        else:
            print("✗ No files to backup")
            return None
    
    def list_backups(self):
        """List available backups"""
        if not self.backup_dir.exists():
            print("No backups directory found")
            return []
        
        backups = []
        for item in self.backup_dir.iterdir():
            if item.is_dir():
                backup_info = {
                    'name': item.name,
                    'path': str(item),
                    'created': datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    'files': list(item.glob('*.y*ml'))
                }
                backups.append(backup_info)
        
        if backups:
            print("=== Available Backups ===")
            for backup in sorted(backups, key=lambda x: x['created'], reverse=True):
                print(f"  {backup['name']}")
                print(f"    Created: {backup['created']}")
                print(f"    Files: {len(backup['files'])}")
                print(f"    Path: {backup['path']}")
                print()
        else:
            print("No backups found")
        
        return backups
    
    def restore_backup(self, backup_name, interactive=True):
        """Restore from backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"✗ Backup not found: {backup_name}")
            return False
        
        if interactive:
            confirm = input(f"Restore from backup '{backup_name}'? This will overwrite current YAML files. (y/N): ")
            if confirm.lower() != 'y':
                print("Restore cancelled")
                return False
        
        files_restored = []
        
        # Restore files
        for backup_file in backup_path.glob('*.y*ml'):
            target_path = self.yaml_dir / backup_file.name
            shutil.copy2(backup_file, target_path)
            files_restored.append(backup_file.name)
            self.log(f"Restored {backup_file.name}")
        
        if files_restored:
            print(f"✓ Restored backup: {backup_name}")
            print(f"  Files restored: {', '.join(files_restored)}")
            return True
        else:
            print("✗ No files to restore")
            return False
    
    def migrate(self, interactive=True, force=False):
        """Perform migration from YAML to SQLite"""
        self.log("Starting migration process", force=True)
        
        # Check if settings.yaml exists
        settings_path = self.yaml_dir / 'settings.yaml'
        if not settings_path.exists():
            print(f"✗ settings.yaml not found in {self.yaml_dir}")
            return False
        
        # Initialize settings service
        try:
            settings_service = SettingsService(str(self.db_path))
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            return False
        
        # Check if database already has settings
        current_version = settings_service.get_current_version()
        if current_version > 0 and not force:
            if interactive:
                confirm = input("Database already contains settings. Overwrite? (y/N): ")
                if confirm.lower() != 'y':
                    print("Migration cancelled")
                    return False
            else:
                print("✗ Database already contains settings (use --force to overwrite)")
                return False
        
        # Create backup before migration
        backup_path = self.create_backup(f"pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Load main settings.yaml
            self.log("Loading settings.yaml")
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
            
            # Migrate API keys
            if 'api_keys' in settings:
                self.log("Migrating API keys")
                api_keys = settings['api_keys']
                for service, service_keys in api_keys.items():
                    if isinstance(service_keys, list):
                        settings_service.update_api_keys(service, service_keys)
                        self.log(f"  Migrated {service} API keys")
                    else:
                        print(f"⚠ Warning: Unexpected format for {service} API keys")
            
            # Migrate other settings categories
            categories = ['tv_series', 'metadata_tagging', 'scheduler']
            
            for category in categories:
                if category in settings:
                    self.log(f"Migrating {category} settings")
                    settings_service.import_from_yaml(settings, category)
            
            # Migrate badge settings
            badge_files = {
                'audio': 'badge_settings_audio.yml',
                'resolution': 'badge_settings_resolution.yml',
                'review': 'badge_settings_review.yml',
                'awards': 'badge_settings_awards.yml'
            }
            
            for badge_type, filename in badge_files.items():
                badge_path = self.yaml_dir / filename
                if badge_path.exists():
                    try:
                        self.log(f"Migrating {badge_type} badge settings")
                        with open(badge_path, 'r') as f:
                            badge_settings = yaml.safe_load(f)
                        settings_service.update_badge_settings(badge_type, badge_settings)
                    except Exception as e:
                        print(f"⚠ Warning: Error loading {filename}: {e}")
            
            # Set the version to 1 to indicate successful migration
            settings_service.set_version(1)
            
            print("✓ Migration completed successfully!")
            if backup_path:
                print(f"  Backup created at: {backup_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            if backup_path:
                print(f"  Your original files are backed up at: {backup_path}")
            return False
    
    def verify(self):
        """Verify migration integrity"""
        print("=== Verifying Migration ===")
        
        if not os.path.exists(self.db_path):
            print("✗ Database file not found")
            return False
        
        try:
            settings_service = SettingsService(str(self.db_path))
            version = settings_service.get_current_version()
            
            if version == 0:
                print("✗ Database not migrated (version 0)")
                return False
            
            print(f"✓ Database version: {version}")
            
            # Verify database integrity
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['settings', 'api_keys', 'badge_settings', 'settings_version']
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"✗ Missing tables: {missing_tables}")
                return False
            
            print("✓ All required tables present")
            
            # Check data counts
            for table in expected_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            
            conn.close()
            
            # Try to load settings through service
            try:
                api_keys = settings_service.get_api_keys()
                print(f"✓ API keys accessible: {len(api_keys)} services")
                
                categories = ['tv_series', 'metadata_tagging', 'scheduler']
                for category in categories:
                    cat_settings = settings_service.get_settings_by_category(category)
                    if cat_settings:
                        print(f"✓ {category} settings: {len(cat_settings)} items")
                
                badge_types = ['audio', 'resolution', 'review', 'awards']
                for badge_type in badge_types:
                    badge_settings = settings_service.get_badge_settings(badge_type)
                    if badge_settings:
                        print(f"✓ {badge_type} badge settings: {len(badge_settings)} items")
                
            except Exception as e:
                print(f"✗ Error accessing settings through service: {e}")
                return False
            
            print("✓ Migration verification successful")
            return True
            
        except Exception as e:
            print(f"✗ Verification failed: {e}")
            return False
    
    def rollback(self, interactive=True):
        """Rollback migration by removing database and restoring from backup"""
        if not os.path.exists(self.db_path):
            print("✗ No database file to rollback")
            return False
        
        if interactive:
            confirm = input(f"Rollback migration? This will delete the database and restore from the most recent backup. (y/N): ")
            if confirm.lower() != 'y':
                print("Rollback cancelled")
                return False
        
        # Find most recent backup
        backups = []
        if self.backup_dir.exists():
            for item in self.backup_dir.iterdir():
                if item.is_dir() and item.name.startswith('pre_migration_'):
                    backups.append((item.name, item.stat().st_mtime))
        
        if not backups:
            print("✗ No migration backups found")
            return False
        
        # Get most recent backup
        latest_backup = max(backups, key=lambda x: x[1])[0]
        
        try:
            # Remove database
            self.log(f"Removing database: {self.db_path}")
            os.remove(self.db_path)
            
            # Restore from backup
            self.log(f"Restoring from backup: {latest_backup}")
            success = self.restore_backup(latest_backup, interactive=False)
            
            if success:
                print(f"✓ Rollback completed")
                print(f"  Database removed: {self.db_path}")
                print(f"  Restored from: {latest_backup}")
                return True
            else:
                print("✗ Rollback failed during backup restoration")
                return False
            
        except Exception as e:
            print(f"✗ Rollback failed: {e}")
            return False
    
    def dry_run(self):
        """Perform a dry run of the migration without making changes"""
        print("=== Migration Dry Run ===")
        print("This is a simulation - no changes will be made")
        print()
        
        # Check what would be migrated
        settings_path = self.yaml_dir / 'settings.yaml'
        if not settings_path.exists():
            print(f"✗ settings.yaml not found in {self.yaml_dir}")
            return False
        
        try:
            # Load and analyze settings.yaml
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
            
            print(f"✓ Would load settings from: {settings_path}")
            
            # Analyze API keys
            if 'api_keys' in settings:
                api_keys = settings['api_keys']
                print(f"✓ Would migrate API keys for {len(api_keys)} services:")
                for service, service_keys in api_keys.items():
                    if isinstance(service_keys, list):
                        print(f"    {service}: {len(service_keys)} configurations")
                    else:
                        print(f"    {service}: 1 configuration")
            
            # Analyze other categories
            categories = ['tv_series', 'metadata_tagging', 'scheduler']
            for category in categories:
                if category in settings:
                    cat_data = settings[category]
                    if isinstance(cat_data, dict):
                        print(f"✓ Would migrate {category}: {len(cat_data)} settings")
                    else:
                        print(f"✓ Would migrate {category}: 1 setting")
            
            # Check badge files
            badge_files = {
                'audio': 'badge_settings_audio.yml',
                'resolution': 'badge_settings_resolution.yml',
                'review': 'badge_settings_review.yml',
                'awards': 'badge_settings_awards.yml'
            }
            
            for badge_type, filename in badge_files.items():
                badge_path = self.yaml_dir / filename
                if badge_path.exists():
                    try:
                        with open(badge_path, 'r') as f:
                            badge_settings = yaml.safe_load(f)
                        print(f"✓ Would migrate {badge_type} badge settings: {len(badge_settings)} items")
                    except Exception as e:
                        print(f"⚠ Warning: Error analyzing {filename}: {e}")
            
            print(f"\n✓ Would create database at: {self.db_path}")
            print(f"✓ Would create backup in: {self.backup_dir}")
            print(f"✓ Dry run completed successfully")
            print("\nTo perform actual migration, run with --migrate")
            
            return True
            
        except Exception as e:
            print(f"✗ Dry run failed: {e}")
            return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Aphrodite Settings Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_settings_cli.py --status
  python migrate_settings_cli.py --migrate --backup --verbose
  python migrate_settings_cli.py --verify
  python migrate_settings_cli.py --rollback
  python migrate_settings_cli.py --dry-run
  python migrate_settings_cli.py --list-backups
  python migrate_settings_cli.py --restore-backup backup_20241201_120000
        """
    )
    
    # Action arguments
    parser.add_argument("--status", action="store_true", help="Check migration status")
    parser.add_argument("--migrate", action="store_true", help="Perform migration")
    parser.add_argument("--verify", action="store_true", help="Verify migration integrity")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without changes")
    
    # Backup arguments
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--list-backups", action="store_true", help="List available backups")
    parser.add_argument("--restore-backup", metavar="NAME", help="Restore from specific backup")
    
    # Path arguments
    parser.add_argument("--yaml-dir", help="Directory containing YAML files")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    
    # Mode arguments
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompts")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--force", action="store_true", help="Force migration even if database exists")
    
    args = parser.parse_args()
    
    # If no action specified, show status
    if not any([args.status, args.migrate, args.verify, args.rollback, args.dry_run, 
               args.list_backups, args.restore_backup]):
        args.status = True
    
    # Initialize CLI
    cli = MigrationCLI(verbose=args.verbose)
    
    # Setup paths
    try:
        cli.setup_paths(args.yaml_dir, args.db_path)
    except Exception as e:
        print(f"✗ Error setting up paths: {e}")
        return 1
    
    # Execute actions
    try:
        if args.status:
            cli.check_status()
        
        elif args.list_backups:
            cli.list_backups()
        
        elif args.restore_backup:
            success = cli.restore_backup(args.restore_backup, not args.non_interactive)
            return 0 if success else 1
        
        elif args.dry_run:
            success = cli.dry_run()
            return 0 if success else 1
        
        elif args.migrate:
            if args.backup:
                cli.create_backup()
            success = cli.migrate(not args.non_interactive, args.force)
            return 0 if success else 1
        
        elif args.verify:
            success = cli.verify()
            return 0 if success else 1
        
        elif args.rollback:
            success = cli.rollback(not args.non_interactive)
            return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
