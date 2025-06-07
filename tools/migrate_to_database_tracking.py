#!/usr/bin/env python3
"""
Migration Script for Aphrodite Database Tracking

This script creates the new database tables required for item tracking
and can migrate existing metadata tags to database records.

Usage:
    python tools/migrate_to_database_tracking.py
    
This script is also called automatically by DatabaseManager.__init__()
so users never need to run it manually.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import aphrodite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aphrodite_helpers.database_manager import DatabaseManager
from aphrodite_helpers.check_jellyfin_connection import load_settings


def run_migration():
    """
    Run the database migration to create item tracking tables.
    
    This is safe to run multiple times - it only creates tables that don't exist.
    """
    print("🚀 Starting Aphrodite Database Migration")
    print("=" * 50)
    
    try:
        # Initialize DatabaseManager - this automatically creates tables
        print("📋 Initializing database manager...")
        db_manager = DatabaseManager()
        
        print("✅ Database schema initialized successfully!")
        print("\nNew tables created:")
        print("  - processed_items: Track all processed media items")
        print("  - item_reviews: Store review data from various sources")
        print("  - schema_versions: Track database schema versions")
        
        # Verify tables were created
        conn = db_manager.get_connection()
        
        # Check processed_items table
        cursor = conn.execute("SELECT COUNT(*) FROM processed_items")
        processed_count = cursor.fetchone()[0]
        print(f"\n📊 Current status:")
        print(f"  - Processed items: {processed_count}")
        
        # Check item_reviews table
        cursor = conn.execute("SELECT COUNT(*) FROM item_reviews")
        reviews_count = cursor.fetchone()[0]
        print(f"  - Stored reviews: {reviews_count}")
        
        # Check schema version
        cursor = conn.execute("SELECT version FROM schema_versions WHERE component = 'item_tracking'")
        schema_version = cursor.fetchone()[0]
        print(f"  - Schema version: {schema_version}")
        
        db_manager.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Start processing items normally - they'll be tracked automatically")
        print("  2. Use 'python aphrodite.py db-status' to view processing statistics")
        print("  3. Use '--skip-processed' flag for faster library processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        print("\nFull error details:")
        print(traceback.format_exc())
        return False


def migrate_existing_metadata_tags():
    """
    Future feature: Migrate existing metadata tags to database records.
    
    This will scan for items with the aphrodite-overlay tag and create
    database records for them, preserving processing history.
    """
    print("\n🏷️ Metadata tag migration not yet implemented")
    print("This feature will be added in a future update to preserve")
    print("existing processing history from metadata tags.")


def test_database_operations():
    """
    Test basic database operations to ensure everything is working.
    """
    print("\n🧪 Testing database operations...")
    
    try:
        db_manager = DatabaseManager()
        
        # Test data
        test_item = {
            'jellyfin_item_id': 'test_' + str(int(time.time())),
            'jellyfin_library_id': 'test_library',
            'jellyfin_user_id': 'test_user',
            'item_type': 'Movie',
            'title': 'Test Movie',
            'year': 2023,
            'last_processing_status': 'success',
            'badges_requested': {'audio': True, 'resolution': True},
            'badges_applied': {'audio': 'DTS-HD MA', 'resolution': '4K'}
        }
        
        # Test insert
        print("  Testing insert...")
        item_id = db_manager.insert_processed_item(test_item)
        print(f"  ✅ Inserted test item with ID: {item_id}")
        
        # Test retrieve
        print("  Testing retrieve...")
        retrieved = db_manager.get_processed_item(test_item['jellyfin_item_id'])
        if retrieved:
            print(f"  ✅ Retrieved item: {retrieved['title']}")
        else:
            print("  ❌ Failed to retrieve item")
            return False
        
        # Test update
        print("  Testing update...")
        update_success = db_manager.update_processed_item(
            test_item['jellyfin_item_id'],
            {'last_processing_status': 'updated', 'processing_count': 2}
        )
        if update_success:
            print("  ✅ Updated item successfully")
        else:
            print("  ❌ Failed to update item")
            return False
        
        # Test reviews
        print("  Testing review insertion...")
        test_reviews = [
            {
                'source': 'imdb',
                'score': 8.5,
                'score_max': 10.0,
                'score_text': '8.5/10',
                'review_count': 12000
            },
            {
                'source': 'rottentomatoes',
                'score': 85.0,
                'score_max': 100.0,
                'score_text': '85%',
                'review_count': 150
            }
        ]
        
        reviews_success = db_manager.insert_item_reviews(item_id, test_reviews)
        if reviews_success:
            print("  ✅ Inserted test reviews")
        else:
            print("  ❌ Failed to insert reviews")
            return False
        
        # Test statistics
        print("  Testing statistics...")
        stats = db_manager.get_processing_statistics()
        print(f"  ✅ Statistics: {stats['total_items']} total items")
        
        # Clean up test data
        conn = db_manager.get_connection()
        conn.execute("DELETE FROM processed_items WHERE jellyfin_item_id = ?", 
                    (test_item['jellyfin_item_id'],))
        conn.commit()
        print("  ✅ Cleaned up test data")
        
        db_manager.close()
        print("\n🎯 All database operations working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  APHRODITE DATABASE TRACKING MIGRATION")
    print("=" * 60)
    
    success = True
    
    # Step 1: Run main migration
    if not run_migration():
        success = False
    
    # Step 2: Test database operations
    if success and not test_database_operations():
        success = False
    
    # Step 3: Future metadata migration (placeholder)
    if success:
        migrate_existing_metadata_tags()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("\nYour Aphrodite installation now supports:")
        print("  ✅ Automatic item tracking")
        print("  ✅ Processing history")
        print("  ✅ Review caching")
        print("  ✅ Smart skip-processed functionality")
        print("  ✅ Processing statistics")
    else:
        print("❌ MIGRATION FAILED!")
        print("Please check the error messages above and try again.")
    
    print("=" * 60)
    sys.exit(0 if success else 1)
