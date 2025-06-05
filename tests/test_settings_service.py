# tests/test_settings_service.py

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import settings service
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / "aphrodite-web"))

from app.services.settings_service import SettingsService

class TestSettingsService(unittest.TestCase):
    
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.settings_service = SettingsService(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.test_db.name)
    
    def test_database_initialization(self):
        """Test that database is properly initialized"""
        # Database should be created and version should be 0
        version = self.settings_service.get_current_version()
        self.assertEqual(version, 0)
    
    def test_setting_crud_operations(self):
        """Test basic CRUD operations for settings"""
        # Test setting a string value
        self.settings_service.set_setting('test.string', 'hello', 'test')
        value = self.settings_service.get_setting('test.string')
        self.assertEqual(value, 'hello')
        
        # Test setting an integer value
        self.settings_service.set_setting('test.integer', 42, 'test')
        value = self.settings_service.get_setting('test.integer')
        self.assertEqual(value, 42)
        self.assertIsInstance(value, int)
        
        # Test setting a boolean value
        self.settings_service.set_setting('test.boolean', True, 'test')
        value = self.settings_service.get_setting('test.boolean')
        self.assertEqual(value, True)
        self.assertIsInstance(value, bool)
        
        # Test setting a float value
        self.settings_service.set_setting('test.float', 3.14, 'test')
        value = self.settings_service.get_setting('test.float')
        self.assertEqual(value, 3.14)
        self.assertIsInstance(value, float)
        
        # Test setting a JSON value
        test_dict = {'key': 'value', 'number': 123}
        self.settings_service.set_setting('test.json', test_dict, 'test')
        value = self.settings_service.get_setting('test.json')
        self.assertEqual(value, test_dict)
        self.assertIsInstance(value, dict)
        
        # Test default value
        value = self.settings_service.get_setting('nonexistent', 'default')
        self.assertEqual(value, 'default')
    
    def test_get_settings_by_category(self):
        """Test retrieving settings by category"""
        # Add some test settings
        self.settings_service.set_setting('cat1.setting1', 'value1', 'cat1')
        self.settings_service.set_setting('cat1.setting2', 42, 'cat1')
        self.settings_service.set_setting('cat2.setting1', True, 'cat2')
        
        # Get settings for category 1
        cat1_settings = self.settings_service.get_settings_by_category('cat1')
        self.assertEqual(len(cat1_settings), 2)
        self.assertEqual(cat1_settings['cat1.setting1'], 'value1')
        self.assertEqual(cat1_settings['cat1.setting2'], 42)
        
        # Get settings for category 2
        cat2_settings = self.settings_service.get_settings_by_category('cat2')
        self.assertEqual(len(cat2_settings), 1)
        self.assertEqual(cat2_settings['cat2.setting1'], True)
    
    def test_api_keys_operations(self):
        """Test API keys management"""
        # Test single service with single group
        jellyfin_keys = [
            {'url': 'http://test.com', 'api_key': 'test123', 'user_id': 'user1'}
        ]
        self.settings_service.update_api_keys('Jellyfin', jellyfin_keys)
        
        # Retrieve keys
        retrieved_keys = self.settings_service.get_api_keys('Jellyfin')
        self.assertEqual(len(retrieved_keys), 1)
        self.assertEqual(retrieved_keys[0]['url'], 'http://test.com')
        self.assertEqual(retrieved_keys[0]['api_key'], 'test123')
        self.assertEqual(retrieved_keys[0]['user_id'], 'user1')
        
        # Test multiple services
        omdb_keys = [
            {'api_key': 'omdb123', 'cache_expiration': 60}
        ]
        self.settings_service.update_api_keys('OMDB', omdb_keys)
        
        all_keys = self.settings_service.get_api_keys()
        self.assertIn('Jellyfin', all_keys)
        self.assertIn('OMDB', all_keys)
        self.assertEqual(len(all_keys), 2)
    
    def test_badge_settings_operations(self):
        """Test badge settings management"""
        # Test audio badge settings
        audio_settings = {
            'General': {
                'general_badge_size': 100,
                'general_edge_padding': 30
            },
            'Text': {
                'font': 'AvenirNextLTProBold.otf',
                'text-color': '#FFFFFF'
            }
        }
        
        self.settings_service.update_badge_settings('audio', audio_settings)
        
        # Retrieve settings
        retrieved_settings = self.settings_service.get_badge_settings('audio')
        self.assertIn('General', retrieved_settings)
        self.assertIn('Text', retrieved_settings)
        self.assertEqual(retrieved_settings['General']['general_badge_size'], 100)
        self.assertEqual(retrieved_settings['Text']['font'], 'AvenirNextLTProBold.otf')
    
    def test_version_management(self):
        """Test version tracking"""
        # Initial version should be 0
        version = self.settings_service.get_current_version()
        self.assertEqual(version, 0)
        
        # Set version to 1
        self.settings_service.set_version(1)
        version = self.settings_service.get_current_version()
        self.assertEqual(version, 1)
        
        # Set version to 2
        self.settings_service.set_version(2)
        version = self.settings_service.get_current_version()
        self.assertEqual(version, 2)
    
    def test_yaml_import(self):
        """Test importing from YAML data"""
        yaml_data = {
            'tv_series': {
                'show_dominant_badges': True,
                'max_episodes_to_analyze': 5
            },
            'metadata_tagging': {
                'enabled': True,
                'tag_name': 'aphrodite-overlay'
            }
        }
        
        # Import TV series settings
        self.settings_service.import_from_yaml(yaml_data, 'tv_series')
        
        # Verify imported settings
        tv_settings = self.settings_service.get_settings_by_category('tv_series')
        self.assertEqual(tv_settings['tv_series.show_dominant_badges'], True)
        self.assertEqual(tv_settings['tv_series.max_episodes_to_analyze'], 5)
        
        # Import metadata tagging settings
        self.settings_service.import_from_yaml(yaml_data, 'metadata_tagging')
        
        # Verify imported settings
        metadata_settings = self.settings_service.get_settings_by_category('metadata_tagging')
        self.assertEqual(metadata_settings['metadata_tagging.enabled'], True)
        self.assertEqual(metadata_settings['metadata_tagging.tag_name'], 'aphrodite-overlay')
    
    def test_export_to_yaml(self):
        """Test exporting to YAML format"""
        # Add some test data
        self.settings_service.set_setting('tv_series.show_dominant_badges', True, 'tv_series')
        self.settings_service.set_setting('tv_series.max_episodes_to_analyze', 5, 'tv_series')
        
        # Add API keys
        jellyfin_keys = [
            {'url': 'http://test.com', 'api_key': 'test123', 'user_id': 'user1'}
        ]
        self.settings_service.update_api_keys('Jellyfin', jellyfin_keys)
        
        # Add badge settings
        audio_settings = {
            'General': {'general_badge_size': 100},
            'Text': {'font': 'AvenirNextLTProBold.otf'}
        }
        self.settings_service.update_badge_settings('audio', audio_settings)
        
        # Export to YAML
        yaml_data, badge_data = self.settings_service.export_to_yaml()
        
        # Verify exported data
        self.assertIn('tv_series', yaml_data)
        self.assertEqual(yaml_data['tv_series']['show_dominant_badges'], True)
        self.assertEqual(yaml_data['tv_series']['max_episodes_to_analyze'], 5)
        
        self.assertIn('api_keys', yaml_data)
        self.assertIn('Jellyfin', yaml_data['api_keys'])
        self.assertEqual(yaml_data['api_keys']['Jellyfin'][0]['url'], 'http://test.com')
        
        self.assertIn('audio', badge_data)
        self.assertEqual(badge_data['audio']['General']['general_badge_size'], 100)

if __name__ == '__main__':
    # Run the tests
    unittest.main()
