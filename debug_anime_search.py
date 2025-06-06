#!/usr/bin/env python3
"""
Enhanced title search and matching for anime
"""

import sys
import os
import re

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.jikan_api import JikanAPI


def clean_title_variations(title):
    """Generate multiple search variations of a title"""
    variations = [title]  # Original title
    
    # Remove special characters and punctuation
    cleaned = re.sub(r'[^\w\s]', '', title)
    if cleaned != title:
        variations.append(cleaned)
    
    # Remove articles (A, An, The)
    no_articles = re.sub(r'^(A|An|The)\s+', '', title, flags=re.IGNORECASE)
    if no_articles != title:
        variations.append(no_articles)
    
    # Remove possessives ('s)
    no_possessive = re.sub(r"'s\b", '', title)
    if no_possessive != title:
        variations.append(no_possessive)
    
    # Replace apostrophes with nothing
    no_apostrophe = title.replace("'", "")
    if no_apostrophe != title:
        variations.append(no_apostrophe)
    
    # Simplified version (keep only alphanumeric and spaces)
    simple = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
    simple = re.sub(r'\s+', ' ', simple).strip()
    if simple != title:
        variations.append(simple)
    
    # Very short version (first few important words)
    words = title.split()
    if len(words) > 2:
        short = ' '.join(words[:3])  # First 3 words
        variations.append(short)
    
    # Remove duplicates while preserving order
    unique_variations = []
    for var in variations:
        if var and var.strip() and var not in unique_variations:
            unique_variations.append(var.strip())
    
    return unique_variations


def search_with_variations(jikan, title):
    """Search using multiple title variations"""
    print(f"\n🔄 Searching with title variations for: '{title}'")
    print("-" * 60)
    
    variations = clean_title_variations(title)
    
    all_results = {}
    best_matches = []
    
    for i, variation in enumerate(variations, 1):
        print(f"\n{i}. Trying: '{variation}'")
        
        try:
            result = jikan.search_anime(variation, limit=5)
            
            if result and "data" in result and result["data"]:
                anime_list = result["data"]
                all_results[variation] = anime_list
                
                print(f"   ✅ Found {len(anime_list)} results")
                
                # Show top result
                top_result = anime_list[0]
                print(f"   Top: {top_result.get('title')} (ID: {top_result.get('mal_id')}, Score: {top_result.get('score')})")
                
                # Check for potential matches
                for anime in anime_list:
                    anime_title = anime.get('title', '').lower()
                    english_title = anime.get('title_english', '').lower()
                    
                    original_lower = title.lower()
                    
                    # Check for partial matches
                    if (original_lower in anime_title or anime_title in original_lower or
                        (english_title and (original_lower in english_title or english_title in original_lower))):
                        best_matches.append({
                            'anime': anime,
                            'search_term': variation,
                            'match_reason': 'Title similarity'
                        })
            else:
                print(f"   ❌ No results")
                all_results[variation] = []
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_results[variation] = []
    
    return all_results, best_matches


