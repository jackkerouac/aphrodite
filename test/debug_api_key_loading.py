#!/usr/bin/env python3
"""
Debug API Key Loading Issue

The batch jobs are failing to load API keys from the database, which prevents
RT Critics and Metacritic from being fetched (they require OMDb API key).

This script will help identify and fix the API key loading issue.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def debug_api_key_loading():
    """Debug the API key loading issue in batch jobs"""
    print("🔍 Debugging API Key Loading Issue")
    print("=" * 60)
    
    try:
        from app.core.database import init_db, close_db, async_session_factory
        from app.services.badge_processing.renderers.review_data_fetcher import V2ReviewDataFetcher
        from app.services.settings_service import settings_service
        
        # Initialize database
        await init_db()
        
        print("\n📋 TESTING API KEY LOADING...")
        
        # Test 1: Direct settings service access
        async with async_session_factory() as db:
            print("\n🔧 Test 1: Direct Settings Service Access")
            try:
                settings_yaml = await settings_service.get_settings(
                    "settings.yaml", db, use_cache=True, force_reload=True
                )
                
                if settings_yaml and 'api_keys' in settings_yaml:
                    api_keys = settings_yaml['api_keys']
                    
                    # Check OMDb
                    omdb_config = api_keys.get("OMDB", [])
                    if omdb_config and len(omdb_config) > 0:
                        omdb_key = omdb_config[0].get("api_key", "")
                        if omdb_key:
                            masked_key = '*' * (len(omdb_key) - 4) + omdb_key[-4:]
                            print(f"   ✅ OMDb API key found: {masked_key}")
                        else:
                            print("   ❌ OMDb API key is empty")
                    else:
                        print("   ❌ OMDb config not found or empty")
                    
                    # Check TMDb
                    tmdb_config = api_keys.get("TMDB", [])
                    if tmdb_config and len(tmdb_config) > 0:
                        tmdb_key = tmdb_config[0].get("api_key", "")
                        if tmdb_key:
                            print(f"   ✅ TMDb API key found")
                        else:
                            print("   ❌ TMDb API key is empty")
                    else:
                        print("   ❌ TMDb config not found or empty")
                        
                else:
                    print("   ❌ No API keys section found in settings.yaml")
                    
            except Exception as e:
                print(f"   ❌ Error accessing settings service: {e}")
        
        # Test 2: Review Data Fetcher
        print("\n🔧 Test 2: Review Data Fetcher API Key Loading")
        try:
            fetcher = V2ReviewDataFetcher()
            await fetcher._load_api_keys()
            
            if fetcher.omdb_api_key:
                masked_key = '*' * (len(fetcher.omdb_api_key) - 4) + fetcher.omdb_api_key[-4:]
                print(f"   ✅ Fetcher loaded OMDb key: {masked_key}")
            else:
                print("   ❌ Fetcher failed to load OMDb key")
                
            if fetcher.tmdb_api_key:
                print(f"   ✅ Fetcher loaded TMDb key")
            else:
                print("   ❌ Fetcher failed to load TMDb key")
                
        except Exception as e:
            print(f"   ❌ Error testing fetcher: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Check current review settings
        print("\n🔧 Test 3: Current Review Settings")
        try:
            from app.services.badge_processing.database_service import badge_settings_service
            
            async with async_session_factory() as db:
                review_settings = await badge_settings_service.get_review_settings(db, force_reload=True)
                
                if review_settings:
                    sources = review_settings.get('Sources', {})
                    print(f"   Current settings:")
                    print(f"     enable_imdb: {sources.get('enable_imdb', 'NOT SET')}")
                    print(f"     enable_tmdb: {sources.get('enable_tmdb', 'NOT SET')}")
                    print(f"     enable_rotten_tomatoes_critics: {sources.get('enable_rotten_tomatoes_critics', 'NOT SET')}")
                    print(f"     enable_metacritic: {sources.get('enable_metacritic', 'NOT SET')}")
                else:
                    print("   ❌ No review settings found")
                    
        except Exception as e:
            print(f"   ❌ Error checking review settings: {e}")
        
        await close_db()
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main debug function"""
    await debug_api_key_loading()
    
    print(f"\n" + "=" * 60)
    print("🎯 DIAGNOSIS:")
    print("   The batch jobs are failing to load API keys from the database.")
    print("   Without OMDb API key, RT Critics and Metacritic cannot be fetched.")
    print("   This is why only IMDb and TMDb are working.")
    print("")
    print("🔧 LIKELY SOLUTIONS:")
    print("   1. Fix database session factory initialization in workers")
    print("   2. Add fallback API key loading method")
    print("   3. Ensure settings.yaml is properly configured with API keys")

if __name__ == "__main__":
    asyncio.run(main())
