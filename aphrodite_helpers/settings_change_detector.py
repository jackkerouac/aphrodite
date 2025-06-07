"""
Settings Change Detection for Aphrodite Database Tracking

Detects when badge settings change and marks items for reprocessing.
Integrates with existing settings system to provide intelligent reprocessing.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .database_manager import DatabaseManager


class SettingsChangeDetector:
    """
    Detects settings changes and manages reprocessing of affected items.
    
    Features:
    - Tracks current settings hash in database
    - Detects when badge settings change
    - Marks affected items for reprocessing
    - Provides reporting on settings changes
    """
    
    def __init__(self, db_path: str = "data/aphrodite.db"):
        self.db_manager = DatabaseManager(db_path)
        self.settings_component = "badge_settings"
    
    def get_current_badge_settings(self) -> Dict[str, Any]:
        """
        Extract current badge settings from the database.
        
        Returns:
            Dictionary of current badge settings
        """
        conn = self.db_manager.get_connection()
        
        try:
            # Get badge settings from database
            cursor = conn.execute("""
                SELECT setting_name, value 
                FROM badge_settings
            """)
            
            settings = {}
            for row in cursor.fetchall():
                setting_name = row[0]
                setting_value = row[1]
                
                # Parse JSON values
                try:
                    if setting_value and setting_value.strip().startswith(('{', '[')):
                        settings[setting_name] = json.loads(setting_value)
                    else:
                        settings[setting_name] = setting_value
                except json.JSONDecodeError:
                    settings[setting_name] = setting_value
            
            # Also include review settings
            cursor = conn.execute("""
                SELECT source_name, enabled, priority, max_variants
                FROM review_sources
            """)
            
            review_settings = {}
            for row in cursor.fetchall():
                review_settings[row[0]] = {
                    'enabled': bool(row[1]),
                    'priority': row[2],
                    'max_variants': row[3]
                }
            
            settings['review_settings'] = review_settings
            
            return settings
            
        except Exception as e:
            print(f"⚠️ Error getting badge settings: {e}")
            # Fallback to empty settings
            return {}
    
    def get_stored_settings_hash(self) -> Optional[str]:
        """
        Get the stored settings hash from the database.
        
        Returns:
            Stored settings hash or None if not found
        """
        conn = self.db_manager.get_connection()
        
        try:
            cursor = conn.execute("""
                SELECT value FROM settings 
                WHERE key = 'current_badge_settings_hash'
            """)
            row = cursor.fetchone()
            return row[0] if row else None
            
        except Exception:
            # Settings table might not have this key yet
            return None
    
    def store_settings_hash(self, settings_hash: str):
        """
        Store the current settings hash in the database.
        
        Args:
            settings_hash: Hash to store
        """
        conn = self.db_manager.get_connection()
        
        try:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, category)
                VALUES ('current_badge_settings_hash', ?, 'system')
            """, (settings_hash,))
            conn.commit()
            
        except Exception as e:
            print(f"⚠️ Error storing settings hash: {e}")
    
    def check_for_settings_changes(self) -> Dict[str, Any]:
        """
        Check if badge settings have changed since last processing.
        
        Returns:
            Dictionary with change detection results
        """
        # Get current settings
        current_settings = self.get_current_badge_settings()
        current_hash = self.db_manager.generate_settings_hash(current_settings)
        
        # Get stored hash
        stored_hash = self.get_stored_settings_hash()
        
        # Check for changes
        changed = stored_hash != current_hash
        
        result = {
            'settings_changed': changed,
            'current_hash': current_hash,
            'stored_hash': stored_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        if changed:
            result['change_detected_at'] = datetime.now().isoformat()
            print(f"🔄 Badge settings change detected!")
            print(f"   Previous hash: {stored_hash or 'None'}")
            print(f"   Current hash:  {current_hash}")
        
        return result
    
    def get_items_needing_reprocessing_due_to_settings(self, library_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get items that need reprocessing due to settings changes.
        
        Args:
            library_id: Optional library ID to filter by
            
        Returns:
            List of items needing reprocessing
        """
        current_settings = self.get_current_badge_settings()
        current_hash = self.db_manager.generate_settings_hash(current_settings)
        
        return self.db_manager.get_items_with_outdated_settings(current_hash, library_id)
    
    def mark_items_for_settings_reprocessing(self, library_id: Optional[str] = None, 
                                           dry_run: bool = False) -> Dict[str, Any]:
        """
        Mark items for reprocessing due to settings changes.
        
        Args:
            library_id: Optional library ID to filter by
            dry_run: If True, only return what would be marked without actually marking
            
        Returns:
            Dictionary with results of the operation
        """
        # Check for settings changes
        change_info = self.check_for_settings_changes()
        
        if not change_info['settings_changed']:
            return {
                'settings_changed': False,
                'items_marked': 0,
                'message': 'No settings changes detected'
            }
        
        # Get items needing reprocessing
        items_to_mark = self.get_items_needing_reprocessing_due_to_settings(library_id)
        
        result = {
            'settings_changed': True,
            'items_found': len(items_to_mark),
            'items_marked': 0,
            'dry_run': dry_run,
            'library_filter': library_id,
            'change_info': change_info
        }
        
        if not items_to_mark:
            result['message'] = 'No items need reprocessing'
            return result
        
        # Mark items (unless dry run)
        if not dry_run:
            item_ids = [item['jellyfin_item_id'] for item in items_to_mark]
            marked_count = self.db_manager.mark_items_for_reprocessing(
                item_ids, 
                f"Badge settings changed (hash: {change_info['current_hash'][:8]})"
            )
            result['items_marked'] = marked_count
            
            # Update stored hash
            self.store_settings_hash(change_info['current_hash'])
            
            result['message'] = f"Marked {marked_count} items for reprocessing due to settings changes"
        else:
            result['message'] = f"Would mark {len(items_to_mark)} items for reprocessing (dry run)"
        
        # Add sample of items
        result['sample_items'] = items_to_mark[:5]  # First 5 items as sample
        
        return result
    
    def auto_detect_and_mark_on_settings_change(self, library_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Automatically detect settings changes and mark items if auto-reprocess is enabled.
        
        Args:
            library_id: Optional library ID to filter by
            
        Returns:
            Results if changes were detected, None otherwise
        """
        # Check if auto-reprocess is enabled
        conn = self.db_manager.get_connection()
        
        try:
            cursor = conn.execute("""
                SELECT value FROM settings 
                WHERE key = 'auto_reprocess_on_settings_change'
            """)
            row = cursor.fetchone()
            auto_reprocess_enabled = row and row[0].lower() == 'true'
            
        except Exception:
            auto_reprocess_enabled = False
        
        # Check for changes
        change_info = self.check_for_settings_changes()
        
        if not change_info['settings_changed']:
            return None
        
        # If auto-reprocess is enabled, mark items
        if auto_reprocess_enabled:
            return self.mark_items_for_settings_reprocessing(library_id, dry_run=False)
        else:
            # Just return information about what would be marked
            items_to_mark = self.get_items_needing_reprocessing_due_to_settings(library_id)
            return {
                'settings_changed': True,
                'auto_reprocess_enabled': False,
                'items_found': len(items_to_mark),
                'message': 'Settings changed but auto-reprocess is disabled. Run with --mark-for-reprocess to update items.',
                'change_info': change_info
            }
    
    def get_settings_change_report(self, library_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report on settings changes and affected items.
        
        Args:
            library_id: Optional library ID to filter by
            
        Returns:
            Comprehensive settings change report
        """
        change_info = self.check_for_settings_changes()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'library_filter': library_id,
            'settings_status': change_info,
            'affected_items': {
                'count': 0,
                'by_type': {},
                'by_library': {},
                'sample': []
            },
            'recommendations': []
        }
        
        # Get affected items
        affected_items = self.get_items_needing_reprocessing_due_to_settings(library_id)
        report['affected_items']['count'] = len(affected_items)
        
        if affected_items:
            # Group by type
            by_type = {}
            by_library = {}
            
            for item in affected_items:
                item_type = item.get('item_type', 'Unknown')
                by_type[item_type] = by_type.get(item_type, 0) + 1
                
                # Note: we don't have library info in the returned items currently
                # This would need to be added to the query if needed
            
            report['affected_items']['by_type'] = by_type
            report['affected_items']['sample'] = affected_items[:10]  # First 10 items
        
        # Generate recommendations
        if change_info['settings_changed']:
            if affected_items:
                report['recommendations'].append(
                    f"Settings have changed and {len(affected_items)} items need reprocessing. "
                    "Run 'aphrodite.py settings-reprocess' to mark them for reprocessing."
                )
            else:
                report['recommendations'].append(
                    "Settings have changed but no existing items need reprocessing."
                )
        else:
            report['recommendations'].append("No settings changes detected. All items are up to date.")
        
        return report


def check_settings_changes_and_report(library_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Standalone function to check for settings changes and generate a report.
    
    Args:
        library_id: Optional library ID to filter by
        
    Returns:
        Settings change report
    """
    detector = SettingsChangeDetector()
    return detector.get_settings_change_report(library_id)


def auto_detect_settings_changes(library_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Standalone function for automatic settings change detection.
    
    Args:
        library_id: Optional library ID to filter by
        
    Returns:
        Results if changes detected, None otherwise
    """
    detector = SettingsChangeDetector()
    return detector.auto_detect_and_mark_on_settings_change(library_id)
