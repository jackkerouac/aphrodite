"""
Database-integrated processing wrapper for Aphrodite.

This module provides database tracking functionality for the main processing pipeline
without requiring major changes to the existing aphrodite.py structure.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from aphrodite_helpers.database_manager import DatabaseManager
from aphrodite_helpers.item_data_collector import ItemDataCollector


def process_item_with_database_tracking(
    jellyfin_url: str, 
    api_key: str, 
    user_id: str,
    item_id: str,
    processing_options: Dict[str, bool],
    original_process_function,
    *args, 
    **kwargs
) -> bool:
    """
    Wrapper function that adds database tracking to the existing process_single_item function.
    
    This function:
    1. Initializes database tracking before processing
    2. Calls the original processing function
    3. Updates database with results after processing
    
    Args:
        jellyfin_url: Jellyfin server URL
        api_key: Jellyfin API key
        user_id: Jellyfin user ID
        item_id: Item to process
        processing_options: Dict with badge options (audio, resolution, reviews, awards)
        original_process_function: The original process_single_item function
        *args, **kwargs: Additional arguments for the original function
        
    Returns:
        bool: Success status from the original processing function
    """
    
    processing_start_time = time.time()
    db_manager = None
    success = False
    
    try:
        # Initialize database tracking
        db_manager = DatabaseManager()
        data_collector = ItemDataCollector(jellyfin_url, api_key, user_id)
        
        # Collect item metadata for database
        item_metadata = data_collector.collect_item_metadata(item_id)
        
        # Check if item was already processed
        existing_item = db_manager.get_processed_item(item_id)
        
        if existing_item:
            print(f"🗄️ Found existing database record for item")
            # Update status to processing
            db_manager.update_processed_item(item_id, {
                'last_processing_status': 'processing',
                'last_processed_at': datetime.now().isoformat()
            })
        else:
            # Create new record with processing status
            item_metadata.update({
                'last_processing_status': 'processing',
                'badges_requested': processing_options,
                'last_processing_version': 'v3.x.x'  # TODO: Get from version file
            })
            
            # Generate settings hash for future change detection
            settings_hash = data_collector.generate_settings_hash(item_metadata)
            item_metadata['settings_hash'] = settings_hash
            
            db_manager.insert_processed_item(item_metadata)
            print(f"🗄️ Created new database record for item")
        
        # Update database with poster info if available
        try:
            poster_info = data_collector.get_poster_info(item_id)
            if poster_info:
                db_manager.update_processed_item(item_id, poster_info)
        except Exception:
            pass
        
        # Call the original processing function
        success = original_process_function(*args, **kwargs)
        
        # Update database with final status
        processing_duration = time.time() - processing_start_time
        
        if success:
            final_status = 'success'
            error_message = None
        else:
            final_status = 'failed'
            error_message = 'Processing function returned False'
        
        update_data = {
            'last_processing_status': final_status,
            'last_processing_duration': processing_duration
        }
        
        if error_message:
            update_data['last_error_message'] = error_message
        
        db_manager.update_processed_item(item_id, update_data)
        print(f"🗄️ Updated database with {final_status} status")
        
    except Exception as e:
        print(f"⚠️ Database tracking error: {e}")
        
        # Still try to update database with error status
        if db_manager:
            try:
                db_manager.update_processed_item(item_id, {
                    'last_processing_status': 'failed',
                    'last_error_message': str(e),
                    'last_processing_duration': time.time() - processing_start_time
                })
            except Exception:
                pass
        
        # Continue processing even if database tracking fails
        success = original_process_function(*args, **kwargs)
    
    finally:
        if db_manager:
            db_manager.close()
    
    return success


def enhance_badges_applied_tracking(
    item_id: str,
    badges_applied: Dict[str, Any]
) -> None:
    """
    Update database with information about which badges were successfully applied.
    
    Args:
        item_id: Jellyfin item ID
        badges_applied: Dictionary of applied badges {badge_type: badge_value}
    """
    try:
        db_manager = DatabaseManager()
        
        update_data = {
            'badges_applied': badges_applied
        }
        
        db_manager.update_processed_item(item_id, update_data)
        
    except Exception as e:
        print(f"⚠️ Failed to update badges applied: {e}")
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def update_poster_path(item_id: str, poster_path: str) -> None:
    """
    Update database with the final poster path.
    
    Args:
        item_id: Jellyfin item ID
        poster_path: Path to the modified poster
    """
    try:
        db_manager = DatabaseManager()
        
        update_data = {
            'poster_modified_path': poster_path
        }
        
        db_manager.update_processed_item(item_id, update_data)
        
    except Exception as e:
        print(f"⚠️ Failed to update poster path: {e}")
    finally:
        if 'db_manager' in locals():
            db_manager.close()
