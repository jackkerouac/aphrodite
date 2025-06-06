#!/usr/bin/env python3
"""
Production-ready comprehensive anime mapping integration
"""

import time
import os
from typing import Optional

# Import the anime offline database
try:
    from anime_offline_database import AnimeOfflineDatabase
    COMPREHENSIVE_DB_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_DB_AVAILABLE = False
    print("⚠️ Comprehensive database not available, using fallback mappings")


def enhance_review_fetcher(review_fetcher_class):
    """
    Enhance the existing ReviewFetcher with comprehensive anime mapping
    
    This is a production-ready enhancement that:
    1. Uses the comprehensive database when available
    2. Falls back gracefully to existing methods
    3. Adds AniDB→MAL mapping support
    4. Improves AniList→MAL mapping coverage
    """
    
    class EnhancedReviewFetcher(review_fetcher_class):
        def __init__(self, settings):
            super().__init__(settings)
            
            # Initialize comprehensive database if available
            self.anime_db = None
            self._anime_db_loaded = False
            
            if COMPREHENSIVE_DB_AVAILABLE:
                try:
                    self.anime_db = AnimeOfflineDatabase()
                except Exception as e:
                    print(f"⚠️ Could not initialize anime database: {e}")
        
        def _ensure_anime_db_loaded(self):
            """Lazy load the anime database"""
            if not self._anime_db_loaded and self.anime_db:
                try:
                    print("📚 Loading comprehensive anime database...")
                    success = self.anime_db.load_database()
                    
                    if success:
                        info = self.anime_db.get_mapping_info()
                        print(f"✅ Loaded {info['anilist_mappings']:,} AniList and {info['anidb_mappings']:,} AniDB mappings")
                        self._anime_db_loaded = True
                    else:
                        print("⚠️ Database load failed, using fallback mappings")
                except Exception as e:
                    print(f"⚠️ Database error: {e}, using fallback mappings")
        
        def find_mal_id_from_anilist(self, anilist_id):
            """Enhanced AniList to MAL mapping"""
            try:
                # Try comprehensive database first
                if self.anime_db:
                    self._ensure_anime_db_loaded()
                    
                    if self._anime_db_loaded:
                        mal_id = self.anime_db.get_mal_id_from_anilist(anilist_id)
                        if mal_id:
                            print(f"✅ Found MAL ID {mal_id} via comprehensive AniList mapping")
                            return mal_id
                
                # Fallback to original hardcoded method
                print(f"🔄 Using fallback AniList mapping...")
                return super().find_mal_id_from_anilist(anilist_id)
                
            except Exception as e:
                print(f"❌ Error in AniList mapping: {e}, using fallback")
                return super().find_mal_id_from_anilist(anilist_id)
        
        def find_mal_id_from_anidb(self, anidb_id):
            """NEW: AniDB to MAL mapping via comprehensive database"""
            try:
                if self.anime_db:
                    self._ensure_anime_db_loaded()
                    
                    if self._anime_db_loaded:
                        mal_id = self.anime_db.get_mal_id_from_anidb(anidb_id)
                        if mal_id:
                            print(f"✅ Found MAL ID {mal_id} via comprehensive AniDB mapping")
                            return mal_id
                
                print(f"🔍 AniDB ID {anidb_id} not found in comprehensive database")
                return None
                
            except Exception as e:
                print(f"❌ Error in AniDB mapping: {e}")
                return None
        
        def fetch_myanimelist_ratings(self, mal_id=None, item_name=None, item_data=None):
            """Enhanced MyAnimeList fetching with comprehensive mapping"""
            print(f"🔍 fetch_myanimelist_ratings called with mal_id: {mal_id}, item_name: {item_name}")
            
            # Check cache first
            cache_key = f"mal_{mal_id or item_name or 'unknown'}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                    print(f"✅ Using cached MyAnimeList data")
                    return cache_entry["data"]
            
            try:
                # If we have a MAL ID, use it directly
                if mal_id:
                    print(f"🌐 Fetching MyAnimeList details for ID: {mal_id}")
                    anime_data = self.jikan_api.get_anime_details(mal_id)
                else:
                    # Enhanced ID discovery strategy
                    mal_id_found = None
                    
                    if item_data:
                        provider_ids = item_data.get("ProviderIds", {})
                        
                        # Strategy 1: Try AniList mapping (enhanced with comprehensive DB)
                        anilist_id = provider_ids.get("AniList")
                        if anilist_id:
                            print(f"🔗 Trying AniList→MAL mapping for ID: {anilist_id}")
                            mal_id_found = self.find_mal_id_from_anilist(anilist_id)
                        
                        # Strategy 2: Try AniDB mapping (NEW - comprehensive DB)
                        if not mal_id_found:
                            anidb_id = provider_ids.get("AniDB")
                            if anidb_id:
                                print(f"🔗 Trying AniDB→MAL mapping for ID: {anidb_id}")
                                mal_id_found = self.find_mal_id_from_anidb(anidb_id)
                    
                    # Use discovered MAL ID or fall back to title search
                    if mal_id_found:
                        print(f"✅ Using discovered MAL ID: {mal_id_found}")
                        anime_data = self.jikan_api.get_anime_details(mal_id_found)
                    elif item_name:
                        print(f"🔍 Falling back to title search for: {item_name}")
                        anime_data = self.jikan_api.find_anime_by_title(item_name)
                    else:
                        print(f"❌ No MAL ID discovery method available")
                        return None
                
                # Process the anime data (same as original)
                if not anime_data:
                    print(f"❌ No anime data found")
                    return None
                
                # Extract rating data
                rating_data = self.jikan_api.extract_rating_data(anime_data)
                
                if rating_data and rating_data.get("score"):
                    # Format the data for our system
                    formatted_data = {
                        "mal_id": rating_data["mal_id"],
                        "title": rating_data["title"],
                        "rating": rating_data["score"],  # Score out of 10
                        "scored_by": rating_data["scored_by"],
                        "rank": rating_data["rank"],
                        "popularity": rating_data["popularity"],
                        "members": rating_data["members"],
                        "source_url": rating_data["source_url"],
                        "year": rating_data["year"],
                        "season": rating_data["season"],
                        "status": rating_data["status"],
                        "episodes": rating_data["episodes"]
                    }
                    
                    # Store in cache
                    self.cache[cache_key] = {
                        "timestamp": time.time(),
                        "data": formatted_data
                    }
                    
                    print(f"✅ Successfully fetched MyAnimeList rating: {rating_data['score']}/10")
                    print(f"   Title: {rating_data['title']}")
                    print(f"   Rank: #{rating_data.get('rank', 'N/A')}")
                    
                    return formatted_data
                else:
                    print(f"❌ No valid rating found in MyAnimeList data")
                    return None
                    
            except Exception as e:
                print(f"❌ Error fetching MyAnimeList ratings: {e}")
                return None
    
    return EnhancedReviewFetcher


