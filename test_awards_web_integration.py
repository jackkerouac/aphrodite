#!/usr/bin/env python3
"""
Test script for Awards Badge Web Integration - Phase 3
Tests the complete awards badge web interface integration
"""

import os
import sys
import yaml
import requests
import time
from pathlib import Path

def test_awards_badge_files():
    """Test that all required awards badge files exist"""
    print("🔍 Testing Awards Badge Files...")
    
    base_dir = Path(__file__).parent
    
    # Test awards configuration file
    awards_config = base_dir / "badge_settings_awards.yml"
    if not awards_config.exists():
        print("❌ badge_settings_awards.yml not found")
        return False
    
    # Test awards images directory structure
    awards_images = base_dir / "images" / "awards"
    if not awards_images.exists():
        print("❌ images/awards directory not found")
        return False
    
    # Test color scheme directories
    color_schemes = ['black', 'gray', 'red', 'yellow']
    for color in color_schemes:
        color_dir = awards_images / color
        if not color_dir.exists():
            print(f"❌ images/awards/{color} directory not found")
            return False
        
        # Test for at least one award image
        images = list(color_dir.glob("*.png"))
        if not images:
            print(f"❌ No PNG images found in images/awards/{color}")
            return False
    
    print("✅ All awards badge files exist")
    return True

def test_awards_configuration():
    """Test that awards configuration is valid"""
    print("🔍 Testing Awards Configuration...")
    
    try:
        with open("badge_settings_awards.yml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Test required sections
        required_sections = ['General', 'Awards', 'ImageBadges']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing section: {section}")
                return False
        
        # Test General settings
        general = config['General']
        if general.get('general_badge_position') != 'bottom-right-flush':
            print("❌ Invalid badge position for awards")
            return False
        
        if general.get('general_edge_padding') != 0:
            print("❌ Awards should have 0 edge padding")
            return False
        
        # Test Awards settings
        awards = config['Awards']
        if 'color_scheme' not in awards:
            print("❌ Missing color_scheme in Awards section")
            return False
        
        if awards['color_scheme'] not in ['black', 'gray', 'red', 'yellow']:
            print("❌ Invalid color scheme")
            return False
        
        if 'award_sources' not in awards or not isinstance(awards['award_sources'], list):
            print("❌ Missing or invalid award_sources")
            return False
        
        # Test ImageBadges settings
        image_badges = config['ImageBadges']
        if not image_badges.get('enable_image_badges'):
            print("❌ Image badges should be enabled for awards")
            return False
        
        if image_badges.get('fallback_to_text') != False:
            print("❌ Awards should not fallback to text")
            return False
        
        print("✅ Awards configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading awards configuration: {e}")
        return False

def test_web_components():
    """Test that web components exist"""
    print("🔍 Testing Web Components...")
    
    # Test AwardsSettings.vue component
    awards_component = Path("aphrodite-web/frontend/src/components/settings/AwardsSettings.vue")
    if not awards_component.exists():
        print("❌ AwardsSettings.vue component not found")
        return False
    
    # Test that SettingsView.vue was updated
    settings_view = Path("aphrodite-web/frontend/src/views/SettingsView.vue")
    if not settings_view.exists():
        print("❌ SettingsView.vue not found")
        return False
    
    # Read SettingsView.vue and check for awards integration
    try:
        with open(settings_view, 'r') as f:
            content = f.read()
        
        if 'AwardsSettings' not in content:
            print("❌ AwardsSettings not imported in SettingsView.vue")
            return False
        
        if "{ id: 'awards', name: 'Awards' }" not in content:
            print("❌ Awards tab not added to SettingsView.vue")
            return False
        
        print("✅ Web components are properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading SettingsView.vue: {e}")
        return False

def test_backend_config_service():
    """Test that backend ConfigService supports awards"""
    print("🔍 Testing Backend Config Service...")
    
    config_service = Path("aphrodite-web/app/services/config.py")
    if not config_service.exists():
        print("❌ ConfigService not found")
        return False
    
    try:
        with open(config_service, 'r') as f:
            content = f.read()
        
        if 'badge_settings_awards.yml' not in content:
            print("❌ ConfigService doesn't include badge_settings_awards.yml")
            return False
        
        print("✅ Backend Config Service supports awards")
        return True
        
    except Exception as e:
        print(f"❌ Error reading ConfigService: {e}")
        return False

def test_static_image_serving():
    """Test that static image serving is configured"""
    print("🔍 Testing Static Image Serving...")
    
    main_py = Path("aphrodite-web/app/main.py")
    if not main_py.exists():
        print("❌ main.py not found")
        return False
    
    try:
        with open(main_py, 'r') as f:
            content = f.read()
        
        if '/images/<path:filename>' not in content:
            print("❌ Image serving route not found in main.py")
            return False
        
        if 'serve_images' not in content:
            print("❌ serve_images function not found in main.py")
            return False
        
        print("✅ Static image serving is configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False

def test_awards_color_schemes():
    """Test that all color schemes have required award images"""
    print("🔍 Testing Awards Color Schemes...")
    
    awards_dir = Path("images/awards")
    if not awards_dir.exists():
        print("❌ Awards images directory not found")
        return False
    
    # Basic award types that should exist
    basic_awards = ['oscars.png', 'emmys.png', 'golden.png', 'bafta.png', 'cannes.png']
    color_schemes = ['black', 'gray', 'red', 'yellow']
    
    missing_images = []
    
    for color in color_schemes:
        color_dir = awards_dir / color
        if not color_dir.exists():
            print(f"❌ Color directory {color} not found")
            return False
        
        for award in basic_awards:
            award_file = color_dir / award
            if not award_file.exists():
                missing_images.append(f"{color}/{award}")
    
    if missing_images:
        print(f"❌ Missing award images: {missing_images}")
        return False
    
    print("✅ All color schemes have required award images")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Aphrodite Awards Badge Web Integration - Phase 3")
    print("=" * 60)
    
    tests = [
        test_awards_badge_files,
        test_awards_configuration,
        test_web_components,
        test_backend_config_service,
        test_static_image_serving,
        test_awards_color_schemes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Awards Badge Web Integration is ready.")
        print("\n📋 Next Steps:")
        print("1. Start the web server: cd aphrodite-web && python main.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Navigate to Settings → Awards tab")
        print("4. Configure awards badges (enable, select color scheme, choose sources)")
        print("5. Test with a known award-winning movie/TV show")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
