#!/usr/bin/env python3
"""
Docker Migration Verification Tool

This tool helps verify that a Docker container is using SQLite database
instead of YAML files for configuration storage.
"""

import os
import sys
import sqlite3
import yaml
import json
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
    sys.exit(1)

class DockerVerification:
    """Verify Docker container is using SQLite instead of YAML"""
    
    def __init__(self):
        self.is_docker = self.detect_docker_environment()
        self.setup_paths()
    
    def detect_docker_environment(self):
        """Detect if running in Docker"""
        # Check for Docker indicators
        docker_indicators = [
            os.path.exists('/.dockerenv'),
            os.path.exists('/app'),
            os.environ.get('DOCKER_CONTAINER') == 'true'
        ]
        
        is_docker = any(docker_indicators)
        print(f"🐳 Docker Environment: {'Yes' if is_docker else 'No'}")
        return is_docker
    
    def setup_paths(self):
        """Setup paths based on environment"""
        if self.is_docker:
            self.base_dir = Path('/app')
            self.db_path = '/app/data/aphrodite.db'
        else:
            self.base_dir = Path(os.path.abspath(__file__)).parent.parent
            self.db_path = self.base_dir / 'data' / 'aphrodite.db'
        
        print(f"📁 Base Directory: {self.base_dir}")
        print(f"🗄️ Database Path: {self.db_path}")
    
    def check_file_locations(self):
        """Check what files exist and their timestamps"""
        print("\n=== File Existence Check ===")
        
        # Check YAML files
        yaml_files = {
            'settings.yaml': self.base_dir / 'settings.yaml',
            'badge_settings_audio.yml': self.base_dir / 'badge_settings_audio.yml',
            'badge_settings_resolution.yml': self.base_dir / 'badge_settings_resolution.yml',
            'badge_settings_review.yml': self.base_dir / 'badge_settings_review.yml',
            'badge_settings_awards.yml': self.base_dir / 'badge_settings_awards.yml'
        }
        
        yaml_exists = {}
        for name, path in yaml_files.items():
            exists = path.exists()
            yaml_exists[name] = exists
            if exists:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                print(f"📄 {name}: ✅ EXISTS (modified: {mtime})")
            else:
                print(f"📄 {name}: ❌ NOT FOUND")
        
        # Check database
        db_exists = os.path.exists(self.db_path)
        if db_exists:
            mtime = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            size = os.path.getsize(self.db_path)
            print(f"🗄️ aphrodite.db: ✅ EXISTS (modified: {mtime}, size: {size} bytes)")
        else:
            print(f"🗄️ aphrodite.db: ❌ NOT FOUND")
        
        return yaml_exists, db_exists
    
    def check_database_content(self):
        """Check database content and version"""
        print("\n=== Database Content Check ===")
        
        if not os.path.exists(self.db_path):
            print("❌ Database file not found")
            return False
        
        try:
            settings_service = SettingsService(str(self.db_path))
            version = settings_service.get_current_version()
            
            print(f"📊 Database Version: {version}")
            
            if version == 0:
                print("⚠️ Database exists but not migrated (version 0)")
                return False
            
            # Check table contents
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['settings', 'api_keys', 'badge_settings', 'settings_version']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📋 {table}: {count} records")
            
            # Show some sample data
            print("\n📝 Sample Database Content:")
            
            # Show API keys
            cursor.execute("SELECT DISTINCT service FROM api_keys")
            services = [row[0] for row in cursor.fetchall()]
            if services:
                print(f"🔑 API Services: {', '.join(services)}")
            
            # Show settings categories
            cursor.execute("SELECT DISTINCT category FROM settings")
            categories = [row[0] for row in cursor.fetchall()]
            if categories:
                print(f"⚙️ Settings Categories: {', '.join(categories)}")
            
            # Show badge types
            cursor.execute("SELECT DISTINCT badge_type FROM badge_settings")
            badge_types = [row[0] for row in cursor.fetchall()]
            if badge_types:
                print(f"🏆 Badge Types: {', '.join(badge_types)}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def test_settings_access(self):
        """Test accessing settings through the service"""
        print("\n=== Settings Access Test ===")
        
        try:
            settings_service = SettingsService(str(self.db_path))
            
            # Test API keys access
            print("🔑 Testing API Keys Access:")
            api_keys = settings_service.get_api_keys()
            for service, configs in api_keys.items():
                print(f"   {service}: {len(configs)} configuration(s)")
            
            # Test settings categories
            print("\n⚙️ Testing Settings Categories:")
            categories = ['tv_series', 'metadata_tagging', 'scheduler']
            for category in categories:
                settings = settings_service.get_settings_by_category(category)
                if settings:
                    print(f"   {category}: {len(settings)} setting(s)")
                else:
                    print(f"   {category}: No settings found")
            
            # Test badge settings
            print("\n🏆 Testing Badge Settings:")
            badge_types = ['audio', 'resolution', 'review', 'awards']
            for badge_type in badge_types:
                settings = settings_service.get_badge_settings(badge_type)
                if settings:
                    print(f"   {badge_type}: {len(settings)} setting(s)")
                else:
                    print(f"   {badge_type}: No settings found")
            
            print("✅ Settings access successful - using SQLite database")
            return True
            
        except Exception as e:
            print(f"❌ Settings access failed: {e}")
            return False
    
    def test_compatibility_layer(self):
        """Test the compatibility layer"""
        print("\n=== Compatibility Layer Test ===")
        
        try:
            # Import and test compatibility layer
            sys.path.append(str(self.base_dir / 'aphrodite_helpers'))
            from settings_compat import SettingsCompat
            
            compat = SettingsCompat(str(self.db_path))
            
            # Test loading settings
            settings = compat.load_settings()
            if settings:
                print(f"✅ Compatibility layer working - loaded {len(settings)} top-level settings")
                
                # Check for expected sections
                expected_sections = ['api_keys', 'tv_series', 'metadata_tagging', 'scheduler']
                for section in expected_sections:
                    if section in settings:
                        print(f"   ✅ {section}: Found")
                    else:
                        print(f"   ⚠️ {section}: Missing")
                
                return True
            else:
                print("❌ Compatibility layer returned empty settings")
                return False
                
        except Exception as e:
            print(f"❌ Compatibility layer test failed: {e}")
            return False
    
    def compare_yaml_vs_database(self):
        """Compare YAML file content with database content"""
        print("\n=== YAML vs Database Comparison ===")
        
        # Check if YAML files exist
        yaml_path = self.base_dir / 'settings.yaml'
        if not yaml_path.exists():
            print("📄 No YAML file to compare")
            return True
        
        try:
            # Load YAML content
            with open(yaml_path, 'r') as f:
                yaml_content = yaml.safe_load(f)
            
            # Load database content through compatibility layer
            sys.path.append(str(self.base_dir / 'aphrodite_helpers'))
            from settings_compat import SettingsCompat
            
            compat = SettingsCompat(str(self.db_path))
            db_content = compat.load_settings()
            
            print("🔍 Comparing key sections:")
            
            # Compare API keys
            yaml_api_keys = yaml_content.get('api_keys', {})
            db_api_keys = db_content.get('api_keys', {})
            
            print(f"🔑 API Keys:")
            print(f"   YAML services: {list(yaml_api_keys.keys())}")
            print(f"   DB services: {list(db_api_keys.keys())}")
            
            # Compare other sections
            sections = ['tv_series', 'metadata_tagging', 'scheduler']
            for section in sections:
                yaml_section = yaml_content.get(section, {})
                db_section = db_content.get(section, {})
                
                yaml_count = len(yaml_section) if isinstance(yaml_section, dict) else 1
                db_count = len(db_section) if isinstance(db_section, dict) else 1
                
                print(f"⚙️ {section}:")
                print(f"   YAML: {yaml_count} items")
                print(f"   DB: {db_count} items")
            
            print("\n💡 If DB counts > 0, the system is using the database")
            return True
            
        except Exception as e:
            print(f"❌ Comparison failed: {e}")
            return False
    
    def create_test_modification(self):
        """Create a test modification to verify live database usage"""
        print("\n=== Live Database Test ===")
        
        try:
            settings_service = SettingsService(str(self.db_path))
            
            # Add a test setting
            test_key = "verification_test.docker_test"
            test_value = f"Docker verification test - {datetime.now().isoformat()}"
            
            settings_service.set_setting(test_key, test_value, "verification_test", 
                                       "Test setting to verify Docker database usage")
            
            print(f"✅ Added test setting: {test_key}")
            
            # Retrieve it back
            retrieved_value = settings_service.get_setting(test_key)
            
            if retrieved_value == test_value:
                print(f"✅ Successfully retrieved test setting")
                print(f"   Value: {retrieved_value}")
                
                # Clean up
                # Note: We don't have a delete method, but we can set it to empty
                settings_service.set_setting(test_key, "", "verification_test", "Cleared")
                print(f"✅ Cleaned up test setting")
                
                return True
            else:
                print(f"❌ Retrieved value doesn't match: {retrieved_value}")
                return False
                
        except Exception as e:
            print(f"❌ Live database test failed: {e}")
            return False
    
    def generate_verification_report(self):
        """Generate a comprehensive verification report"""
        print("\n" + "="*60)
        print("🔍 DOCKER MIGRATION VERIFICATION REPORT")
        print("="*60)
        
        yaml_exists, db_exists = self.check_file_locations()
        db_content_ok = self.check_database_content()
        settings_access_ok = self.test_settings_access()
        compat_ok = self.test_compatibility_layer()
        comparison_ok = self.compare_yaml_vs_database()
        live_test_ok = self.create_test_modification()
        
        print("\n" + "="*60)
        print("📊 VERIFICATION SUMMARY")
        print("="*60)
        
        # Database status
        if db_exists and db_content_ok:
            print("🗄️ Database Status: ✅ ACTIVE AND POPULATED")
        elif db_exists:
            print("🗄️ Database Status: ⚠️ EXISTS BUT EMPTY/INVALID")
        else:
            print("🗄️ Database Status: ❌ NOT FOUND")
        
        # Settings access
        if settings_access_ok:
            print("⚙️ Settings Access: ✅ USING DATABASE")
        else:
            print("⚙️ Settings Access: ❌ FAILED")
        
        # Compatibility layer
        if compat_ok:
            print("🔄 Compatibility Layer: ✅ WORKING")
        else:
            print("🔄 Compatibility Layer: ❌ FAILED")
        
        # Overall status
        print("\n" + "-"*60)
        
        if all([db_exists, db_content_ok, settings_access_ok, compat_ok]):
            print("🎉 OVERALL STATUS: ✅ DOCKER IS USING SQLITE DATABASE")
            print("   Your Docker container has successfully migrated to SQLite!")
            print("   The system is no longer dependent on YAML files.")
        elif any(yaml_exists.values()) and not db_content_ok:
            print("⚠️ OVERALL STATUS: 🔄 STILL USING YAML FILES")
            print("   Migration may not have completed successfully.")
            print("   Run migration process to switch to SQLite.")
        else:
            print("❌ OVERALL STATUS: 🚨 CONFIGURATION ISSUE")
            print("   Neither YAML nor database appears to be working properly.")
            print("   Check your configuration and migration status.")
        
        print("\n" + "="*60)
        
        return all([db_exists, db_content_ok, settings_access_ok, compat_ok])

def main():
    """Main verification entry point"""
    print("🐳 Aphrodite Docker Migration Verification Tool")
    print("=" * 50)
    
    verifier = DockerVerification()
    success = verifier.generate_verification_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