def apply_enhancements():
    """
    Apply comprehensive anime mapping enhancements to Aphrodite
    
    This function can be called to enhance the existing ReviewFetcher
    without breaking existing functionality.
    """
    try:
        # Import the existing ReviewFetcher
        from aphrodite_helpers.get_review_info import ReviewFetcher
        
        # Create enhanced version
        EnhancedReviewFetcher = enhance_review_fetcher(ReviewFetcher)
        
        # Replace the original class in the module
        import aphrodite_helpers.get_review_info as review_module
        review_module.ReviewFetcher = EnhancedReviewFetcher
        
        print("✅ Applied comprehensive anime mapping enhancements")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply enhancements: {e}")
        return False


def test_production_integration():
    """Test the production integration"""
    print("🧪 Testing Production Integration")
    print("=" * 60)
    
    # Test the enhancement system
    success = apply_enhancements()
    
    if not success:
        print("❌ Enhancement failed")
        return False
    
    # Test with real data
    from aphrodite_helpers.settings_validator import load_settings
    from aphrodite_helpers.get_review_info import ReviewFetcher
    
    settings = load_settings("settings.yaml")
    fetcher = ReviewFetcher(settings)  # This should now be the enhanced version
    
    # Test data from your original log
    item_data = {
        "Name": "A Returner's Magic Should Be Special",
        "ProviderIds": {
            "Imdb": "tt15299932",
            "Tmdb": "155837", 
            "AniList": "126579",  # This should try comprehensive DB first, then fallback
            "Tvdb": "432815",
            "TvdbSlug": "a-returners-magic-should-be-special",
            "AniDB": "17944"      # This should work via comprehensive DB!
        }
    }
    
    print(f"🔍 Testing with: {item_data['Name']}")
    print(f"🔍 Provider IDs: {list(item_data['ProviderIds'].keys())}")
    
    # Test the enhanced fetching
    result = fetcher.fetch_myanimelist_ratings(
        mal_id=None,
        item_name=item_data['Name'],
        item_data=item_data
    )
    
    if result:
        print(f"\n🎉 PRODUCTION INTEGRATION SUCCESS!")
        print(f"   Title: {result.get('title')}")
        print(f"   MAL ID: {result.get('mal_id')}")
        print(f"   Rating: {result.get('rating')}/10")
        print(f"   Rank: #{result.get('rank')}")
        print(f"\n✅ Ready for production deployment!")
        return True
    else:
        print(f"\n❌ Production integration failed")
        return False


if __name__ == "__main__":
    test_production_integration()