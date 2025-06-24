#!/usr/bin/env python3
"""
Test script to diagnose MyAnimeList badge issues
"""

import asyncio
import sys
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mal_badge():
    """Test MAL badge creation step by step"""
    
    # Test 1: Check if MAL is enabled in settings
    print("🔍 Test 1: Checking MAL settings...")
    try:
        from api.app.services.badge_processing.database_service import badge_settings_service
        
        # Load review source settings
        review_source_settings = await badge_settings_service.get_review_source_settings_standalone(force_reload=True)
        print(f"Review source settings: {review_source_settings}")
        
        if review_source_settings:
            mal_enabled = review_source_settings.get('enable_myanimelist', False)
            print(f"MyAnimeList enabled: {mal_enabled}")
            
            # Show all enabled sources
            enabled_sources = []
            for key, value in review_source_settings.items():
                if key.startswith('enable_') and value:
                    source_name = key.replace('enable_', '').replace('_', ' ').title()
                    enabled_sources.append(source_name)
            print(f"Enabled review sources: {enabled_sources}")
        else:
            print("❌ No review source settings found!")
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Test MAL API directly
    print("🔍 Test 2: Testing MAL/Jikan API...")
    try:
        from aphrodite_helpers.jikan_api import JikanAPI
        
        jikan = JikanAPI()
        print("JikanAPI imported successfully")
        
        # Test search for a known anime
        test_title = "Demon Slayer"
        print(f"Searching for: {test_title}")
        
        search_result = jikan.search_anime(test_title, limit=3)
        if search_result and search_result.get('data'):
            print(f"Found {len(search_result['data'])} results")
            for anime in search_result['data'][:2]:
                print(f"  - {anime.get('title')} (ID: {anime.get('mal_id')}, Score: {anime.get('score')})")
        else:
            print("❌ No search results")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ API error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Test the review detector MAL function
    print("🔍 Test 3: Testing review detector MAL function...")
    try:
        from api.app.services.badge_processing.review_detector import get_review_detector
        
        detector = get_review_detector()
        print("Review detector loaded")
        
        # Simulate anime content (series type)
        fake_settings = {
            'Sources': {
                'enable_myanimelist': True,
                'enable_imdb': True,
                'enable_tmdb': True
            }
        }
        
        # Test MAL rating fetch directly
        mal_result = await detector._fetch_myanimelist_rating(
            mal_id=None, 
            anilist_id=None, 
            title="Demon Slayer", 
            settings=fake_settings
        )
        
        if mal_result:
            print(f"✅ MAL result: {mal_result}")
        else:
            print("❌ No MAL result returned")
            
    except Exception as e:
        print(f"❌ Error testing MAL function: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Test demo review data
    print("🔍 Test 4: Testing demo review generation with MAL enabled...")
    try:
        from api.app.services.badge_processing.review_detector import get_review_detector
        
        detector = get_review_detector()
        
        # Settings with MAL enabled
        settings_with_mal = {
            'Sources': {
                'enable_imdb': True,
                'enable_tmdb': True,
                'enable_myanimelist': True,  # Enable MAL
                'enable_rotten_tomatoes_critics': False,
                'enable_metacritic': False
            }
        }
        
        demo_reviews = detector.get_demo_reviews("test_anime_poster.jpg", settings_with_mal)
        print(f"Demo reviews generated: {len(demo_reviews)}")
        
        for review in demo_reviews:
            source = review.get('source', 'Unknown')
            text = review.get('text', 'N/A')
            print(f"  - {source}: {text}")
            
        # Check if MAL is included
        mal_reviews = [r for r in demo_reviews if 'anime' in r.get('source', '').lower()]
        if mal_reviews:
            print(f"✅ MAL included in demo reviews")
        else:
            print("❌ MAL NOT included in demo reviews")
            
    except Exception as e:
        print(f"❌ Error testing demo reviews: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mal_badge())
