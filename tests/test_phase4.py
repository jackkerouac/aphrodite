#!/usr/bin/env python3
"""
Phase 4 Comprehensive Test Suite

Tests all Phase 4 functionality including:
- Enhanced CLI tool
- Docker verification
- Documentation validation
- End-to-end migration scenarios
"""

import os
import sys
import subprocess
import tempfile
import shutil
import yaml
import sqlite3
from pathlib import Path
import unittest

# Add parent directory to path
parent_dir = Path(os.path.abspath(__file__)).parent.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / 'aphrodite-web'))

class Phase4TestSuite(unittest.TestCase):
    """Comprehensive test suite for Phase 4"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = Path(tempfile.mkdtemp(prefix="aphrodite_phase4_test_"))
        cls.tools_dir = parent_dir / 'tools'
        cls.original_dir = os.getcwd()
        
        print(f"Test directory: {cls.test_dir}")
        
        # Create test YAML files
        cls.create_test_yaml_files()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_dir)
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_yaml_files(cls):
        """Create test YAML files for migration testing"""
        # Create settings.yaml
        settings = {
            'api_keys': {
                'Jellyfin': [{
                    'url': 'http://localhost:8096',
                    'api_key': 'test_api_key',
                    'user_id': 'test_user'
                }],
                'OMDB': [{'api_key': 'omdb_test_key'}],
                'TMDB': [{'api_key': 'tmdb_test_key'}]
            },
            'tv_series': {
                'enabled': True,
                'auto_process': False
            },
            'metadata_tagging': {
                'enabled': True,
                'format': 'standard'
            },
            'scheduler': {
                'enabled': False,
                'interval': 3600
            }
        }
        
        with open(cls.test_dir / 'settings.yaml', 'w') as f:
            yaml.dump(settings, f)
        
        # Create badge settings files
        badge_settings = {
            'audio': {'enabled': True, 'format': 'standard'},
            'resolution': {'4k': True, '1080p': True},
            'review': {'min_score': 7.0, 'enabled': True},
            'awards': {'oscars': True, 'emmys': True}
        }
        
        for badge_type, settings in badge_settings.items():
            filename = f'badge_settings_{badge_type}.yml'
            with open(cls.test_dir / filename, 'w') as f:
                yaml.dump(settings, f)
        
        # Create data directory
        (cls.test_dir / 'data').mkdir(exist_ok=True)
    
    def run_cli_command(self, args, cwd=None):
        """Run CLI command and return result"""
        if cwd is None:
            cwd = self.test_dir
        
        cli_script = self.tools_dir / 'migrate_settings_cli.py'
        cmd = [sys.executable, str(cli_script)] + args
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd,
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def test_cli_help(self):
        """Test CLI help functionality"""
        print("\n=== Testing CLI Help ===")
        
        returncode, stdout, stderr = self.run_cli_command(['--help'])
        
        self.assertEqual(returncode, 0, f"Help command failed: {stderr}")
        self.assertIn("Enhanced Aphrodite Settings Migration Tool", stdout)
        self.assertIn("--status", stdout)
        self.assertIn("--migrate", stdout)
        self.assertIn("--verify", stdout)
        
        print("✅ CLI help working correctly")
    
    def test_cli_status(self):
        """Test CLI status command"""
        print("\n=== Testing CLI Status ===")
        
        returncode, stdout, stderr = self.run_cli_command(['--status'])
        
        self.assertEqual(returncode, 0, f"Status command failed: {stderr}")
        self.assertIn("Migration Status", stdout)
        self.assertIn("settings.yaml", stdout)
        
        print("✅ CLI status working correctly")
    
    def test_cli_dry_run(self):
        """Test CLI dry run functionality"""
        print("\n=== Testing CLI Dry Run ===")
        
        returncode, stdout, stderr = self.run_cli_command(['--dry-run'])
        
        self.assertEqual(returncode, 0, f"Dry run failed: {stderr}")
        self.assertIn("Migration Dry Run", stdout)
        self.assertIn("no changes will be made", stdout)
        self.assertIn("Would migrate API keys", stdout)
        
        print("✅ CLI dry run working correctly")
    
    def test_cli_backup(self):
        """Test CLI backup functionality"""
        print("\n=== Testing CLI Backup ===")
        
        returncode, stdout, stderr = self.run_cli_command(['--backup'])
        
        self.assertEqual(returncode, 0, f"Backup command failed: {stderr}")
        self.assertIn("Created backup", stdout)
        
        # Check backup was created
        backup_dir = self.test_dir / 'backups' / 'settings'
        self.assertTrue(backup_dir.exists(), "Backup directory not created")
        
        # Find the backup folder
        backup_folders = [d for d in backup_dir.iterdir() if d.is_dir()]
        self.assertGreater(len(backup_folders), 0, "No backup folder created")
        
        backup_folder = backup_folders[0]
        self.assertTrue((backup_folder / 'settings.yaml').exists(), "settings.yaml not backed up")
        
        print("✅ CLI backup working correctly")
    
    def test_cli_migration(self):
        """Test CLI migration functionality"""
        print("\n=== Testing CLI Migration ===")
        
        returncode, stdout, stderr = self.run_cli_command(['--migrate', '--non-interactive', '--verbose'])
        
        self.assertEqual(returncode, 0, f"Migration failed: {stderr}")
        self.assertIn("Migration completed successfully", stdout)
        
        # Check database was created
        db_path = self.test_dir / 'data' / 'aphrodite.db'
        self.assertTrue(db_path.exists(), "Database file not created")
        
        # Check database content
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['settings', 'api_keys', 'badge_settings', 'settings_version']
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not created")
        
        # Check some data exists
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        api_count = cursor.fetchone()[0]
        self.assertGreater(api_count, 0, "No API keys migrated")
        
        conn.close()
        
        print("✅ CLI migration working correctly")
    
    def test_cli_verify(self):
        """Test CLI verify functionality"""
        print("\n=== Testing CLI Verify ===")
        
        # First migrate
        self.run_cli_command(['--migrate', '--non-interactive'])
        
        # Then verify
        returncode, stdout, stderr = self.run_cli_command(['--verify'])
        
        self.assertEqual(returncode, 0, f"Verify failed: {stderr}")
        self.assertIn("Verifying Migration", stdout)
        self.assertIn("verification successful", stdout)
        
        print("✅ CLI verify working correctly")
    
    def test_docker_verification_tool(self):
        """Test Docker verification tool"""
        print("\n=== Testing Docker Verification Tool ===")
        
        # First migrate to have something to verify
        self.run_cli_command(['--migrate', '--non-interactive'])
        
        # Run docker verification
        verify_script = self.tools_dir / 'verify_docker_migration.py'
        cmd = [sys.executable, str(verify_script)]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Note: Docker verification may fail in test environment (not actually Docker)
            # but we can check that the script runs and produces expected output
            self.assertIn("DOCKER MIGRATION VERIFICATION", result.stdout)
            self.assertIn("Docker Environment:", result.stdout)
            
            print("✅ Docker verification tool working correctly")
            
        except subprocess.TimeoutExpired:
            self.fail("Docker verification tool timed out")
    
    def test_file_structure(self):
        """Test that all required files exist"""
        print("\n=== Testing File Structure ===")
        
        required_files = [
            'tools/migrate_settings_cli.py',
            'tools/verify_docker_migration.py',
            'tools/migrate_settings.py',
            'tools/verify_migration.py'
        ]
        
        for file_path in required_files:
            full_path = parent_dir / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
            
            # Check file is executable/readable
            self.assertTrue(os.access(full_path, os.R_OK), f"File not readable: {file_path}")
        
        print("✅ All required files present")
    
    def test_end_to_end_scenario(self):
        """Test complete end-to-end migration scenario"""
        print("\n=== Testing End-to-End Scenario ===")
        
        # 1. Check initial status
        returncode, stdout, stderr = self.run_cli_command(['--status'])
        self.assertEqual(returncode, 0)
        self.assertIn("Migration needed", stdout)
        
        # 2. Create backup
        returncode, stdout, stderr = self.run_cli_command(['--backup'])
        self.assertEqual(returncode, 0)
        
        # 3. Do dry run
        returncode, stdout, stderr = self.run_cli_command(['--dry-run'])
        self.assertEqual(returncode, 0)
        
        # 4. Perform migration
        returncode, stdout, stderr = self.run_cli_command(['--migrate', '--non-interactive', '--verbose'])
        self.assertEqual(returncode, 0)
        
        # 5. Verify migration
        returncode, stdout, stderr = self.run_cli_command(['--verify'])
        self.assertEqual(returncode, 0)
        
        # 6. Check final status
        returncode, stdout, stderr = self.run_cli_command(['--status'])
        self.assertEqual(returncode, 0)
        self.assertIn("Already migrated", stdout)
        
        print("✅ End-to-end scenario working correctly")

def run_performance_tests():
    """Run performance tests for CLI tool"""
    print("\n" + "="*60)
    print("🚀 PERFORMANCE TESTS")
    print("="*60)
    
    import time
    
    # Create a large test dataset
    test_dir = Path(tempfile.mkdtemp(prefix="perf_test_"))
    
    try:
        # Create large settings file
        large_settings = {
            'api_keys': {
                f'Service_{i}': [{'key': f'value_{i}', 'url': f'http://test{i}.com'}] 
                for i in range(100)
            },
            'tv_series': {f'setting_{i}': f'value_{i}' for i in range(500)},
            'metadata_tagging': {f'tag_{i}': f'format_{i}' for i in range(200)},
            'scheduler': {f'schedule_{i}': i for i in range(100)}
        }
        
        with open(test_dir / 'settings.yaml', 'w') as f:
            yaml.dump(large_settings, f)
        
        # Create data directory
        (test_dir / 'data').mkdir()
        
        # Time the migration
        cli_script = parent_dir / 'tools' / 'migrate_settings_cli.py'
        cmd = [sys.executable, str(cli_script), '--migrate', '--non-interactive']
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=test_dir, capture_output=True, text=True)
        end_time = time.time()
        
        migration_time = end_time - start_time
        
        print(f"📊 Migration of {len(large_settings['api_keys'])} services completed in {migration_time:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ Performance test passed")
            
            # Check database size
            db_path = test_dir / 'data' / 'aphrodite.db'
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"📁 Database size: {size_mb:.2f} MB")
        else:
            print(f"❌ Performance test failed: {result.stderr}")
    
    finally:
        shutil.rmtree(test_dir)

def main():
    """Main test runner"""
    print("🧪 Phase 4 Comprehensive Test Suite")
    print("="*50)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase4TestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print("🎉 Phase 4 implementation is working correctly")
        return 0
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
