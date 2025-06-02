#!/usr/bin/env python3
"""
Quick test script for the version service
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.version_service import VersionService

def test_version_service():
    print("Testing Aphrodite Version Service")
    print("=" * 40)
    
    # Create version service
    vs = VersionService()
    
    # Test current version
    current = vs.get_current_version()
    print(f"Current version from config: {current}")
    
    # Test version file location
    print(f"Version file location: {vs.version_file}")
    print(f"Version file exists: {vs.version_file.exists()}")
    
    # Test version check
    print("\nChecking for updates...")
    result = vs.check_for_updates(force_check=True)
    
    print(f"Check successful: {result['check_successful']}")
    print(f"Current version: {result['current_version']}")
    print(f"Latest version: {result['latest_version']}")
    print(f"Update available: {result['update_available']}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    if result['release_url']:
        print(f"Release URL: {result['release_url']}")
    
    if result['published_at']:
        print(f"Published: {result['published_at']}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_version_service()
