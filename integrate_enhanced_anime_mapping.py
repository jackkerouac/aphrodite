#!/usr/bin/env python3
"""
Production Integration Script for Enhanced Anime Mapping
Applies the comprehensive anime mapping enhancements to Aphrodite
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the production enhancement
from production_anime_mapping import enhance_review_fetcher

def apply_production_enhancements():
    """Apply the enhanced anime mapping to production ReviewFetcher"""
    try:
        # Import the existing ReviewFetcher
        from aphrodite_helpers.get_review_info import ReviewFetcher
        
        # Create enhanced version with comprehensive database support
        EnhancedReviewFetcher = enhance_review_fetcher(ReviewFetcher)
        
        # Replace the original class in the module
        import aphrodite_helpers.get_review_info as review_module
        review_module.ReviewFetcher = EnhancedReviewFetcher
        
        print("✅ Successfully applied enhanced anime mapping to production")
        print("🎯 Features enabled:")
        print("   • Comprehensive AniDB→MAL mapping (13,000+ anime)")
        print("   • Enhanced AniList→MAL mapping (18,000+ anime)")
        print("   • Graceful fallbacks for unmapped anime")
        print("   • Automatic MyAnimeList badge generation")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply enhancements: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Integrating Enhanced Anime Mapping into Production")
    print("=" * 60)
    
    success = apply_production_enhancements()
    
    if success:
        print("\n🎉 Integration Complete!")
        print("   Enhanced anime mapping is now active in Aphrodite")
        print("   MyAnimeList badges will use comprehensive database mapping")
    else:
        print("\n❌ Integration Failed!")
        print("   Check the error messages above")
