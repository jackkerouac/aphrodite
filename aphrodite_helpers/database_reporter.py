"""
Database Reporting and Statistics for Aphrodite

Provides comprehensive reporting on processing statistics, item status,
and database insights for monitoring and analysis.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

from aphrodite_helpers.database_manager import DatabaseManager


class DatabaseReporter:
    """
    Generate reports and statistics from the Aphrodite database.
    
    Provides insights into:
    - Processing success/failure rates
    - Performance metrics
    - Review data analysis
    - Item processing history
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def close(self):
        """Clean up database connections."""
        if self.db_manager:
            self.db_manager.close()
    
    def get_database_status(self, library_id: Optional[str] = None, 
                          detailed: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive database status and statistics.
        
        Args:
            library_id: Optional library ID to filter by
            detailed: Include detailed item listings
            
        Returns:
            Dictionary containing database status information
        """
        conn = self.db_manager.get_connection()
        
        # Build base query components
        where_clause = ""
        params = []
        if library_id:
            where_clause = "WHERE jellyfin_library_id = ?"
            params.append(library_id)
        
        # Total processed items
        cursor = conn.execute(f"SELECT COUNT(*) FROM processed_items {where_clause}", params)
        total_items = cursor.fetchone()[0]
        
        # Status breakdown
        cursor = conn.execute(f"""
            SELECT last_processing_status, COUNT(*) as count
            FROM processed_items {where_clause}
            GROUP BY last_processing_status
            ORDER BY count DESC
        """, params)
        
        status_counts = {}
        for row in cursor.fetchall():
            status_counts[row[0]] = row[1]
        
        # Success rate
        successful = status_counts.get('success', 0)
        success_rate = (successful / max(total_items, 1)) * 100
        
        # Processing times
        cursor = conn.execute(f"""
            SELECT 
                AVG(last_processing_duration) as avg_time,
                MIN(last_processing_duration) as min_time,
                MAX(last_processing_duration) as max_time,
                COUNT(last_processing_duration) as time_count
            FROM processed_items 
            {where_clause}
            {"AND" if where_clause else "WHERE"} last_processing_duration IS NOT NULL
        """, params)
        
        time_stats = cursor.fetchone()
        processing_times = {
            'average': round(time_stats[0], 2) if time_stats[0] else None,
            'minimum': round(time_stats[1], 2) if time_stats[1] else None,
            'maximum': round(time_stats[2], 2) if time_stats[2] else None,
            'items_with_timing': time_stats[3]
        }
        
        # Recent activity (last 24 hours, 7 days, 30 days)
        now = datetime.now()
        periods = {
            '24h': now - timedelta(hours=24),
            '7d': now - timedelta(days=7),
            '30d': now - timedelta(days=30)
        }
        
        recent_activity = {}
        for period_name, threshold in periods.items():
            threshold_iso = threshold.isoformat()
            cursor = conn.execute(f"""
                SELECT COUNT(*) FROM processed_items 
                {where_clause}
                {"AND" if where_clause else "WHERE"} last_processed_at > ?
            """, params + [threshold_iso])
            recent_activity[period_name] = cursor.fetchone()[0]
        
        # Item type breakdown
        cursor = conn.execute(f"""
            SELECT item_type, COUNT(*) as count
            FROM processed_items {where_clause}
            GROUP BY item_type
            ORDER BY count DESC
        """, params)
        
        item_types = {}
        for row in cursor.fetchall():
            item_types[row[0]] = row[1]
        
        # Review statistics
        cursor = conn.execute(f"""
            SELECT 
                COUNT(DISTINCT p.id) as items_with_reviews,
                COUNT(r.id) as total_reviews,
                AVG(r.score) as avg_score,
                MIN(r.score) as min_score,
                MAX(r.score) as max_score
            FROM processed_items p
            LEFT JOIN item_reviews r ON p.id = r.processed_item_id
            {where_clause}
        """, params)
        
        review_row = cursor.fetchone()
        review_stats = {
            'items_with_reviews': review_row[0],
            'total_review_entries': review_row[1],
            'average_score': round(review_row[2], 2) if review_row[2] else None,
            'minimum_score': review_row[3],
            'maximum_score': review_row[4]
        }
        
        # Error analysis
        cursor = conn.execute(f"""
            SELECT 
                COUNT(*) as failed_items,
                COUNT(DISTINCT last_error_message) as unique_errors
            FROM processed_items 
            {where_clause}
            {"AND" if where_clause else "WHERE"} last_processing_status = 'failed'
        """, params)
        
        error_row = cursor.fetchone()
        error_stats = {
            'failed_items': error_row[0],
            'unique_error_types': error_row[1]
        }
        
        # Common errors (top 5)
        cursor = conn.execute(f"""
            SELECT last_error_message, COUNT(*) as count
            FROM processed_items 
            {where_clause}
            {"AND" if where_clause else "WHERE"} last_error_message IS NOT NULL
            GROUP BY last_error_message
            ORDER BY count DESC
            LIMIT 5
        """, params)
        
        common_errors = []
        for row in cursor.fetchall():
            common_errors.append({
                'error': row[0],
                'count': row[1]
            })
        
        # Compile status report
        status = {
            'library_id': library_id,
            'total_items': total_items,
            'status_breakdown': status_counts,
            'success_rate': round(success_rate, 1),
            'processing_times': processing_times,
            'recent_activity': recent_activity,
            'item_types': item_types,
            'review_statistics': review_stats,
            'error_analysis': error_stats,
            'common_errors': common_errors,
            'generated_at': datetime.now().isoformat()
        }
        
        # Add detailed item listings if requested
        if detailed:
            status['detailed_items'] = self._get_detailed_item_list(library_id)
        
        return status
    
    def _get_detailed_item_list(self, library_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get detailed list of processed items."""
        conn = self.db_manager.get_connection()
        
        where_clause = ""
        params = []
        if library_id:
            where_clause = "WHERE jellyfin_library_id = ?"
            params.append(library_id)
        
        cursor = conn.execute(f"""
            SELECT 
                jellyfin_item_id, title, item_type, last_processing_status,
                last_processed_at, last_processing_duration, processing_count,
                highest_review_score, lowest_review_score, last_error_message
            FROM processed_items {where_clause}
            ORDER BY last_processed_at DESC
        """, params)
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'item_id': row[0],
                'title': row[1],
                'type': row[2],
                'status': row[3],
                'last_processed': row[4],
                'duration': row[5],
                'processing_count': row[6],
                'highest_score': row[7],
                'lowest_score': row[8],
                'error': row[9]
            })
        
        return items
    
    def get_items_for_reprocessing(self, 
                                 failed_only: bool = False,
                                 older_than_days: Optional[int] = None,
                                 library_id: Optional[str] = None,
                                 settings_changed: bool = False) -> List[Dict[str, Any]]:
        """
        Get items that meet reprocessing criteria.
        
        Args:
            failed_only: Only include failed items
            older_than_days: Only include items processed more than X days ago
            library_id: Filter by library ID
            settings_changed: Include items where settings might have changed
            
        Returns:
            List of items meeting the criteria
        """
        conn = self.db_manager.get_connection()
        
        where_clauses = []
        params = []
        
        # Filter by status
        if failed_only:
            where_clauses.append("last_processing_status = 'failed'")
        
        # Filter by age
        if older_than_days:
            threshold = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            where_clauses.append("last_processed_at < ?")
            params.append(threshold)
        
        # Filter by library
        if library_id:
            where_clauses.append("jellyfin_library_id = ?")
            params.append(library_id)
        
        # Settings change detection (simplified - would need more complex logic)
        if settings_changed:
            where_clauses.append("settings_hash IS NULL OR settings_hash != 'current_hash'")
        
        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)
        
        cursor = conn.execute(f"""
            SELECT 
                jellyfin_item_id, title, item_type, last_processing_status,
                last_processed_at, retry_count, last_error_message,
                jellyfin_library_id
            FROM processed_items 
            {where_clause}
            ORDER BY 
                CASE WHEN last_processing_status = 'failed' THEN 0 ELSE 1 END,
                last_processed_at ASC
        """, params)
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'item_id': row[0],
                'title': row[1],
                'type': row[2],
                'status': row[3],
                'last_processed': row[4],
                'retry_count': row[5],
                'error': row[6],
                'library_id': row[7]
            })
        
        return items
    
    def get_database_processed_items(self, library_id: str) -> List[str]:
        """
        Get list of item IDs that have been successfully processed (database version).
        This replaces the metadata tag checking for much faster skip-processed functionality.
        
        Args:
            library_id: Library ID to check
            
        Returns:
            List of Jellyfin item IDs that have been successfully processed
        """
        conn = self.db_manager.get_connection()
        
        cursor = conn.execute("""
            SELECT jellyfin_item_id 
            FROM processed_items 
            WHERE jellyfin_library_id = ? 
            AND last_processing_status = 'success'
        """, (library_id,))
        
        return [row[0] for row in cursor.fetchall()]
    

    def get_processed_items_hybrid(self, library_id: str, jellyfin_url: str, 
                                  api_key: str, user_id: str) -> List[str]:
        """
        Get list of item IDs that have been processed using BOTH database records 
        AND metadata tags for complete accuracy.
        
        This hybrid approach ensures we catch:
        1. Items processed and recorded in database 
        2. Items processed before database tracking (have metadata tags only)
        3. Items that may have failed database recording but have tags
        
        Args:
            library_id: Library ID to check
            jellyfin_url: Jellyfin server URL
            api_key: Jellyfin API key  
            user_id: Jellyfin user ID
            
        Returns:
            List of Jellyfin item IDs that have been processed
        """
        processed_items = set()
        
        # 1. Get items from database (fast)
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT jellyfin_item_id 
                FROM processed_items 
                WHERE jellyfin_library_id = ? 
                AND last_processing_status IN ('success', 'partial_success')
            """, (library_id,))
            
            db_items = {row[0] for row in cursor.fetchall()}
            processed_items.update(db_items)
            print(f"📊 Database found {len(db_items)} processed items")
            
        except Exception as e:
            print(f"⚠️ Database check failed: {e}")
            db_items = set()
        
        # 2. Get items with metadata tags (thorough but slower)
        try:
            from aphrodite_helpers.metadata_tagger import MetadataTagger, get_tagging_settings
            
            tagging_settings = get_tagging_settings()
            tag_name = tagging_settings.get('tag_name', 'aphrodite-overlay')
            tagger = MetadataTagger(jellyfin_url, api_key, user_id)
            
            # Get all items in library
            from aphrodite_helpers.check_jellyfin_connection import get_library_items
            all_items = get_library_items(jellyfin_url, api_key, user_id, library_id)
            
            if all_items:
                tag_items = set()
                for item in all_items:
                    item_id = item.get('Id')
                    if item_id and tagger.check_aphrodite_tag(item_id, tag_name):
                        tag_items.add(item_id)
                
                processed_items.update(tag_items)
                print(f"📊 Metadata tags found {len(tag_items)} processed items")
                
                # Report any discrepancies for debugging
                db_only = db_items - tag_items
                tag_only = tag_items - db_items
                
                if db_only:
                    print(f"📝 Note: {len(db_only)} items in database but no metadata tag")
                if tag_only:
                    print(f"📝 Note: {len(tag_only)} items with metadata tag but not in database")
                    
        except Exception as e:
            print(f"⚠️ Metadata tag check failed: {e}")
        
        total_processed = list(processed_items)
        print(f"📊 Hybrid method found {len(total_processed)} total processed items")
        return total_processed

    def export_processing_data(self, library_id: Optional[str] = None, 
                             format: str = 'json') -> Dict[str, Any]:
        """
        Export processing data for external analysis.
        
        Args:
            library_id: Optional library ID filter
            format: Export format ('json', 'csv_data')
            
        Returns:
            Exported data structure
        """
        conn = self.db_manager.get_connection()
        
        where_clause = ""
        params = []
        if library_id:
            where_clause = "WHERE jellyfin_library_id = ?"
            params.append(library_id)
        
        # Get all processed items with review data
        cursor = conn.execute(f"""
            SELECT 
                p.jellyfin_item_id, p.title, p.item_type, p.year,
                p.last_processing_status, p.last_processed_at,
                p.last_processing_duration, p.processing_count,
                p.badges_requested, p.badges_applied,
                p.highest_review_score, p.lowest_review_score,
                p.jellyfin_library_id, p.external_ids,
                p.last_error_message, p.created_at
            FROM processed_items p
            {where_clause}
            ORDER BY p.last_processed_at DESC
        """, params)
        
        items = []
        for row in cursor.fetchall():
            item_data = {
                'item_id': row[0],
                'title': row[1],
                'type': row[2],
                'year': row[3],
                'status': row[4],
                'processed_at': row[5],
                'duration': row[6],
                'processing_count': row[7],
                'badges_requested': row[8],
                'badges_applied': row[9],
                'highest_score': row[10],
                'lowest_score': row[11],
                'library_id': row[12],
                'external_ids': row[13],
                'error': row[14],
                'created_at': row[15]
            }
            
            # Parse JSON fields
            json_fields = ['badges_requested', 'badges_applied', 'external_ids']
            for field in json_fields:
                if item_data[field]:
                    try:
                        item_data[field] = json.loads(item_data[field])
                    except json.JSONDecodeError:
                        item_data[field] = {}
            
            items.append(item_data)
        
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'library_id': library_id,
                'total_items': len(items),
                'format': format
            },
            'items': items
        }
        
        # Add summary statistics
        export_data['summary'] = self.get_database_status(library_id, detailed=False)
        
        return export_data
    
    def print_status_report(self, library_id: Optional[str] = None, detailed: bool = False):
        """
        Print a formatted status report to console.
        
        Args:
            library_id: Optional library ID to filter by
            detailed: Include detailed item listings
        """
        status = self.get_database_status(library_id, detailed)
        
        # Header
        print("\n" + "="*60)
        print("📊 APHRODITE DATABASE STATUS REPORT")
        print("="*60)
        
        if library_id:
            print(f"📚 Library: {library_id}")
        else:
            print("📚 All Libraries")
        
        print(f"🕒 Generated: {status['generated_at']}")
        print()
        
        # Summary
        print("📈 SUMMARY")
        print("-" * 20)
        print(f"Total Items: {status['total_items']}")
        print(f"Success Rate: {status['success_rate']}%")
        print()
        
        # Status breakdown
        print("📊 PROCESSING STATUS")
        print("-" * 20)
        for status_type, count in status['status_breakdown'].items():
            percentage = (count / max(status['total_items'], 1)) * 100
            print(f"{status_type:15} {count:6} ({percentage:5.1f}%)")
        print()
        
        # Performance
        if status['processing_times']['average']:
            print("⚡ PERFORMANCE")
            print("-" * 20)
            print(f"Average Time: {status['processing_times']['average']:.2f}s")
            print(f"Fastest Item: {status['processing_times']['minimum']:.2f}s")
            print(f"Slowest Item: {status['processing_times']['maximum']:.2f}s")
            print()
        
        # Recent activity
        print("📅 RECENT ACTIVITY")
        print("-" * 20)
        print(f"Last 24 hours: {status['recent_activity']['24h']} items")
        print(f"Last 7 days:   {status['recent_activity']['7d']} items")
        print(f"Last 30 days:  {status['recent_activity']['30d']} items")
        print()
        
        # Item types
        if status['item_types']:
            print("🎬 ITEM TYPES")
            print("-" * 20)
            for item_type, count in status['item_types'].items():
                print(f"{item_type:15} {count:6}")
            print()
        
        # Reviews
        if status['review_statistics']['items_with_reviews']:
            print("⭐ REVIEW STATISTICS")
            print("-" * 20)
            rs = status['review_statistics']
            print(f"Items with reviews: {rs['items_with_reviews']}")
            print(f"Total review entries: {rs['total_review_entries']}")
            if rs['average_score']:
                print(f"Average score: {rs['average_score']:.1f}")
            print()
        
        # Errors
        if status['error_analysis']['failed_items']:
            print("❌ ERROR ANALYSIS")
            print("-" * 20)
            ea = status['error_analysis']
            print(f"Failed items: {ea['failed_items']}")
            print(f"Unique error types: {ea['unique_error_types']}")
            
            if status['common_errors']:
                print("\nMost common errors:")
                for error in status['common_errors'][:3]:
                    error_text = error['error'][:50] + "..." if len(error['error']) > 50 else error['error']
                    print(f"  • {error_text} ({error['count']}x)")
            print()
        
        # Detailed items if requested
        if detailed and status.get('detailed_items'):
            print("📋 DETAILED ITEM LIST")
            print("-" * 60)
            for item in status['detailed_items'][:20]:  # Limit to first 20
                status_icon = "✅" if item['status'] == 'success' else "❌" if item['status'] == 'failed' else "⚠️"
                duration = f"{item['duration']:.1f}s" if item['duration'] else "N/A"
                print(f"{status_icon} {item['title'][:40]:40} | {item['type']:8} | {duration:6}")
            
            if len(status['detailed_items']) > 20:
                print(f"... and {len(status['detailed_items']) - 20} more items")
            print()
        
        print("="*60)
