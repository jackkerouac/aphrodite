#!/usr/bin/env python3
# aphrodite_helpers/get_awards_info.py

import os
import sys
import argparse
import requests
import json
import time
from requests.exceptions import RequestException

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.get_media_info import get_jellyfin_item_details
from aphrodite_helpers.awards_data_source import AwardsDataSource

class AwardsFetcher:
    def __init__(self, settings):
        self.settings = settings
        self.jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        self.tmdb_settings = settings.get("api_keys", {}).get("TMDB", [{}])[0]
        self.omdb_settings = settings.get("api_keys", {}).get("OMDB", [{}])[0]
        
        # Setup headers for Jellyfin API calls
        self.jellyfin_headers = {"X-Emby-Token": self.jellyfin_settings.get("api_key", "")}
        
        # Initialize cache
        self.cache = {}
        self.cache_expiration = 60 * 60 * 24  # Cache for 24 hours (awards don't change often)
        
        # Load badge settings to get award sources
        self.badge_settings = self.load_badge_settings()
        
        # Load awards mapping
        self.awards_mapping = self.load_awards_mapping()
    
    def load_badge_settings(self, settings_file="badge_settings_awards.yml"):
        """Load badge settings to get award sources and mappings"""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(root_dir, settings_file)
            
            with open(full_path, 'r') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load awards badge settings: {e}")
            return {}
    
    def load_awards_mapping(self):
        """Load static awards mapping for known winners"""
        # This will be expanded in Phase 2 - for now, basic mapping
        return {
            "movies": {
                # Example entries - to be expanded
                "tt0111161": {"awards": ["imdb"], "year": 1994, "title": "The Shawshank Redemption"},
                "tt0068646": {"awards": ["oscars"], "year": 1972, "title": "The Godfather"},
                "tt0071562": {"awards": ["oscars"], "year": 1974, "title": "The Godfather Part II"},
                "tt0468569": {"awards": ["oscars"], "year": 2008, "title": "The Dark Knight"},
                "tt1375666": {"awards": ["oscars"], "year": 2010, "title": "Inception"},
                "tt0167260": {"awards": ["oscars"], "year": 2003, "title": "The Lord of the Rings: The Return of the King"}
            },
            "tv": {
                # Example entries - to be expanded
                "tt0944947": {"awards": ["emmys"], "year": 2011, "title": "Game of Thrones"},
                "tt0903747": {"awards": ["emmys"], "year": 2008, "title": "Breaking Bad"},
                "tt2356777": {"awards": ["emmys"], "year": 2014, "title": "True Detective"},
                "tt0386676": {"awards": ["emmys"], "year": 2005, "title": "The Office"}
            }
        }
    
    def get_jellyfin_item_metadata(self, item_id):
        """Retrieve item metadata from Jellyfin"""
        return get_jellyfin_item_details(
            self.jellyfin_settings.get('url'),
            self.jellyfin_settings.get('api_key'),
            self.jellyfin_settings.get('user_id'),
            item_id
        )
    
    def get_imdb_id(self, item_data):
        """Extract IMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        provider_ids = item_data.get("ProviderIds", {})
        return provider_ids.get("Imdb")
    
    def get_tmdb_id(self, item_data):
        """Extract TMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        provider_ids = item_data.get("ProviderIds", {})
        return provider_ids.get("Tmdb")
    
    def check_award_eligibility(self, item_info, award_sources):
        """Check if item has won any configured awards and return the award type"""
        if not item_info or not award_sources:
            return None
        
        # Get IMDb and TMDb IDs from item info
        imdb_id = self.get_imdb_id(item_info)
        tmdb_id = self.get_tmdb_id(item_info)
        
        if not imdb_id and not tmdb_id:
            print(f"ℹ️ No IMDb or TMDb ID found for item")
            return None
        
        # Determine media type
        media_type = "tv" if item_info.get("Type") == "Series" else "movies"
        
        # Use AwardsDataSource for comprehensive award detection
        awards_data_source = AwardsDataSource(self.settings)
        
        if media_type == "tv":
            all_awards = awards_data_source.get_tv_awards(tmdb_id=tmdb_id, imdb_id=imdb_id)
        else:
            all_awards = awards_data_source.get_movie_awards(tmdb_id=tmdb_id, imdb_id=imdb_id)
        
        if all_awards:
            # Return the most prestigious award that matches our configured sources
            primary_award = self.get_primary_award(all_awards)
            if primary_award in award_sources:
                print(f"✅ Found primary award: {primary_award} for {media_type} (IMDb: {imdb_id}, TMDb: {tmdb_id})")
                return primary_award
            
            # If primary award not in sources, check others
            for award in all_awards:
                if award in award_sources:
                    print(f"✅ Found award: {award} for {media_type} (IMDb: {imdb_id}, TMDb: {tmdb_id})")
                    return award
        
        return None
    
    def check_static_mapping(self, imdb_id, media_type, award_sources):
        """Check static awards mapping for the given IMDb ID (legacy method)"""
        # This method is now primarily used as a fallback
        # Main award detection is handled by AwardsDataSource
        if not self.awards_mapping or media_type not in self.awards_mapping:
            return None
        
        mapping = self.awards_mapping[media_type]
        if imdb_id in mapping:
            item_awards = mapping[imdb_id].get("awards", [])
            
            # Return the first award that matches our configured sources
            for award in item_awards:
                if award in award_sources:
                    print(f"✅ Found award: {award} for IMDb ID {imdb_id} (static mapping)")
                    return award
        
        return None
    
    def get_primary_award(self, awards_list):
        """Return the most prestigious award from a list"""
        if not awards_list:
            return None
        
        # Award priority order (most prestigious first)
        priority_order = [
            "oscars",      # Academy Awards
            "cannes",      # Cannes Film Festival
            "golden",      # Golden Globes
            "bafta",       # BAFTA Awards
            "emmys",       # Emmy Awards
            "berlinale",   # Berlin International Film Festival
            "venice",      # Venice Film Festival
            "sundance",    # Sundance Film Festival
            "spirit",      # Independent Spirit Awards
            "cesar",       # César Awards
            "choice",      # People's Choice Awards
            "imdb",        # IMDb Top lists
            "letterboxd",  # Letterboxd recognition
            "metacritic",  # Metacritic recognition
            "rotten",      # Rotten Tomatoes recognition
            "netflix"      # Netflix awards/recognition
        ]
        
        # Return the first award in priority order that exists in the list
        for award in priority_order:
            if award in awards_list:
                return award
        
        # If none match priority order, return first available
        return awards_list[0]
    
    def get_media_awards_info(self, jellyfin_url, api_key, user_id, item_id):
        """Get awards information for a media item"""
        try:
            # Get item data from Jellyfin
            item_data = self.get_jellyfin_item_metadata(item_id)
            if not item_data:
                print(f"❌ Could not retrieve item data from Jellyfin for ID: {item_id}")
                return None
            
            # Get configured award sources from badge settings
            award_sources = self.badge_settings.get("Awards", {}).get("award_sources", [])
            if not award_sources:
                print(f"ℹ️ No award sources configured in badge settings")
                return None
            
            # Check if item has won any awards
            award_type = self.check_award_eligibility(item_data, award_sources)
            
            if award_type:
                item_title = item_data.get("Name", "Unknown")
                print(f"🏆 Found award '{award_type}' for item: {item_title}")
                
                return {
                    "award_type": award_type,
                    "item_id": item_id,
                    "item_title": item_title,
                    "imdb_id": self.get_imdb_id(item_data),
                    "tmdb_id": self.get_tmdb_id(item_data)
                }
            else:
                print(f"ℹ️ No awards found for item ID: {item_id}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting awards info for item {item_id}: {e}")
            return None

def main():
    """Command line interface for testing awards detection"""
    parser = argparse.ArgumentParser(description="Get awards information for a Jellyfin media item")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--settings", default="settings.yaml", help="Settings file path")
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings(args.settings)
    
    # Create awards fetcher
    awards_fetcher = AwardsFetcher(settings)
    
    try:
        # Get awards info
        jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        awards_info = awards_fetcher.get_media_awards_info(
            jellyfin_settings.get("url", ""),
            jellyfin_settings.get("api_key", ""),
            jellyfin_settings.get("user_id", ""),
            args.itemid
        )
        
        if awards_info:
            print(f"\n🏆 Awards Information:")
            print(f"   Title: {awards_info['item_title']}")
            print(f"   Award: {awards_info['award_type']}")
            print(f"   IMDb ID: {awards_info.get('imdb_id', 'N/A')}")
            print(f"   TMDb ID: {awards_info.get('tmdb_id', 'N/A')}")
        else:
            print(f"\nℹ️ No awards found for item ID: {args.itemid}")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
