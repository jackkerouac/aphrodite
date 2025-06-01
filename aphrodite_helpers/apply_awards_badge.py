#!/usr/bin/env python3
# aphrodite_helpers/apply_awards_badge.py

import os
import sys
from PIL import Image

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.get_awards_info import AwardsFetcher
from aphrodite_helpers.badge_components.badge_generator import create_badge
from aphrodite_helpers.badge_components.badge_applicator import apply_badge_to_poster

def process_item_awards(item_id, jellyfin_url, api_key, user_id, settings_file, working_poster_path):
    """Process and apply awards badge to a poster"""
    try:
        print(f"🏆 Processing awards badge for item: {item_id}")
        
        # Load settings
        settings = load_settings()
        
        # Load awards badge settings
        awards_settings = load_awards_badge_settings(settings_file)
        if not awards_settings:
            print("⚠️ Awards badge settings not found")
            return False
        
        # Check if awards badges are enabled
        if not awards_settings.get("General", {}).get("enabled", True):
            print("ℹ️ Awards badges are disabled")
            return True  # Not an error, just disabled
        
        # Create awards fetcher
        awards_fetcher = AwardsFetcher(settings)
        
        # Get awards information
        awards_info = awards_fetcher.get_media_awards_info(jellyfin_url, api_key, user_id, item_id)
        
        if not awards_info:
            print("ℹ️ No awards found for this item")
            return True  # Not an error, just no awards
        
        award_type = awards_info["award_type"]
        print(f"🏆 Found award: {award_type}")
        
        # Get color scheme from settings
        color_scheme = awards_settings.get("Awards", {}).get("color_scheme", "black")
        
        # Create badge
        badge_image = create_badge(awards_settings, award_type)
        if not badge_image:
            print(f"❌ Failed to create badge for award: {award_type}")
            return False
        
        # Apply badge with flush positioning
        result_path = apply_awards_badge_flush(working_poster_path, badge_image, color_scheme)
        
        if result_path and os.path.exists(result_path):
            print(f"✅ Awards badge applied successfully")
            return result_path
        else:
            print(f"❌ Failed to apply awards badge")
            return False
            
    except Exception as e:
        print(f"❌ Error processing awards badge: {e}")
        return False

def apply_awards_badge_flush(poster_path, badge_image, color_scheme):
    """Apply awards badge flush to bottom-right corner"""
    try:
        # Load poster
        poster = Image.open(poster_path).convert("RGBA")
        
        # Ensure badge is in RGBA mode
        if isinstance(badge_image, str):
            # If badge_image is a path
            badge = Image.open(badge_image).convert("RGBA")
        else:
            # If badge_image is already a PIL Image
            badge = badge_image.convert("RGBA")
        
        # Calculate flush position (bottom-right corner, no padding)
        x = poster.width - badge.width
        y = poster.height - badge.height
        
        # Ensure position is not negative
        x = max(0, x)
        y = max(0, y)
        
        # Apply badge to poster
        poster.paste(badge, (x, y), badge)
        
        # Save the result
        poster.save(poster_path)
        print(f"🏆 Awards badge applied at position ({x}, {y}) with flush positioning")
        
        return poster_path
        
    except Exception as e:
        print(f"❌ Error applying awards badge: {e}")
        return None

def load_awards_badge_settings(settings_file="badge_settings_awards.yml"):
    """Load awards badge settings"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(root_dir, settings_file)
        
        with open(full_path, 'r') as f:
            import yaml
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️ Warning: Could not load awards badge settings: {e}")
        return None

def validate_awards_badge_image(award_type, color_scheme="black"):
    """Validate that the awards badge image exists"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(root_dir, "images", "awards", color_scheme, f"{award_type}.png")
        
        return os.path.exists(image_path)
    except Exception as e:
        print(f"⚠️ Error validating awards badge image: {e}")
        return False

def get_available_award_images(color_scheme="black"):
    """Get list of available award images for a color scheme"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        awards_dir = os.path.join(root_dir, "images", "awards", color_scheme)
        
        if not os.path.exists(awards_dir):
            return []
        
        award_images = []
        for file in os.listdir(awards_dir):
            if file.endswith('.png'):
                award_type = file.replace('.png', '')
                award_images.append(award_type)
        
        return award_images
        
    except Exception as e:
        print(f"⚠️ Error getting available award images: {e}")
        return []

def test_awards_badge_system():
    """Test the awards badge system with sample data"""
    try:
        print("🧪 Testing Awards Badge System")
        print("=" * 40)
        
        # Test available color schemes
        color_schemes = ["black", "gray", "red", "yellow"]
        
        for scheme in color_schemes:
            print(f"\n📁 Color Scheme: {scheme}")
            available_awards = get_available_award_images(scheme)
            if available_awards:
                print(f"   Available awards: {', '.join(available_awards)}")
            else:
                print(f"   ⚠️ No award images found for {scheme} scheme")
        
        # Test award validation
        test_awards = ["oscars", "emmys", "golden", "bafta", "cannes"]
        print(f"\n🔍 Testing Award Image Validation:")
        
        for award in test_awards:
            exists = validate_awards_badge_image(award, "black")
            status = "✅" if exists else "❌"
            print(f"   {status} {award}.png")
        
        print("\n🧪 Awards badge system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing awards badge system: {e}")
        return False

if __name__ == "__main__":
    """Command line interface for testing awards badge functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test awards badge functionality")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--validate", help="Validate specific award image (e.g., 'oscars')")
    parser.add_argument("--color", default="black", help="Color scheme to test (default: black)")
    parser.add_argument("--list", action="store_true", help="List available award images")
    
    args = parser.parse_args()
    
    if args.test:
        test_awards_badge_system()
    elif args.validate:
        exists = validate_awards_badge_image(args.validate, args.color)
        status = "✅ Found" if exists else "❌ Not found"
        print(f"{status}: {args.validate}.png in {args.color} scheme")
    elif args.list:
        print(f"Available award images in {args.color} scheme:")
        awards = get_available_award_images(args.color)
        if awards:
            for award in sorted(awards):
                print(f"  • {award}")
        else:
            print(f"  No awards found in {args.color} scheme")
    else:
        print("Use --help for usage information")
