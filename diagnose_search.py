#!/usr/bin/env python3
"""
Specific test to find 'A Returner's Magic Should Be Special' in search results
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.jikan_api import JikanAPI


def search_for_target_anime():
    """Search specifically for the target anime and analyze results"""
    print("🎯 Searching for 'A Returner's Magic Should Be Special'")
    print("=" * 60)
    
    jikan = JikanAPI()
    target_title = "A Returner's Magic Should Be Special"
    
    # From your debug output, we know these searches work:
    working_searches = [
        "Returner Magic Special",
        "returner magic"
    ]
    
    target_mal_id = 54852  # We know this is the correct ID
    
    for search_term in working_searches:
        print(f"\n🔍 Testing search: '{search_term}'")
        print("-" * 40)
        
        result = jikan.search_anime(search_term, limit=10)
        
        if result and "data" in result:
            anime_list = result["data"]
            print(f"Found {len(anime_list)} results")
            
            # Look for our target anime
            target_found = False
            for i, anime in enumerate(anime_list, 1):
                mal_id = anime.get('mal_id')
                title = anime.get('title', '')
                english = anime.get('title_english', '')
                score = anime.get('score', 'N/A')
                
                print(f"  {i}. {title} (ID: {mal_id})")
                print(f"     English: {english}")
                print(f"     Score: {score}")
                
                if mal_id == target_mal_id:
                    target_found = True
                    print(f"     ✅ FOUND TARGET ANIME!")
                    
                    # Test if our matching logic would find this
                    if english and target_title.lower() in english.lower():
                        print(f"     ✅ Would match by English title")
                    elif title and any(word in title.lower() for word in ['returner', 'magic', 'special']):
                        print(f"     ✅ Would match by keywords")
                    else:
                        print(f"     ❌ Would NOT match - this is the problem!")
                        print(f"     Title: '{title}'")
                        print(f"     English: '{english}'")
            
            if target_found:
                print(f"\n✅ Target anime found in '{search_term}' results!")
                return True
            else:
                print(f"\n❌ Target anime NOT found in '{search_term}' results")
        else:
            print(f"❌ No results for '{search_term}'")
    
    return False


def test_direct_lookup():
    """Test direct lookup of the target anime"""
    print(f"\n🧪 Testing direct lookup of MAL ID 54852")
    print("-" * 40)
    
    jikan = JikanAPI()
    
    result = jikan.get_anime_details(54852)
    
    if result and "data" in result:
        anime = result["data"]
        print(f"✅ Direct lookup successful:")
        print(f"   Title: {anime.get('title')}")
        print(f"   English: {anime.get('title_english')}")
        print(f"   Japanese: {anime.get('title_japanese')}")
        print(f"   Score: {anime.get('score')}")
        
        # Show all titles to understand matching issues
        if "titles" in anime:
            print(f"   All titles:")
            for title_obj in anime["titles"]:
                title_type = title_obj.get("type", "")
                title = title_obj.get("title", "")
                print(f"     - {title} ({title_type})")
        
        return True
    else:
        print(f"❌ Direct lookup failed")
        return False


def test_improved_matching():
    """Test if our improved matching logic works"""
    print(f"\n🧪 Testing improved matching logic")
    print("-" * 40)
    
    jikan = JikanAPI()
    target_title = "A Returner's Magic Should Be Special"
    
    # Try the improved find_anime_by_title method
    print(f"🔍 Using find_anime_by_title for: '{target_title}'")
    
    result = jikan.find_anime_by_title(target_title)
    
    if result and "data" in result:
        anime = result["data"]
        mal_id = anime.get('mal_id')
        
        print(f"✅ Found anime: {anime.get('title')} (ID: {mal_id})")
        
        if mal_id == 54852:
            print(f"🎉 SUCCESS! Found the correct anime!")
            return True
        else:
            print(f"❌ Found wrong anime (expected ID 54852)")
            return False
    else:
        print(f"❌ No anime found")
        return False


def main():
    """Main test function"""
    print("🔍 Diagnostic Test for 'A Returner's Magic Should Be Special'")
    print("=" * 80)
    
    # Test 1: Search where we know the anime appears
    found_in_search = search_for_target_anime()
    
    # Test 2: Direct lookup
    direct_works = test_direct_lookup()
    
    # Test 3: Our improved matching
    matching_works = test_improved_matching()
    
    print(f"\n📊 DIAGNOSTIC RESULTS")
    print("=" * 40)
    print(f"Found in search results: {'✅ YES' if found_in_search else '❌ NO'}")
    print(f"Direct MAL ID lookup: {'✅ YES' if direct_works else '❌ NO'}")
    print(f"Improved matching works: {'✅ YES' if matching_works else '❌ NO'}")
    
    if matching_works:
        print(f"\n🎉 SOLUTION READY!")
        print(f"   The improved search should now work in the real application")
    elif found_in_search and direct_works:
        print(f"\n🔧 NEEDS REFINEMENT")
        print(f"   The anime is findable but our matching logic needs improvement")
        print(f"   Consider using the working search terms in the algorithm")
    else:
        print(f"\n❌ DEEPER ISSUES")
        print(f"   There may be API connectivity or other issues")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if matching_works:
        print(f"   ✅ Ready to test with real Aphrodite data")
    else:
        print(f"   🔧 Modify search algorithm to use working search terms")
        print(f"   🔧 Add specific keyword matching for 'returner magic special'")
        print(f"   🔧 Consider using MAL ID when available in provider data")


if __name__ == "__main__":
    main()
