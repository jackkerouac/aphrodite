#!/usr/bin/env python3
"""
Test script to verify if MyAnimeList badges are using real or demo data
"""

import requests
import json

def test_mal_data_source():
    """Test what data source MAL badges are using"""
    
    print("🔍 Testing MyAnimeList data source...")
    
    # Generate a preview with review badges
    request_data = {
        "badgeTypes": ["review"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/preview/generate",
            headers={"Content-Type": "application/json"},
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            poster_url = data.get('posterUrl', '')
            applied_badges = data.get('appliedBadges', [])
            
            print(f"✅ Preview generated successfully")
            print(f"Applied badges: {applied_badges}")
            print(f"Poster URL: {poster_url}")
            
            # Extract jellyfin ID from the URL
            if 'jellyfin_' in poster_url:
                parts = poster_url.split('jellyfin_')[1]
                jellyfin_id = parts.split('_')[0]
                print(f"🎬 Jellyfin ID: {jellyfin_id}")
                
                # Check if this is anime content by looking at the title/type
                print(f"\n🔍 Let's check what type of content this is...")
                
                # We can infer if MAL should be triggered based on the content
                if 'review' in applied_badges:
                    print(f"✅ Review badges were applied - MyAnimeList may be included")
                    
                    # To determine if it's using real vs demo MAL data, we would need to:
                    # 1. Check the actual content type (movie vs series vs anime)
                    # 2. Look at the server logs for MAL API calls
                    # 3. Or modify the system to return more detailed badge info
                    
                    print(f"\n💡 Data Source Analysis:")
                    print(f"   - Since this uses a real Jellyfin ID ({jellyfin_id})")
                    print(f"   - The system will try to get REAL review data first")
                    print(f"   - MyAnimeList will only trigger if:")
                    print(f"     a) The content is anime/series type, OR")
                    print(f"     b) Jellyfin has MAL/AniList provider IDs, OR") 
                    print(f"     c) Falls back to demo data if real data fails")
                    
                    print(f"\n🔬 To verify real vs demo data:")
                    print(f"   1. Check server logs for Jikan API calls")
                    print(f"   2. Try the same test multiple times - demo data is consistent")
                    print(f"   3. Real API data might vary or show actual anime ratings")
                
            else:
                print(f"❌ Not a Jellyfin poster - would use demo data")
                
        else:
            print(f"❌ Preview generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mal_data_source()
