#!/usr/bin/env python3
"""
Set Environment Variables for API Keys

If your database settings aren't loading properly in batch workers,
you can set API keys as environment variables as a fallback.

This script helps you set them up.
"""

import os
import sys

def setup_env_variables():
    """Instructions for setting up environment variables"""
    print("🔧 Setting Up API Key Environment Variables")
    print("=" * 60)
    
    print("\n📋 OPTION 1: Add to Docker Compose")
    print("Add these lines to your docker-compose.yml under the worker service:")
    print("""
    aphrodite-worker:
      environment:
        - OMDB_API_KEY=your_omdb_api_key_here
        - TMDB_API_KEY=your_tmdb_api_key_here
    """)
    
    print("\n📋 OPTION 2: Add to Dockerfile")
    print("Add these lines to your Dockerfile:")
    print("""
    ENV OMDB_API_KEY=your_omdb_api_key_here
    ENV TMDB_API_KEY=your_tmdb_api_key_here
    """)
    
    print("\n📋 OPTION 3: Runtime Environment Variables")
    print("Set these before starting your containers:")
    print("""
    export OMDB_API_KEY=your_omdb_api_key_here
    export TMDB_API_KEY=your_tmdb_api_key_here
    """)
    
    print("\n🔍 FINDING YOUR API KEYS:")
    print("Your API keys should be in the Aphrodite Settings UI.")
    print("Navigate to Settings → API Keys to find:")
    print("- OMDb API Key (for RT Critics and Metacritic)")
    print("- TMDb API Key (for TMDb ratings)")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("- The fixed code will try database first, then fall back to env vars")
    print("- Environment variables are a backup method for batch workers")
    print("- Keep your API keys secure and don't commit them to git")

def check_current_env():
    """Check if environment variables are already set"""
    print("\n🔍 CHECKING CURRENT ENVIRONMENT:")
    
    omdb_key = os.getenv('OMDB_API_KEY')
    tmdb_key = os.getenv('TMDB_API_KEY')
    
    if omdb_key:
        masked_omdb = '*' * (len(omdb_key) - 4) + omdb_key[-4:]
        print(f"   ✅ OMDB_API_KEY: {masked_omdb}")
    else:
        print(f"   ❌ OMDB_API_KEY: Not set")
        
    if tmdb_key:
        print(f"   ✅ TMDB_API_KEY: Set")
    else:
        print(f"   ❌ TMDB_API_KEY: Not set")

if __name__ == "__main__":
    setup_env_variables()
    check_current_env()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Set environment variables using one of the methods above")
    print("2. Rebuild your Docker containers")
    print("3. Test batch processing again")
    print("4. Check logs to see if RT Critics and Metacritic are now included")
