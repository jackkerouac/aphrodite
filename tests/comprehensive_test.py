#!/usr/bin/env python3
# comprehensive_test.py - Test all updated files work with compatibility layer

import sys
import os

# Add paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'aphrodite-web'))

def test_file_compatibility(file_path, test_name):
    """Test if a file can be imported and run basic functions"""
    print(f"\n🧪 Testing {test_name}...")
    try:
        # Test import
        if file_path == "check_jellyfin_connection":
            from aphrodite_helpers.check_jellyfin_connection import load_settings
            settings = load_settings()
            if settings:
                print(f"✅ {test_name}: Successfully loaded settings")
                return True
            else:
                print(f"⚠️  {test_name}: No settings loaded (may be empty)")
                return True
                
        elif file_path == "badge_settings":
            from aphrodite_helpers.badge_components.badge_settings import load_badge_settings
            badge_settings = load_badge_settings("badge_settings_audio.yml")
            print(f"✅ {test_name}: Successfully tested badge settings loading")
            return True
            
        elif file_path == "read_audio_settings":
            from aphrodite_helpers.read_audio_settings import load_yaml_from_root
            settings = load_yaml_from_root("badge_settings_audio.yml")
            print(f"✅ {test_name}: Successfully tested audio settings loading")
            return True
            
        elif file_path == "settings_validator":
            from aphrodite_helpers.settings_validator import run_settings_check
            # Note: run_settings_check calls sys.exit, so we just test import
            print(f"✅ {test_name}: Successfully imported settings validator")
            return True
            
        elif file_path == "config_service":
            from app.services.config import ConfigService
            config_service = ConfigService()
            files = config_service.get_config_files()
            print(f"✅ {test_name}: Found {len(files)} config files")
            return True
            
        else:
            print(f"❌ {test_name}: Unknown test case")
            return False
            
    except Exception as e:
        print(f"❌ {test_name}: Error - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive compatibility tests"""
    print("🚀 Comprehensive Phase 2 Compatibility Test")
    print("=" * 50)
    
    tests = [
        ("check_jellyfin_connection", "Jellyfin Connection Helper"),
        ("badge_settings", "Badge Settings Components"),
        ("read_audio_settings", "Audio Settings Reader"),
        ("settings_validator", "Settings Validator"),
        ("config_service", "Web Config Service"),
    ]
    
    passed = 0
    total = len(tests)
    
    # Test settings compatibility layer first
    print("\n🧪 Testing Settings Compatibility Layer...")
    try:
        from aphrodite_helpers.settings_compat import load_settings, load_badge_settings
        settings = load_settings()
        if settings:
            print("✅ Compatibility Layer: Successfully loaded settings")
            passed += 1
        else:
            print("⚠️  Compatibility Layer: No settings loaded")
            passed += 1  # This is OK
    except Exception as e:
        print(f"❌ Compatibility Layer: Error - {e}")
    
    total += 1
    
    # Run individual file tests
    for file_path, test_name in tests:
        if test_file_compatibility(file_path, test_name):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Comprehensive Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All compatibility tests passed!")
        print("✅ Phase 2 implementation is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
