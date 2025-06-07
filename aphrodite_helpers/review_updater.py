"""
Review Update Management for Aphrodite Database Tracking

Handles intelligent review data updates, cache management, and batch processing
for keeping review information current across the media library.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

from aphrodite_helpers.database_manager import DatabaseManager
from aphrodite_helpers.apply_review_badges import process_item_reviews


class ReviewUpdater:
    """
    Manages review data updates and cache management for processed items.
    
    Key Features:
    - Detect items with stale review data
    - Batch update reviews with rate limiting
    - Cache management and expiration handling
    - Integration with existing review badge processing
    """
    
    def __init__(self, jellyfin_url: str, api_key: str, user_id: str):
        self.jellyfin_url = jellyfin_url
        self.api_key = api_key
        self.user_id = user_id
        self.db_manager = DatabaseManager()
    
    def close(self):
        """Clean up database connections."""
        if self.db_manager:
            self.db_manager.close()
    
    def check_items_needing_review_update(self, library_id: Optional[str] = None, 
                                        hours_threshold: int = 24) -> List[Dict[str, Any]]:
        """
        Query database for items with stale review data.
        
        Args:
            library_id: Optional library ID to filter by
            hours_threshold: Hours since last review check to consider stale
            
        Returns:
            List of items that need review updates
        """
        conn = self.db_manager.get_connection()
        
        # Calculate threshold timestamp
        threshold_time = datetime.now() - timedelta(hours=hours_threshold)
        threshold_iso = threshold_time.isoformat()
        
        # Build query with optional library filter
        where_clauses = [
            "(reviews_last_checked IS NULL OR reviews_last_checked < ?)",
            "last_processing_status = 'success'"  # Only update successful items
        ]
        params = [threshold_iso]
        
        if library_id:
            where_clauses.append("jellyfin_library_id = ?")
            params.append(library_id)
        
        query = f"""
            SELECT jellyfin_item_id, title, item_type, jellyfin_library_id,
                   reviews_last_checked, reviews_cache_expiry, highest_review_score,
                   external_ids, last_processed_at
            FROM processed_items 
            WHERE {' AND '.join(where_clauses)}
            ORDER BY 
                CASE WHEN reviews_last_checked IS NULL THEN 0 ELSE 1 END,
                reviews_last_checked ASC,
                last_processed_at DESC
        """
        
        cursor = conn.execute(query, params)
        items = []
        
        for row in cursor.fetchall():
            item_data = dict(row)
            # Parse external_ids if present
            if item_data.get('external_ids'):
                try:
                    import json
                    item_data['external_ids'] = json.loads(item_data['external_ids'])
                except json.JSONDecodeError:
                    item_data['external_ids'] = {}
            items.append(item_data)
        
        return items
    
    def update_reviews_for_item(self, item_id: str, poster_path: Optional[str] = None) -> bool:
        """
        Re-fetch and update review data for a single item.
        
        Args:
            item_id: Jellyfin item ID to update
            poster_path: Optional poster path for badge regeneration
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            print(f"🔄 Updating reviews for item {item_id}")
            
            # Get current item data from database
            item_data = self.db_manager.get_processed_item(item_id)
            if not item_data:
                print(f"⚠️ Item {item_id} not found in database")
                return False
            
            # Determine poster path if not provided
            if not poster_path and item_data.get('poster_modified_path'):
                poster_path = item_data['poster_modified_path']
            
            # Re-process reviews (this will update the database automatically)
            review_success = process_item_reviews(
                item_id,
                self.jellyfin_url,
                self.api_key,
                self.user_id,
                "badge_settings_review.yml",
                "posters/modified",
                poster_path
            )
            
            # Update review check timestamp regardless of review success
            # (to avoid repeatedly checking items with no available reviews)
            now = datetime.now().isoformat()
            cache_expiry = (datetime.now() + timedelta(hours=24)).isoformat()
            
            update_data = {
                'reviews_last_checked': now,
                'reviews_cache_expiry': cache_expiry
            }
            
            self.db_manager.update_processed_item(item_id, update_data)
            
            if review_success:
                print(f"✅ Successfully updated reviews for {item_data.get('title', item_id)}")
            else:
                print(f"ℹ️ No reviews found for {item_data.get('title', item_id)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating reviews for {item_id}: {e}")
            return False
    
    def bulk_update_reviews(self, item_list: List[str], rate_limit_seconds: float = 2.0,
                           max_items: Optional[int] = None) -> Dict[str, int]:
        """
        Update reviews for multiple items with rate limiting.
        
        Args:
            item_list: List of Jellyfin item IDs to update
            rate_limit_seconds: Delay between API calls
            max_items: Maximum number of items to process (for testing)
            
        Returns:
            Dictionary with update statistics
        """
        if max_items:
            item_list = item_list[:max_items]
        
        stats = {
            'total': len(item_list),
            'successful': 0,
            'failed': 0,
            'no_reviews': 0
        }
        
        print(f"🔄 Starting bulk review update for {stats['total']} items")
        print(f"⏱️ Rate limit: {rate_limit_seconds}s between items")
        
        for i, item_id in enumerate(item_list, 1):
            print(f"\n[{i}/{stats['total']}] Processing {item_id}")
            
            try:
                success = self.update_reviews_for_item(item_id)
                if success:
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
                
                # Rate limiting between items
                if i < len(item_list):  # Don't sleep after the last item
                    time.sleep(rate_limit_seconds)
                    
            except Exception as e:
                print(f"❌ Error processing {item_id}: {e}")
                stats['failed'] += 1
        
        print(f"\n📊 Bulk update complete:")
        print(f"  ✅ Successful: {stats['successful']}")
        print(f"  ❌ Failed: {stats['failed']}")
        print(f"  📋 Total: {stats['total']}")
        
        return stats
    
    def get_review_update_summary(self, library_id: Optional[str] = None, 
                                hours_threshold: int = 24) -> Dict[str, Any]:
        """
        Get summary of items that need review updates without actually updating them.
        
        Args:
            library_id: Optional library ID to filter by
            hours_threshold: Hours since last review check
            
        Returns:
            Summary dictionary with counts and details
        """
        items_needing_update = self.check_items_needing_review_update(library_id, hours_threshold)
        
        # Categorize by how old the data is
        now = datetime.now()
        categories = {
            'never_checked': [],
            'very_stale': [],  # > 7 days
            'stale': [],       # > 1 day
            'recent': []       # within threshold but still stale
        }
        
        for item in items_needing_update:
            if not item.get('reviews_last_checked'):
                categories['never_checked'].append(item)
            else:
                try:
                    last_checked = datetime.fromisoformat(item['reviews_last_checked'])
                    days_old = (now - last_checked).days
                    
                    if days_old > 7:
                        categories['very_stale'].append(item)
                    elif days_old > 1:
                        categories['stale'].append(item)
                    else:
                        categories['recent'].append(item)
                except ValueError:
                    categories['never_checked'].append(item)
        
        summary = {
            'total_items': len(items_needing_update),
            'library_id': library_id,
            'hours_threshold': hours_threshold,
            'categories': {
                'never_checked': len(categories['never_checked']),
                'very_stale': len(categories['very_stale']),
                'stale': len(categories['stale']),
                'recent': len(categories['recent'])
            },
            'items': categories
        }
        
        return summary
    
    def cleanup_expired_reviews(self) -> int:
        """
        Remove expired review entries from the database.
        
        Returns:
            Number of expired entries removed
        """
        conn = self.db_manager.get_connection()
        now = datetime.now().isoformat()
        
        # Find reviews with expired cache
        cursor = conn.execute("""
            SELECT r.id FROM item_reviews r
            JOIN processed_items p ON r.processed_item_id = p.id
            WHERE r.cache_expires_at IS NOT NULL AND r.cache_expires_at < ?
        """, (now,))
        
        expired_ids = [row[0] for row in cursor.fetchall()]
        
        if expired_ids:
            placeholders = ','.join(['?' for _ in expired_ids])
            conn.execute(f"DELETE FROM item_reviews WHERE id IN ({placeholders})", expired_ids)
            conn.commit()
            
            print(f"🧹 Cleaned up {len(expired_ids)} expired review entries")
        
        return len(expired_ids)
