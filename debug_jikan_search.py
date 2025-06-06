#!/usr/bin/env python3
"""
Debug script to test Jikan API search results for different anime titles
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.jikan_api import JikanAPI


def search_and_display(jikan, query, description=""):
    """Search for an anime and display detailed results"""
    print(f"\n🔍 Searching for: '{query}' {description}")
    print("-" * 60)
    
    try:
        result = jikan.search_anime(query, limit=10)
        
        if not result or "data" not in result:
            print(f"❌ No results found")
            return []
        
        anime_list = result["data"]
        
        if not anime_list:
            print(f"❌ Empty results")
            return []
        
        print(f"✅ Found {len(anime_list)} results:")
        
        for i, anime in enumerate(anime_list, 1):
            print(f"\n{i}. {anime.get('title', 'Unknown Title')}")
            print(f"   MAL ID: {anime.get('mal_id', 'N/A')}")
            print(f"   English: {anime.get('title_english', 'N/A')}")
            print(f"   Japanese: {anime.get('title_japanese', 'N/A')}")
            print(f"   Score: {anime.get('score', 'N/A')}/10")
            print(f"   Year: {anime.get('year', 'N/A')}")
            print(f"   Type: {anime.get('type', 'N/A')}")
            print(f"   Status: {anime.get('status', 'N/A')}")
            
            # Show alternative titles if available
            if "titles" in anime and anime["titles"]:
                alt_titles = []
                for title_obj in anime["titles"]:
                    title_type = title_obj.get("type", "")
                    title = title_obj.get("title", "")
                    if title and title != anime.get('title'):
                        alt_titles.append(f"{title} ({title_type})")
                
                if alt_titles:
                    print(f"   Alt titles: {', '.join(alt_titles[:3])}")  # Show first 3
        
        return anime_list
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def test_specific_anime_details(jikan, mal_id):
    """Test getting details for a specific MAL ID"""
    print(f"\n📺 Getting details for MAL ID: {mal_id}")
    print("-" * 60)
    
    try:
        result = jikan.get_anime_details(mal_id)
        
        if not result or "data" not in result:
            print(f"❌ No details found")
            return None
        
        anime = result["data"]
        
        print(f"✅ Details found:")
        print(f"   Title: {anime.get('title', 'N/A')}")
        print(f"   English: {anime.get('title_english', 'N/A')}")
        print(f"   Japanese: {anime.get('title_japanese', 'N/A')}")
        print(f"   Score: {anime.get('score', 'N/A')}/10")
        print(f"   Scored by: {anime.get('scored_by', 'N/A')} users")
        print(f"   Rank: #{anime.get('rank', 'N/A')}")
        print(f"   Popularity: #{anime.get('popularity', 'N/A')}")
        print(f"   Type: {anime.get('type', 'N/A')}")
        print(f"   Episodes: {anime.get('episodes', 'N/A')}")
        print(f"   Status: {anime.get('status', 'N/A')}")
        print(f"   Year: {anime.get('year', 'N/A')}")
        print(f"   Season: {anime.get('season', 'N/A')}")
        
        # Show all title variations
        if "titles" in anime and anime["titles"]:
            print(f"\n   All title variations:")
            for title_obj in anime["titles"]:
                title_type = title_obj.get("type", "")
                title = title_obj.get("title", "")
                print(f"     - {title} ({title_type})")
        
        return anime
        
    except Exception as e:
        print(f"❌ Details failed: {e}")
        return None


def test_find_by_title(jikan, title):
    """Test the find_anime_by_title method"""
    print(f"\n🎯 Testing find_anime_by_title for: '{title}'")
    print("-" * 60)
    
    try:
        result = jikan.find_anime_by_title(title)
        
        if not result:
            print(f"❌ No match found")
            return None
        
        if "data" not in result:
            print(f"❌ Invalid result format")
            return None
        
        anime = result["data"]
        
        print(f"✅ Best match found:")
        print(f"   Title: {anime.get('title', 'N/A')}")
        print(f"   MAL ID: {anime.get('mal_id', 'N/A')}")
        print(f"   English: {anime.get('title_english', 'N/A')}")
        print(f"   Japanese: {anime.get('title_japanese', 'N/A')}")
        print(f"   Score: {anime.get('score', 'N/A')}/10")
        
        return anime
        
    except Exception as e:
        print(f"❌ Find by title failed: {e}")
        return None


def main():
    """Main debugging function"""
    print("🐛 Jikan API Search Debug Tool")
    print("=" * 80)
    
    # Initialize Jikan API
    jikan = JikanAPI()
    
    # Test different search variations for "A Returner's Magic Should Be Special"
    search_queries = [
        ("A Returner's Magic Should Be Special", "(English title from Jellyfin)"),
        ("Kikansha no Mahou wa Tokubetsu desu", "(Japanese title from MAL)"),
        ("Returner Magic Special", "(Shortened English)"),
        ("Kikansha no Mahou", "(Shortened Japanese)"),
        ("returner magic", "(Simple search)"),
        ("A Returner's Magic", "(Partial English)")
    ]
    
    all_results = {}
    
    for query, desc in search_queries:
        results = search_and_display(jikan, query, desc)
        all_results[query] = results
    
    # Test the find_anime_by_title method
    test_titles = [
        "A Returner's Magic Should Be Special",
        "Kikansha no Mahou wa Tokubetsu desu"
    ]
    
    for title in test_titles:
        test_find_by_title(jikan, title)
    
    # If we found any results, test getting details for the first few
    print(f"\n📋 TESTING SPECIFIC ANIME DETAILS")
    print("=" * 80)
    
    tested_ids = set()
    for query, results in all_results.items():
        for anime in results[:2]:  # Test first 2 from each search
            mal_id = anime.get('mal_id')
            if mal_id and mal_id not in tested_ids:
                test_specific_anime_details(jikan, mal_id)
                tested_ids.add(mal_id)
    
    # Manual test for known MAL ID (if we can find it)
    print(f"\n🔍 MANUAL SEARCH ON MYANIMELIST.NET")
    print("=" * 80)
    print(f"Please manually search for 'A Returner's Magic Should Be Special' on MyAnimeList.net")
    print(f"and provide the MAL ID if found. Common patterns:")
    print(f"  - URL like: https://myanimelist.net/anime/XXXXX/...")
    print(f"  - The XXXXX number is the MAL ID")
    
    # Summary
    print(f"\n📊 SEARCH SUMMARY")
    print("=" * 80)
    
    for query, results in all_results.items():
        count = len(results)
        if count > 0:
            first_title = results[0].get('title', 'Unknown')
            first_id = results[0].get('mal_id', 'N/A')
            print(f"✅ '{query}': {count} results (top: {first_title} - {first_id})")
        else:
            print(f"❌ '{query}': No results")
    
    print(f"\n💡 RECOMMENDATIONS:")
    
    # Find the query that returned the most results
    best_query = max(all_results.keys(), key=lambda k: len(all_results[k]))
    best_count = len(all_results[best_query])
    
    if best_count > 0:
        print(f"   1. Best search term: '{best_query}' ({best_count} results)")
        best_result = all_results[best_query][0]
        print(f"   2. Top match: {best_result.get('title')} (ID: {best_result.get('mal_id')})")
        print(f"   3. Consider updating search logic to handle Japanese titles")
    else:
        print(f"   1. No results found with any search term")
        print(f"   2. The anime might not be in MyAnimeList database")
        print(f"   3. Try manual search on MyAnimeList.net")
    
    # Suggestions for improving the search
    print(f"\n🔧 SEARCH IMPROVEMENT SUGGESTIONS:")
    print(f"   1. Try removing special characters: apostrophes, colons, etc.")
    print(f"   2. Search with both English and Japanese titles")
    print(f"   3. Use AniList ID to find MAL ID via mapping services")
    print(f"   4. Implement fuzzy matching for similar titles")


if __name__ == "__main__":
    main()
