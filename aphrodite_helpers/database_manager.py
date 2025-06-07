"""
Database Manager for Aphrodite Item Tracking

Handles automatic schema management, table creation, and database operations
for tracking processed media items and their metadata.
"""

import sqlite3
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import os


class DatabaseManager:
    """
    Manages database operations for item tracking in Aphrodite.
    
    Key Features:
    - Automatic schema creation and management
    - Zero-configuration setup (tables created automatically)
    - Schema version tracking for future migrations
    - Backward compatibility with existing installations
    """
    
    def __init__(self, db_path: str = "data/aphrodite.db"):
        self.db_path = db_path
        self.connection = None
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # CRITICAL: Automatically initialize schema on first connection
        self.ensure_schema_exists()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def ensure_schema_exists(self):
        """
        AUTOMATIC SCHEMA MANAGEMENT
        Called on every DatabaseManager initialization.
        Creates tables if they don't exist, adds missing columns if schema evolved.
        This ensures seamless upgrades when users download new versions.
        """
        conn = self.get_connection()
        
        try:
            # 1. Check if schema_versions table exists, create if missing
            if not self.table_exists('schema_versions'):
                self.create_schema_versions_table()
            
            # 2. Check current schema version
            current_version = self.get_schema_version('item_tracking')
            required_version = 1  # Will increment as we add features
            
            # 3. Apply any missing schema changes
            if current_version < required_version:
                self.upgrade_schema(current_version, required_version)
            
            # 4. Create tables if they don't exist
            self.create_tables_if_not_exist()
            
            # 5. Add any missing columns (for future upgrades)
            self.add_missing_columns()
            
            conn.commit()
            
        except Exception as e:
            print(f"⚠️ Error during schema initialization: {e}")
            conn.rollback()
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        conn = self.get_connection()
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    def create_schema_versions_table(self):
        """Create the schema_versions table for tracking database schema."""
        conn = self.get_connection()
        conn.execute("""
            CREATE TABLE schema_versions (
                component TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert initial version
        conn.execute(
            "INSERT OR REPLACE INTO schema_versions (component, version) VALUES (?, ?)",
            ('item_tracking', 0)
        )
    
    def get_schema_version(self, component: str) -> int:
        """Get the current schema version for a component."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT version FROM schema_versions WHERE component = ?",
            (component,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def set_schema_version(self, component: str, version: int):
        """Set the schema version for a component."""
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO schema_versions (component, version) VALUES (?, ?)",
            (component, version)
        )
    
    def upgrade_schema(self, current_version: int, target_version: int):
        """Apply schema upgrades from current to target version."""
        print(f"📈 Upgrading item tracking schema from v{current_version} to v{target_version}")
        
        # For now, just update the version number
        # Future upgrades will be added here
        self.set_schema_version('item_tracking', target_version)
    
    def create_tables_if_not_exist(self):
        """Create all required tables if they don't exist."""
        conn = self.get_connection()
        
        # Create processed_items table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Jellyfin Identifiers
                jellyfin_item_id TEXT NOT NULL UNIQUE,
                jellyfin_library_id TEXT NOT NULL,
                jellyfin_user_id TEXT NOT NULL,
                
                -- Media Information
                item_type TEXT NOT NULL, -- 'Movie', 'Series', 'Season', 'Episode'
                title TEXT NOT NULL,
                year INTEGER,
                parent_item_id TEXT, -- For episodes/seasons linking to series
                
                -- External IDs (JSON format for flexibility)
                external_ids TEXT, -- JSON: {"tmdb": "12345", "tvdb": "67890", "imdb": "tt1234567"}
                
                -- File Information
                file_path TEXT,
                file_size INTEGER,
                file_modified_date TIMESTAMP,
                
                -- Processing Information
                first_processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processing_count INTEGER NOT NULL DEFAULT 1,
                last_processing_status TEXT NOT NULL, -- 'success', 'partial_success', 'failed'
                last_processing_version TEXT, -- Aphrodite version used
                last_processing_duration REAL, -- Seconds
                
                -- Processing Options (what was requested)
                badges_requested TEXT, -- JSON: {"audio": true, "resolution": true, "reviews": true}
                badges_applied TEXT, -- JSON: {"audio": "DTS-HD MA", "resolution": "4K"}
                
                -- Settings Hash (to detect when reprocessing needed)
                settings_hash TEXT,
                
                -- Poster Information
                poster_original_url TEXT,
                poster_modified_path TEXT,
                
                -- Metadata Cache
                metadata_sources_used TEXT, -- JSON: ["tmdb", "tvdb", "jellyfin"]
                metadata_last_updated TIMESTAMP,
                
                -- Review Cache Information
                reviews_last_checked TIMESTAMP,
                reviews_cache_expiry TIMESTAMP,
                highest_review_score REAL,
                lowest_review_score REAL,
                
                -- Error Tracking
                last_error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                
                -- Timestamps
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create item_reviews table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS item_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processed_item_id INTEGER NOT NULL,
                
                -- Review Source Information
                source TEXT NOT NULL, -- 'imdb', 'rottentomatoes', 'metacritic', 'mal'
                source_id TEXT, -- Source-specific ID
                
                -- Review Data
                score REAL,
                score_max REAL, -- Max possible score for this source
                score_text TEXT, -- Display text (e.g., "8.5/10", "85%")
                review_count INTEGER,
                
                -- Metadata
                retrieved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                cache_expires_at TIMESTAMP,
                
                -- Raw Data (for debugging)
                raw_data TEXT, -- JSON of complete API response
                
                FOREIGN KEY (processed_item_id) REFERENCES processed_items(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        self.create_indexes_if_not_exist()
    
    def create_indexes_if_not_exist(self):
        """Create database indexes for optimal performance."""
        conn = self.get_connection()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_processed_items_jellyfin_id ON processed_items(jellyfin_item_id)",
            "CREATE INDEX IF NOT EXISTS idx_processed_items_library ON processed_items(jellyfin_library_id)",
            "CREATE INDEX IF NOT EXISTS idx_processed_items_status ON processed_items(last_processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_processed_items_last_processed ON processed_items(last_processed_at)",
            "CREATE INDEX IF NOT EXISTS idx_processed_items_parent ON processed_items(parent_item_id)",
            "CREATE INDEX IF NOT EXISTS idx_item_reviews_processed_item ON item_reviews(processed_item_id)",
            "CREATE INDEX IF NOT EXISTS idx_item_reviews_source ON item_reviews(source)",
            "CREATE INDEX IF NOT EXISTS idx_item_reviews_score ON item_reviews(score)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except sqlite3.Error as e:
                # Index might already exist, that's fine
                pass
    
    def add_missing_columns(self):
        """Add any missing columns for future schema upgrades."""
        # This method will be used for future schema migrations
        # For now, it's a placeholder for when we need to add new columns
        pass
    
    # ================================
    # CORE DATABASE OPERATIONS
    # ================================
    
    def insert_processed_item(self, item_data: Dict[str, Any]) -> int:
        """
        Insert a new processed item record.
        
        Args:
            item_data: Dictionary containing item information
            
        Returns:
            The ID of the inserted record
        """
        conn = self.get_connection()
        
        # Prepare data with defaults
        now = datetime.now().isoformat()
        
        data = {
            'jellyfin_item_id': item_data['jellyfin_item_id'],
            'jellyfin_library_id': item_data['jellyfin_library_id'],
            'jellyfin_user_id': item_data['jellyfin_user_id'],
            'item_type': item_data.get('item_type', 'Unknown'),
            'title': item_data.get('title', 'Unknown'),
            'year': item_data.get('year'),
            'parent_item_id': item_data.get('parent_item_id'),
            'external_ids': json.dumps(item_data.get('external_ids', {})),
            'file_path': item_data.get('file_path'),
            'file_size': item_data.get('file_size'),
            'file_modified_date': item_data.get('file_modified_date'),
            'last_processing_status': item_data.get('last_processing_status', 'processing'),
            'last_processing_version': item_data.get('last_processing_version'),
            'last_processing_duration': item_data.get('last_processing_duration'),
            'badges_requested': json.dumps(item_data.get('badges_requested', {})),
            'badges_applied': json.dumps(item_data.get('badges_applied', {})),
            'settings_hash': item_data.get('settings_hash'),
            'poster_original_url': item_data.get('poster_original_url'),
            'poster_modified_path': item_data.get('poster_modified_path'),
            'metadata_sources_used': json.dumps(item_data.get('metadata_sources_used', [])),
            'metadata_last_updated': item_data.get('metadata_last_updated'),
            'reviews_last_checked': item_data.get('reviews_last_checked'),
            'reviews_cache_expiry': item_data.get('reviews_cache_expiry'),
            'highest_review_score': item_data.get('highest_review_score'),
            'lowest_review_score': item_data.get('lowest_review_score'),
            'last_error_message': item_data.get('last_error_message'),
            'retry_count': item_data.get('retry_count', 0),
            'updated_at': now
        }
        
        # Create SQL and parameters
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        sql = f"""
            INSERT INTO processed_items ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor = conn.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    
    def update_processed_item(self, jellyfin_item_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing processed item record.
        
        Args:
            jellyfin_item_id: The Jellyfin item ID to update
            updates: Dictionary of fields to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        conn = self.get_connection()
        
        # Add updated timestamp
        updates['updated_at'] = datetime.now().isoformat()
        
        # Handle JSON fields
        json_fields = ['external_ids', 'badges_requested', 'badges_applied', 'metadata_sources_used']
        for field in json_fields:
            if field in updates and not isinstance(updates[field], str):
                updates[field] = json.dumps(updates[field])
        
        # If this is an existing item being reprocessed, increment processing count
        if 'last_processing_status' in updates:
            conn.execute(
                "UPDATE processed_items SET processing_count = processing_count + 1 WHERE jellyfin_item_id = ?",
                (jellyfin_item_id,)
            )
        
        # Build UPDATE query
        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(jellyfin_item_id)  # For WHERE clause
        
        sql = f"""
            UPDATE processed_items 
            SET {', '.join(set_clauses)}
            WHERE jellyfin_item_id = ?
        """
        
        cursor = conn.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0
    
    def get_processed_item(self, jellyfin_item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a processed item by Jellyfin ID.
        
        Args:
            jellyfin_item_id: The Jellyfin item ID to retrieve
            
        Returns:
            Dictionary containing item data, or None if not found
        """
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM processed_items WHERE jellyfin_item_id = ?",
            (jellyfin_item_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert to dictionary and parse JSON fields
        data = dict(row)
        json_fields = ['external_ids', 'badges_requested', 'badges_applied', 'metadata_sources_used']
        for field in json_fields:
            if data.get(field):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    data[field] = {}
        
        return data
    
    def item_exists(self, jellyfin_item_id: str) -> bool:
        """Check if an item has been processed before."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT 1 FROM processed_items WHERE jellyfin_item_id = ?",
            (jellyfin_item_id,)
        )
        return cursor.fetchone() is not None
    
    def get_items_needing_review_update(self, hours_threshold: int = 24) -> List[Dict[str, Any]]:
        """
        Find items whose reviews might need updating.
        
        Args:
            hours_threshold: Number of hours since last review check
            
        Returns:
            List of items that need review updates
        """
        conn = self.get_connection()
        
        # Calculate threshold timestamp
        threshold_time = datetime.now().timestamp() - (hours_threshold * 3600)
        threshold_iso = datetime.fromtimestamp(threshold_time).isoformat()
        
        cursor = conn.execute("""
            SELECT * FROM processed_items 
            WHERE reviews_last_checked IS NULL 
               OR reviews_last_checked < ?
               OR reviews_cache_expiry < ?
            ORDER BY last_processed_at DESC
        """, (threshold_iso, datetime.now().isoformat()))
        
        items = []
        for row in cursor.fetchall():
            data = dict(row)
            # Parse JSON fields
            json_fields = ['external_ids', 'badges_requested', 'badges_applied', 'metadata_sources_used']
            for field in json_fields:
                if data.get(field):
                    try:
                        data[field] = json.loads(data[field])
                    except json.JSONDecodeError:
                        data[field] = {}
            items.append(data)
        
        return items
    
    def insert_item_reviews(self, processed_item_id: int, reviews_data: List[Dict[str, Any]]) -> bool:
        """
        Insert review data for an item.
        
        Args:
            processed_item_id: ID of the processed item
            reviews_data: List of review dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection()
        
        try:
            # First, delete existing reviews for this item
            conn.execute(
                "DELETE FROM item_reviews WHERE processed_item_id = ?",
                (processed_item_id,)
            )
            
            # Insert new reviews
            for review in reviews_data:
                data = {
                    'processed_item_id': processed_item_id,
                    'source': review['source'],
                    'source_id': review.get('source_id'),
                    'score': review.get('score'),
                    'score_max': review.get('score_max'),
                    'score_text': review.get('score_text'),
                    'review_count': review.get('review_count'),
                    'cache_expires_at': review.get('cache_expires_at'),
                    'raw_data': json.dumps(review.get('raw_data', {}))
                }
                
                columns = list(data.keys())
                placeholders = ['?' for _ in columns]
                values = list(data.values())
                
                sql = f"""
                    INSERT INTO item_reviews ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                """
                
                conn.execute(sql, values)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting reviews: {e}")
            conn.rollback()
            return False
    
    def get_item_reviews(self, processed_item_id: int) -> List[Dict[str, Any]]:
        """
        Get all reviews for an item.
        
        Args:
            processed_item_id: ID of the processed item
            
        Returns:
            List of review dictionaries
        """
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM item_reviews WHERE processed_item_id = ? ORDER BY score DESC",
            (processed_item_id,)
        )
        
        reviews = []
        for row in cursor.fetchall():
            data = dict(row)
            # Parse raw_data JSON
            if data.get('raw_data'):
                try:
                    data['raw_data'] = json.loads(data['raw_data'])
                except json.JSONDecodeError:
                    data['raw_data'] = {}
            reviews.append(data)
        
        return reviews
    
    def get_processing_statistics(self, library_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get processing statistics for reporting.
        
        Args:
            library_id: Optional library ID to filter by
            
        Returns:
            Dictionary containing processing statistics
        """
        conn = self.get_connection()
        
        # Base query
        where_clause = ""
        params = []
        if library_id:
            where_clause = "WHERE jellyfin_library_id = ?"
            params.append(library_id)
        
        # Total counts by status
        cursor = conn.execute(f"""
            SELECT 
                last_processing_status,
                COUNT(*) as count
            FROM processed_items 
            {where_clause}
            GROUP BY last_processing_status
        """, params)
        
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total items
        cursor = conn.execute(f"SELECT COUNT(*) FROM processed_items {where_clause}", params)
        total_items = cursor.fetchone()[0]
        
        # Average processing time
        cursor = conn.execute(f"""
            SELECT AVG(last_processing_duration) 
            FROM processed_items 
            {where_clause}
            AND last_processing_duration IS NOT NULL
        """, params)
        avg_processing_time = cursor.fetchone()[0]
        
        # Items processed in last 24 hours
        day_ago = (datetime.now().timestamp() - 86400)
        day_ago_iso = datetime.fromtimestamp(day_ago).isoformat()
        
        cursor = conn.execute(f"""
            SELECT COUNT(*) FROM processed_items 
            {where_clause} 
            {"AND" if where_clause else "WHERE"} last_processed_at > ?
        """, params + [day_ago_iso])
        recent_items = cursor.fetchone()[0]
        
        return {
            'total_items': total_items,
            'status_counts': status_counts,
            'success_rate': status_counts.get('success', 0) / max(total_items, 1) * 100,
            'average_processing_time': avg_processing_time,
            'items_processed_24h': recent_items,
            'library_id': library_id
        }
    
    def generate_settings_hash(self, settings_data: Dict[str, Any]) -> str:
        """
        Generate a hash of relevant settings for change detection.
        
        Args:
            settings_data: Dictionary of settings to hash
            
        Returns:
            SHA256 hash of the settings
        """
        # Sort keys for consistent hashing
        settings_str = json.dumps(settings_data, sort_keys=True)
        return hashlib.sha256(settings_str.encode()).hexdigest()[:16]  # First 16 chars
