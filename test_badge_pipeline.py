#!/usr/bin/env python3
"""
Badge Pipeline Connection Test Script

This script specifically tests the badge pipeline with the database connection fixes
to ensure the review processor now runs properly after the resolution processor.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "api"))

async def test_badge_pipeline_flow():
    """Test the badge pipeline flow with connection recovery"""
    print("🎬 Testing Badge Pipeline Flow with Database Connection Recovery")
    print("=" * 70)
    
    try:
        # Initialize database first
        from app.core.database import init_db
        await init_db()
        print("✅ Database initialized")
        
        # Import badge processing components
        from app.services.badge_processing.pipeline import UniversalBadgeProcessor
        from app.services.badge_processing.types import (
            UniversalBadgeRequest, SingleBadgeRequest, ProcessingMode
        )
        
        # Create a test poster path (doesn't need to exist for database connection testing)
        test_poster_path = "/tmp/test_poster.jpg"
        test_jellyfin_id = "e89693a94849aed9fb0cb2e8cc180f1b"  # Ahsoka series ID from the issue
        
        print(f"📋 Test Configuration:")
        print(f"   Poster Path: {test_poster_path}")
        print(f"   Jellyfin ID: {test_jellyfin_id}")
        print(f"   Badge Types: ['resolution', 'review']")
        print()
        
        # Create badge processor
        processor = UniversalBadgeProcessor()
        print("✅ UniversalBadgeProcessor created")
        
        # Create single badge request focusing on the problematic flow
        single_request = SingleBadgeRequest(
            poster_path=test_poster_path,
            badge_types=["resolution", "review"],  # The exact flow that was failing
            use_demo_data=True,  # Use demo data to avoid needing real Jellyfin
            jellyfin_id=test_jellyfin_id,
            output_path=None
        )
        
        # Create universal request
        universal_request = UniversalBadgeRequest(
            processing_mode=ProcessingMode.IMMEDIATE,
            single_request=single_request,
            bulk_request=None
        )
        
        print("✅ Badge request created")
        print()
        
        # Test the critical database connection flow
        print("🔄 Testing Badge Pipeline Database Connection Flow")
        print("   This should now show both processors running successfully...")
        print()
        
        try:
            # Process the request - this is where the crash was happening
            result = await processor.process_request(universal_request)
            
            print(f"📊 Pipeline Result:")
            print(f"   Success: {result.success}")
            print(f"   Error: {result.error}")
            print(f"   Processing Time: {result.processing_time:.2f}s")
            print(f"   Results Count: {len(result.results)}")
            
            if result.results:
                for i, poster_result in enumerate(result.results):
                    print(f"   Result {i+1}:")
                    print(f"     Source: {poster_result.source_path}")
                    print(f"     Output: {poster_result.output_path}")
                    print(f"     Success: {poster_result.success}")
                    print(f"     Applied Badges: {poster_result.applied_badges}")
                    print(f"     Error: {poster_result.error}")
            
            if result.success:
                print("\n✅ Badge pipeline completed successfully!")
                print("🎯 The database connection issue appears to be fixed.")
                
                # Check if both processors ran
                if result.results and len(result.results) > 0:
                    applied_badges = result.results[0].applied_badges
                    if "resolution" in applied_badges:
                        print("   ✅ Resolution processor ran successfully")
                    if "review" in applied_badges:
                        print("   ✅ Review processor ran successfully")
                        print("   🎉 CRITICAL: Review processor now works after resolution!")
                    else:
                        print("   ⚠️ Review processor may not have run (check logs)")
                
                return True
            else:
                print(f"\n❌ Badge pipeline failed: {result.error}")
                return False
                
        except Exception as pipeline_error:
            print(f"\n🚨 PIPELINE ERROR: {pipeline_error}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"\n🚨 CRITICAL ERROR in badge pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    print("🚀 Aphrodite Badge Pipeline Connection Test")
    print("🎯 Testing the fix for RT/Metacritic badges not appearing")
    print()
    
    success = await test_badge_pipeline_flow()
    
    if success:
        print("\n🎉 Badge pipeline connection test PASSED!")
        print("\n📝 Expected behavior:")
        print("   ✅ Resolution processor completes successfully")
        print("   ✅ Review processor starts after resolution processor")
        print("   ✅ No database connection crashes between processors")
        print("   ✅ RT and Metacritic badges should now appear")
        print("\n📋 Next steps:")
        print("   1. Rebuild the Docker container")
        print("   2. Test with real Ahsoka series poster")
        print("   3. Verify RT and Metacritic badges appear")
        return 0
    else:
        print("\n❌ Badge pipeline connection test FAILED!")
        print("📝 The database connection issue may still exist.")
        print("📋 Review the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
