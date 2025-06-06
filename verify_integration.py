#!/usr/bin/env python3
"""
Quick verification script for Jikan and Metacritic integration
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.jikan_api import JikanAPI
from aphrodite_helpers.review_preferences import ReviewPreferences
import requests


def test_jikan_api_directly():
    """Test Jikan API directly"""
    print("🧪 Testing Jikan API directly...")
    
    jikan = JikanAPI()
    
    # Test search
    search_result = jikan.search_anime("Attack on Titan", limit=3)
    if search_result and "data" in search_result:
        print(f"✅ Jikan search working - found {len(search_result['data'])} results")
        first_anime = search_result['data'][0]
        print(f"   First result: {first_anime.get('title')} (ID: {first_anime.get('mal_id')})")
    else:
        print(f"❌ Jikan search failed")
        return False
    
    # Test details
    anime_details = jikan.get_anime_details(16498)  # Attack on Titan
    if anime_details and "data" in anime_details:
        anime = anime_details['data']
        print(f"✅ Jikan details working - {anime.get('title')} score: {anime.get('score')}")
    else:
        print(f"❌ Jikan details failed")
        return False
    
    return True


def test_omdb_metacritic():
    """Test OMDb API for Metacritic data"""
    print("\n🧪 Testing OMDb API for Metacritic...")
    
    # Check if we have OMDb API key in settings
    try:
        from aphrodite_helpers.settings_validator import load_settings
        settings = load_settings("settings.yaml")
        omdb_settings = settings.get("api_keys", {}).get("OMDB", [{}])[0]
        api_key = omdb_settings.get("api_key")
        
        if not api_key:
            print(f"⚠️  No OMDb API key found - testing with free tier")
            params = {"t": "Dune", "y": "2021", "plot": "short", "r": "json"}
        else:
            print(f"✅ OMDb API key found - using authenticated requests")
            params = {"t": "Dune", "y": "2021", "plot": "short", "r": "json", "apikey": api_key}
        
        response = requests.get("http://www.omdbapi.com/", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                print(f"✅ OMDb working - found: {data.get('Title')} ({data.get('Year')})")
                
                # Check for Metacritic in ratings
                ratings = data.get("Ratings", [])
                metacritic_found = False
                for rating in ratings:
                    if rating.get("Source") == "Metacritic":
                        metacritic_found = True
                        print(f"✅ Metacritic data found: {rating.get('Value')}")
                        break
                
                if not metacritic_found:
                    print(f"⚠️  No Metacritic data in OMDb response")
                    print(f"   Available sources: {[r.get('Source') for r in ratings]}")
                
                return metacritic_found
            else:
                print(f"❌ OMDb error: {data.get('Error', 'Unknown error')}")
        else:
            print(f"❌ OMDb request failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ OMDb test failed: {e}")
    
    return False


def test_database_settings():
    """Test database settings for review sources"""
    print("\n🧪 Testing database review source settings...")
    
    try:
        prefs = ReviewPreferences()
        enabled_sources = prefs.get_enabled_sources()
        
        metacritic_enabled = any(s['name'] == 'Metacritic' for s in enabled_sources)
        myanimelist_enabled = any(s['name'] == 'MyAnimeList' for s in enabled_sources)
        
        print(f"✅ Database connection working")
        print(f"   Metacritic enabled: {'✅ Yes' if metacritic_enabled else '❌ No'}")
        print(f"   MyAnimeList enabled: {'✅ Yes' if myanimelist_enabled else '❌ No'}")
        print(f"   Total enabled sources: {len(enabled_sources)}")
        
        return metacritic_enabled, myanimelist_enabled
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False, False


def main():
    """Run verification tests"""
    print("🔍 Verification: Jikan + Metacritic Integration")
    print("=" * 50)
    
    # Test components individually
    jikan_works = test_jikan_api_directly()
    omdb_metacritic_works = test_omdb_metacritic()
    metacritic_enabled, myanimelist_enabled = test_database_settings()
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    print(f"🔧 Component Status:")
    print(f"   Jikan API: {'✅ Working' if jikan_works else '❌ Failed'}")
    print(f"   OMDb + Metacritic: {'✅ Working' if omdb_metacritic_works else '❌ Failed'}")
    print(f"   Database: {'✅ Working' if (metacritic_enabled or myanimelist_enabled) else '❌ Failed'}")
    
    print(f"\n🎯 Integration Status:")
    integration_ready = True
    
    if myanimelist_enabled and jikan_works:
        print(f"   MyAnimeList via Jikan: ✅ Ready")
    else:
        print(f"   MyAnimeList via Jikan: ❌ Not ready")
        if not myanimelist_enabled:
            print(f"     - Enable MyAnimeList in review sources")
        if not jikan_works:
            print(f"     - Jikan API connection failed")
        integration_ready = False
    
    if metacritic_enabled and omdb_metacritic_works:
        print(f"   Metacritic via OMDb: ✅ Ready")
    else:
        print(f"   Metacritic via OMDb: ❌ Not ready")
        if not metacritic_enabled:
            print(f"     - Enable Metacritic in review sources")
        if not omdb_metacritic_works:
            print(f"     - OMDb API or Metacritic data issue")
        integration_ready = False
    
    if integration_ready:
        print(f"\n🎉 Both integrations are ready!")
        print(f"   ✅ Users can now enable MyAnimeList in Review Settings")
        print(f"   ✅ Metacritic should show when OMDb has the data")
    else:
        print(f"\n⚠️  Some setup needed - see issues above")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Run the full test: python test_review_integration.py")
    print(f"   2. Check Review Settings UI for source toggles")
    print(f"   3. Test with actual media items")


if __name__ == "__main__":
    main()
