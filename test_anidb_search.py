#!/usr/bin/env python3
# test_anidb_search.py - Test AniDB search functionality

import sys
import os

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from aphrodite_helpers.get_review_info import ReviewFetcher
from aphrodite_helpers.settings_validator import load_settings

def test_title_search():
    print("🧪 Testing AniDB title search functionality...")
    
    # Load settings
    settings = load_settings()
    if not settings:
        print("❌ Failed to load settings")
        return False
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    # Test searching for a well-known anime
    test_title = "Aharen-san wa Hakarenai"
    print(f"\n🔍 Testing search for: {test_title}")
    
    # Test the search function directly
    anidb_id = review_fetcher.search_anidb_by_title(test_title)
    print(f"🔍 Search result: {anidb_id}")
    
    if anidb_id:
        # Test fetching rating
        print(f"\n🔍 Testing rating fetch for ID: {anidb_id}")
        rating_data = review_fetcher.fetch_anidb_anime_info(anidb_id)
        print(f"🔍 Rating data: {rating_data}")
        
        if rating_data:
            print(f"✅ Success! Found rating: {rating_data.get('rating', 'N/A')}")
        else:
            print("❌ Failed to fetch rating data")
    else:
        print("❌ Failed to find AniDB ID for title")
    
    return True

def test_full_review_fetch():
    print("\n🧪 Testing full review fetch with AniDB...")
    
    # Load settings
    settings = load_settings()
    if not settings:
        print("❌ Failed to load settings")
        return False
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    # Test with a mock item data (simulating Jellyfin metadata without AniDB ID)
    mock_item_data = {
        "Name": "Aharen-san wa Hakarenai",
        "Type": "Series",
        "ProviderIds": {
            "Imdb": "tt19648600",  # Example IMDB ID
            "Tmdb": "154749"       # Example TMDB ID
            # Note: No AniDB ID - this will trigger title search
        }
    }
    
    print(f"📺 Mock item: {mock_item_data['Name']}")
    print(f"🆔 Provider IDs: {mock_item_data['ProviderIds']}")
    
    # Test AniDB ID extraction (should be None)
    anidb_id = review_fetcher.get_anidb_id(mock_item_data)
    print(f"🔍 AniDB ID from metadata: {anidb_id}")
    
    # Test the full AniDB fetch (should trigger title search)
    print(f"\n🔍 Testing full AniDB fetch...")
    result = review_fetcher.fetch_anidb_ratings(anidb_id, mock_item_data.get('Name'))
    print(f"🔍 AniDB fetch result: {result}")
    
    if result:
        print(f"✅ Success! AniDB rating: {result.get('rating', 'N/A')}")
    else:
        print("❌ No AniDB rating found")
    
    return True

if __name__ == "__main__":
    try:
        test_title_search()
        test_full_review_fetch()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        print(traceback.format_exc())
