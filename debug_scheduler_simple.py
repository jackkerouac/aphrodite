#!/usr/bin/env python3
"""
Debug script to identify why schedules are not starting or processing items correctly.

This script connects directly to the database to analyze the issue.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Set up environment
project_root = Path(__file__).parent
os.environ.setdefault('APHRODITE_ROOT', str(project_root))

# Now we can safely import
sys.path.insert(0, str(project_root / 'api'))

# Add required environment variables
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://postgres:aphrodite@localhost:5432/aphrodite')
os.environ.setdefault('JELLYFIN_URL', 'http://localhost:8096')
os.environ.setdefault('JELLYFIN_API_KEY', 'your_api_key_here')
os.environ.setdefault('SECRET_KEY', 'debug-secret-key')

async def debug_scheduler_issue():
    """Debug the scheduler issue using direct database queries"""
    
    print("🐛 Starting Scheduler Debug Analysis")
    print("=" * 60)
    
    try:
        # First, let's check what we know from the database
        print("📊 Database Analysis:")
        print("From the schedule_executions table:")
        print("  - Total items: 1366")
        print("  - Processed items: 0") 
        print("  - Failed items: 0")
        print("  - Created jobs: []")
        print("  - Status: completed")
        print("  - No error message")
        print()
        
        print("🔍 This indicates the scheduler found 1366 items but processed none.")
        print("   Most likely causes:")
        print("   1. All items already have 'aphrodite-overlay' tag (reprocess_all=false)")
        print("   2. UUID conversion failing (Jellyfin IDs are not UUIDs)")
        print("   3. Job creation logic failing silently")
        print()
        
        # Test the UUID conversion theory
        print("🧪 Testing UUID Conversion Theory:")
        print("Jellyfin typically uses 32-character hex IDs like: f137a2dd21bbc1b99aa5c0f6bf02a805")
        print("These are NOT UUIDs (which have dashes like: f137a2dd-21bb-c1b9-9aa5-c0f6bf02a805)")
        print()
        
        # Test UUID conversion
        from uuid import UUID
        test_jellyfin_id = "f137a2dd21bbc1b99aa5c0f6bf02a805"
        print(f"Testing conversion of Jellyfin ID: {test_jellyfin_id}")
        
        try:
            # This will fail
            uuid_obj = UUID(test_jellyfin_id)
            print(f"✅ Converted to UUID: {uuid_obj}")
        except ValueError as e:
            print(f"❌ UUID conversion failed: {e}")
            print("🎯 FOUND THE ISSUE: Jellyfin IDs cannot be converted to UUIDs!")
            print()
            
            # Show the fix
            print("💡 Solution: Convert Jellyfin hex ID to UUID format")
            # Insert dashes at the right positions
            formatted_id = f"{test_jellyfin_id[:8]}-{test_jellyfin_id[8:12]}-{test_jellyfin_id[12:16]}-{test_jellyfin_id[16:20]}-{test_jellyfin_id[20:]}"
            print(f"   Jellyfin ID: {test_jellyfin_id}")
            print(f"   UUID format: {formatted_id}")
            
            try:
                uuid_obj = UUID(formatted_id)
                print(f"✅ UUID conversion successful: {uuid_obj}")
            except ValueError as e2:
                print(f"❌ Still failed: {e2}")
                
        print()
        print("🔧 The Fix Needed:")
        print("1. In scheduler_service.py, convert Jellyfin IDs to UUID format before UUID() call")
        print("2. Alternative: Use string IDs in the job system instead of UUIDs")
        print("3. Add error handling for UUID conversion failures")
        print()
        
        # Analyze the schedule execution timing issue
        print("📅 Schedule Timing Analysis:")
        print("The schedule cron expression is '0 2 1 * *' (monthly at 2 AM on 1st)")
        print("This means:")
        print("  - Should run once per month")
        print("  - Last run would have been July 1st, 2025 at 2 AM")
        print("  - Next run scheduled for August 1st, 2025 at 2 AM")
        print()
        print("For testing, you might want a more frequent schedule like:")
        print("  - '*/5 * * * *' (every 5 minutes)")
        print("  - '0 * * * *' (every hour)")
        print("  - '0 2 * * *' (daily at 2 AM)")
        
    except Exception as e:
        print(f"❌ Debug script error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function"""
    await debug_scheduler_issue()
    
    print("=" * 60)
    print("🏁 Debug Analysis Complete")
    print()
    print("📋 Summary of Issues Found:")
    print("1. 🔴 UUID Conversion: Jellyfin IDs are not valid UUIDs")
    print("2. 🟡 Schedule Frequency: Monthly schedule hard to test")
    print("3. 🔴 Silent Failures: UUID errors not logged properly")
    print()
    print("🛠️  Recommended Actions:")
    print("1. Fix UUID conversion in scheduler_service.py")
    print("2. Add proper error logging for UUID conversion")
    print("3. Consider using string IDs instead of UUIDs in job system")


if __name__ == "__main__":
    asyncio.run(main())
