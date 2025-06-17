#!/usr/bin/env python3
# aphrodite_helpers/get_review_info.py - Modularized version

import os
import sys
import argparse

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.get_media_info import get_jellyfin_item_details
# REMOVED: from aphrodite_helpers.review_preferences import filter_reviews_by_preferences

# Import modular components
from aphrodite_helpers.review_fetcher_core import ReviewFetcher as CoreReviewFetcher
from aphrodite_helpers.review_fetcher_omdb_tmdb import OmdbTmdbMixin
from aphrodite_helpers.review_fetcher_anidb import AnidbMixin
from aphrodite_helpers.review_fetcher_mal import MyAnimeListMixin
from aphrodite_helpers.review_fetcher_formatter import ReviewFormatterMixin

# Combine all mixins into the main ReviewFetcher class
class ReviewFetcher(CoreReviewFetcher, OmdbTmdbMixin, AnidbMixin, MyAnimeListMixin, ReviewFormatterMixin):
    """
    Complete ReviewFetcher class combining all API integrations.
    
    This modular approach allows us to convert each component separately
    without dealing with the entire large file at once.
    """
    pass

# Module-level function for backward compatibility
def get_reviews(item_id, settings, show_details=False):
    """
    Module-level function to get reviews for an item.
    Maintains compatibility with existing code that imports get_reviews directly.
    """
    review_fetcher = ReviewFetcher(settings)
    return review_fetcher.get_reviews(item_id, show_details)

def display_reviews(reviews, item_title):
    """Display reviews in a human-readable format"""
    print(f"\n📊 Reviews for: {item_title}\n")
    print("-" * 50)
    
    if not reviews:
        print("No reviews found.")
        return
    
    for review in reviews:
        source = review.get("source", "Unknown")
        rating = review.get("rating", "N/A")
        max_rating = review.get("max_rating", "")
        votes = review.get("votes", "")
        
        print(f"🏆 {source}: {rating}" + (f"/{max_rating}" if max_rating else ""))
        if votes:
            print(f"   Votes: {votes}")
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Get reviews for a Jellyfin media item")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--show-reviews", action="store_true", help="Display reviews in human-readable format")
    parser.add_argument("--settings", default="settings.yaml", help="Settings file path")
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings(args.settings)
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    try:
        # Get item details for title
        jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        item_details = get_jellyfin_item_details(
            jellyfin_settings.get("url", ""),
            jellyfin_settings.get("api_key", ""),
            jellyfin_settings.get("user_id", ""),
            args.itemid
        )
        
        if not item_details:
            print(f"❌ Could not retrieve item details for ID: {args.itemid}")
            return 1
        
        item_title = item_details.get("Name", "Unknown Title")
        
        # Get reviews with detailed information for display
        reviews = review_fetcher.get_reviews(args.itemid, show_details=True)
        
        # Display reviews if requested
        if args.show_reviews:
            display_reviews(reviews, item_title)
        else:
            # Just return the number of reviews found
            print(f"✅ Found {len(reviews)} reviews for '{item_title}'")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
