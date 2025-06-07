#!/usr/bin/env python3
"""
Quick debug script to test MyAnimeList fetching with verbose logging
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def debug_myanimelist_fetching():
    """Debug MyAnimeList fetching with enhanced mapping"""
    print("🔍 Debug: Testing MyAnimeList Fetching")
    print("=" * 50)
    
    try:
        # Load settings
        from aphrodite_helpers.settings_validator import load_settings
        settings = load_settings("settings.yaml")
        print("✅ Settings loaded")
        
        # Import enhanced ReviewFetcher
        try:
            from production_anime_mapping import enhance_review_fetcher
            from aphrodite_helpers.get_review_info import ReviewFetcher as BaseReviewFetcher
            ReviewFetcher = enhance_review_fetcher(BaseReviewFetcher)
            print("✅ Enhanced ReviewFetcher loaded")
        except Exception as e:
            from aphrodite_helpers.get_review_info import ReviewFetcher
            print(f"⚠️ Using original ReviewFetcher: {e}")
        
        # Create fetcher instance
        fetcher = ReviewFetcher(settings)
        print("✅ ReviewFetcher instance created")
        
        # Test data (known to work)
        test_data = {
            "Name": "A Returner's Magic Should Be Special",
            "Type": "Series", 
            "Genres": ["Animation", "Anime"],
            "ProviderIds": {
                "AniDB": "17944",
                "AniList": "126579",
                "Tmdb": "155837"
            }
        }
        
        print(f"\n🧪 Testing with anime: {test_data['Name']}")
        print(f"   Provider IDs: {test_data['ProviderIds']}")
        
        # Test MyAnimeList fetching directly
        print("\n📺 Testing MyAnimeList fetching...")
        mal_result = fetcher.fetch_myanimelist_ratings(
            mal_id=None,
            item_name=test_data['Name'],
            item_data=test_data
        )
        
        if mal_result:
            print("✅ MyAnimeList result:")
            print(f"   Title: {mal_result.get('title')}")
            print(f"   MAL ID: {mal_result.get('mal_id')}")
            print(f"   Rating: {mal_result.get('rating')}/10")
            print(f"   Rank: #{mal_result.get('rank')}")
        else:
            print("❌ No MyAnimeList result")
            
        # Test complete review fetching
        print("\n📊 Testing complete review fetching...")
        from aphrodite_helpers.review_preferences import ReviewPreferences
        
        prefs = ReviewPreferences()
        
        # Check anime detection
        is_anime = prefs._is_anime_content(test_data)
        print(f"   Detected as anime: {is_anime}")
        
        # Check if MyAnimeList should be included
        should_include = prefs.should_include_source('MyAnimeList', test_data)
        print(f"   Should include MyAnimeList: {should_include}")
        
        # Mock some review data to test filtering
        mock_reviews = []
        
        if mal_result:
            mock_reviews.append({
                "source": "MyAnimeList",
                "rating": f"{int(mal_result['rating'] * 10)}%",
                "original_rating": str(mal_result['rating']),
                "max_rating": "100%",
                "image_key": "MAL"
            })
        
        # Add TMDb for comparison
        mock_reviews.append({
            "source": "TMDb",
            "rating": "82%",
            "image_key": "TMDb"
        })
        
        print(f"\n   Mock reviews created: {len(mock_reviews)}")
        for review in mock_reviews:
            print(f"      - {review['source']}: {review['rating']}")
        
        # Filter reviews using preferences
        filtered_reviews = prefs.filter_and_order_reviews(mock_reviews, test_data)
        
        print(f"\n   Filtered reviews: {len(filtered_reviews)}")
        for review in filtered_reviews:
            print(f"      - {review['source']}: {review['rating']}")
        
        # Check if MyAnimeList made it through
        mal_in_final = any(r.get('source') == 'MyAnimeList' for r in filtered_reviews)
        print(f"\n   MyAnimeList in final results: {mal_in_final}")
        
        if mal_in_final:
            print("🎉 SUCCESS: MyAnimeList reviews are working!")
        else:
            print("❌ ISSUE: MyAnimeList reviews are being filtered out")
            
        return mal_in_final
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = debug_myanimelist_fetching()
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug found issues")
