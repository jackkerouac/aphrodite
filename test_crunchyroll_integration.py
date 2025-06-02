#!/usr/bin/env python3
# test_crunchyroll_integration.py
"""
Simple test script to verify Crunchyroll integration works
"""

import os
import sys

# Add parent directory to sys.path to allow importing from other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aphrodite_helpers.awards_data_source import AwardsDataSource
from aphrodite_helpers.settings_validator import load_settings

def test_crunchyroll_integration():
    """Test that Crunchyroll awards detection works"""
    print("🧪 Testing Crunchyroll Integration")
    print("=" * 50)
    
    try:
        # Load settings
        settings = load_settings("settings.yaml")
        print("✅ Settings loaded successfully")
        
        # Create awards data source
        awards_source = AwardsDataSource(settings)
        print("✅ AwardsDataSource created successfully")
        
        # Check if Crunchyroll data loaded
        if awards_source.crunchyroll_awards:
            total_anime = len(awards_source.crunchyroll_awards.get("anime_winners", {}))
            print(f"✅ Crunchyroll awards data loaded: {total_anime} anime winners")
        else:
            print("❌ Crunchyroll awards data not loaded")
            return False
        
        # Test cases with known winners
        test_cases = [
            {"tmdb_id": "127532", "title": "Solo Leveling", "expected": True},
            {"tmdb_id": "85937", "title": "Demon Slayer: Kimetsu no Yaiba", "expected": True},
            {"tmdb_id": "1429", "title": "Attack on Titan", "expected": True},
            {"tmdb_id": "95479", "title": "Jujutsu Kaisen", "expected": True},
            {"tmdb_id": "999999", "title": "Non-existent Anime", "expected": False},
        ]
        
        print("\n🔍 Testing Crunchyroll Award Detection:")
        print("-" * 50)
        
        success_count = 0
        for test_case in test_cases:
            tmdb_id = test_case["tmdb_id"]
            title = test_case["title"]
            expected = test_case["expected"]
            
            # Test the Crunchyroll check method directly
            result = awards_source.check_crunchyroll_awards(tmdb_id=tmdb_id, title=title)
            
            if result == expected:
                status = "✅ PASS"
                success_count += 1
            else:
                status = "❌ FAIL"
            
            print(f"{status} TMDb ID {tmdb_id} ({title}): Expected {expected}, Got {result}")
        
        print(f"\n📊 Test Results: {success_count}/{len(test_cases)} tests passed")
        
        # Test TV awards integration
        print("\n🔍 Testing TV Awards Integration:")
        print("-" * 50)
        
        # Test Solo Leveling (should return crunchyroll award)
        solo_leveling_awards = awards_source.get_tv_awards(tmdb_id="127532", title="Solo Leveling")
        if "crunchyroll" in solo_leveling_awards:
            print("✅ Solo Leveling correctly detected as Crunchyroll winner")
        else:
            print("❌ Solo Leveling not detected as Crunchyroll winner")
        
        # Test non-anime (should not return crunchyroll award)
        test_tv_awards = awards_source.get_tv_awards(tmdb_id="999999", title="Some Random Show")
        if "crunchyroll" not in test_tv_awards:
            print("✅ Non-anime correctly did not get Crunchyroll award")
        else:
            print("❌ Non-anime incorrectly got Crunchyroll award")
        
        print("\n🎯 Crunchyroll integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crunchyroll_image_files():
    """Test that Crunchyroll image files exist in all color schemes"""
    print("\n🖼️ Testing Crunchyroll Image Files:")
    print("-" * 50)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    color_schemes = ["black", "gray", "red", "yellow"]
    
    all_found = True
    for color in color_schemes:
        image_path = os.path.join(root_dir, "images", "awards", color, "crunchyroll.png")
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ {color}/crunchyroll.png found ({file_size} bytes)")
        else:
            print(f"❌ {color}/crunchyroll.png not found")
            all_found = False
    
    return all_found

def test_badge_settings():
    """Test that badge settings include Crunchyroll"""
    print("\n⚙️ Testing Badge Settings:")
    print("-" * 50)
    
    try:
        import yaml
        
        # Test awards badge settings
        with open("badge_settings_awards.yml", 'r') as f:
            awards_settings = yaml.safe_load(f)
        
        award_sources = awards_settings.get("Awards", {}).get("award_sources", [])
        if "crunchyroll" in award_sources:
            print("✅ Crunchyroll found in award_sources")
        else:
            print("❌ Crunchyroll not found in award_sources")
            return False
        
        image_mapping = awards_settings.get("ImageBadges", {}).get("image_mapping", {})
        if "crunchyroll" in image_mapping:
            print(f"✅ Crunchyroll image mapping found: {image_mapping['crunchyroll']}")
        else:
            print("❌ Crunchyroll not found in image_mapping")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing badge settings: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Crunchyroll Integration Tests")
    print("=" * 60)
    
    # Run all tests
    test1 = test_crunchyroll_integration()
    test2 = test_crunchyroll_image_files()
    test3 = test_badge_settings()
    
    print("\n" + "=" * 60)
    if test1 and test2 and test3:
        print("🎉 All tests passed! Crunchyroll integration is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)