def analyze_provider_ids(provider_ids):
    """Analyze available provider IDs and suggest MAL ID lookup strategies"""
    print(f"\n🔍 Analyzing Provider IDs: {list(provider_ids.keys())}")
    print("-" * 60)
    
    suggestions = []
    
    # Check for AniList ID (can be mapped to MAL)
    if 'AniList' in provider_ids:
        anilist_id = provider_ids['AniList']
        print(f"✅ AniList ID found: {anilist_id}")
        suggestions.append(f"Use AniList ID {anilist_id} to find MAL mapping")
    
    # Check for AniDB ID (can be mapped to MAL)
    if 'AniDB' in provider_ids:
        anidb_id = provider_ids['AniDB']
        print(f"✅ AniDB ID found: {anidb_id}")
        suggestions.append(f"Use AniDB ID {anidb_id} to find MAL mapping")
    
    # Check for TMDB ID (sometimes mapped to MAL)
    if 'Tmdb' in provider_ids:
        tmdb_id = provider_ids['Tmdb']
        print(f"✅ TMDB ID found: {tmdb_id}")
        suggestions.append(f"Use TMDB ID {tmdb_id} to find MAL mapping")
    
    # Check for TVDB ID (can be mapped to MAL)
    if 'Tvdb' in provider_ids:
        tvdb_id = provider_ids['Tvdb']
        print(f"✅ TVDB ID found: {tvdb_id}")
        suggestions.append(f"Use TVDB ID {tvdb_id} to find MAL mapping")
    
    if suggestions:
        print(f"\n💡 Mapping Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    else:
        print(f"❌ No useful provider IDs for MAL mapping")
    
    return suggestions


def test_known_anime():
    """Test with some known anime to verify the API works"""
    print(f"\n🧪 Testing with known anime titles")
    print("=" * 60)
    
    jikan = JikanAPI()
    
    known_anime = [
        ("Attack on Titan", "Should find popular anime"),
        ("One Piece", "Should find very popular anime"),
        ("Naruto", "Should find classic anime"),
        ("Death Note", "Should find well-known anime")
    ]
    
    for title, description in known_anime:
        print(f"\n🔍 Testing: {title} ({description})")
        
        try:
            result = jikan.search_anime(title, limit=3)
            if result and "data" in result and result["data"]:
                top_result = result["data"][0]
                print(f"   ✅ Found: {top_result.get('title')} (ID: {top_result.get('mal_id')})")
            else:
                print(f"   ❌ No results - API might be down")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Main function to debug the specific anime search issue"""
    print("🎯 Enhanced Anime Search Debug")
    print("=" * 80)
    
    # First test that the API is working with known anime
    test_known_anime()
    
    # Now test the problematic anime
    target_title = "A Returner's Magic Should Be Special"
    jikan = JikanAPI()
    
    print(f"\n🎯 DEBUGGING: {target_title}")
    print("=" * 80)
    
    # Test with variations
    all_results, best_matches = search_with_variations(jikan, target_title)
    
    # Analyze the provider IDs from the log
    provider_ids = {
        'Imdb': 'tt15299932',  # From the log
        'Tmdb': '155837',
        'AniList': '126579',   # From the log
        'Tvdb': '432815',
        'TvdbSlug': 'a-returners-magic-should-be-special',
        'AniDB': '17944'       # Found via auto-discovery in log
    }
    
    analyze_provider_ids(provider_ids)
    
    # Show best matches found
    if best_matches:
        print(f"\n🎯 POTENTIAL MATCHES FOUND:")
        print("-" * 40)
        for i, match in enumerate(best_matches, 1):
            anime = match['anime']
            print(f"{i}. {anime.get('title')} (MAL ID: {anime.get('mal_id')})")
            print(f"   English: {anime.get('title_english', 'N/A')}")
            print(f"   Score: {anime.get('score', 'N/A')}/10")
            print(f"   Found via: {match['search_term']}")
            print(f"   Reason: {match['match_reason']}")
    else:
        print(f"\n❌ NO MATCHES FOUND")
        print("This anime might not be in MyAnimeList or has a very different title")
    
    # Check if we can use AniList ID to find MAL ID
    if 'AniList' in provider_ids:
        print(f"\n🔗 ANILIST TO MAL MAPPING ATTEMPT")
        print("-" * 40)
        anilist_id = provider_ids['AniList']
        print(f"AniList ID: {anilist_id}")
        print(f"You can manually check: https://anilist.co/anime/{anilist_id}")
        print(f"Look for 'External Links' section to find MyAnimeList link")
    
    # Summary and recommendations
    print(f"\n📋 SUMMARY AND RECOMMENDATIONS")
    print("=" * 80)
    
    if best_matches:
        best = best_matches[0]['anime']
        print(f"✅ Best candidate: {best.get('title')} (MAL ID: {best.get('mal_id')})")
        print(f"   Recommendation: Manually verify this is the correct anime")
    else:
        print(f"❌ No matches found via title search")
        print(f"   Recommendations:")
        print(f"   1. Manually search MyAnimeList.net for the Japanese title")
        print(f"   2. Use AniList ID {provider_ids.get('AniList')} to find MAL link")
        print(f"   3. The anime might be too new or not yet on MyAnimeList")
        print(f"   4. Consider using AniDB rating instead (already working)")
    
    # Show what worked in the log vs what didn't
    print(f"\n🔍 LOG ANALYSIS")
    print("=" * 80)
    print(f"✅ AniDB: Found rating 4.64 via auto-discovery (TVDB ID → AniDB ID)")
    print(f"❌ MyAnimeList: No valid rating found")
    print(f"   Possible reasons:")
    print(f"   - Title mismatch between Jellyfin and MyAnimeList")
    print(f"   - Anime not in MyAnimeList database")
    print(f"   - Search algorithm needs improvement")


if __name__ == "__main__":
    main()
