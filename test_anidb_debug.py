#!/usr/bin/env python3
# test_anidb_debug.py - Test script to check AniDB review functionality

import sys
import os

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from aphrodite_helpers.get_review_info import ReviewFetcher
from aphrodite_helpers.settings_validator import load_settings

def test_anidb_reviews():
    print("🧪 Testing AniDB review functionality...")
    
    # Load settings
    settings = load_settings()
    if not settings:
        print("❌ Failed to load settings")
        return False
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    # Check AniDB settings
    print(f"🔍 AniDB settings loaded: {bool(review_fetcher.anidb_settings)}")
    if review_fetcher.anidb_settings:
        print(f"🔍 AniDB settings: {review_fetcher.anidb_settings}")
    
    # Test with the item ID from your log
    item_id = "263c101971f0bd50317e17fbc58ab7d5"
    print(f"\n🔍 Testing with item ID: {item_id}")
    
    # Get item metadata
    item_data = review_fetcher.get_jellyfin_item_metadata(item_id)
    if not item_data:
        print("❌ Could not retrieve item metadata")
        return False
    
    print(f"📺 Item: {item_data.get('Name', 'Unknown')}")
    print(f"📝 Type: {item_data.get('Type', 'Unknown')}")
    
    # Check provider IDs
    provider_ids = item_data.get("ProviderIds", {})
    print(f"🆔 Provider IDs: {provider_ids}")
    
    # Get reviews
    print(f"\n🔍 Fetching reviews...")
    reviews = review_fetcher.get_reviews(item_id, show_details=True)
    
    print(f"\n✅ Found {len(reviews)} reviews:")
    for review in reviews:
        print(f"  - {review.get('source', 'Unknown')}: {review.get('rating', 'N/A')}")
    
    return True

if __name__ == "__main__":
    try:
        test_anidb_reviews()
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        print(traceback.format_exc())
