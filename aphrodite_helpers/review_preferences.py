#!/usr/bin/env python3
# aphrodite_helpers/review_preferences.py

import os
import sys
import sqlite3
import json
from typing import List, Dict, Any, Optional

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

class ReviewPreferences:
    """Service for managing user review source preferences from the database"""
    
    def __init__(self, db_path=None):
        """Initialize with database path"""
        if db_path is None:
            # Determine default path
            is_docker = os.path.exists('/.dockerenv')
            if is_docker:
                self.db_path = '/app/data/aphrodite.db'
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
        else:
            self.db_path = db_path
    
    def _get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        """Get all enabled review sources ordered by display priority"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_name, enabled, display_order, max_variants, priority, conditions
            FROM review_sources 
            WHERE enabled = 1 
            ORDER BY display_order ASC, priority ASC
        """)
        
        sources = []
        for row in cursor.fetchall():
            source_data = {
                'name': row['source_name'],
                'enabled': bool(row['enabled']),
                'display_order': row['display_order'],
                'max_variants': row['max_variants'],
                'priority': row['priority'],
                'conditions': json.loads(row['conditions']) if row['conditions'] else None
            }
            sources.append(source_data)
        
        conn.close()
        return sources
    
    def get_review_settings(self) -> Dict[str, Any]:
        """Get general review settings"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_key, setting_value FROM review_settings")
        
        settings = {}
        for row in cursor.fetchall():
            key = row['setting_key']
            value = row['setting_value']
            
            # Convert known boolean settings
            if key in ['show_percentage_only', 'group_related_sources', 'anime_sources_for_anime_only']:
                settings[key] = value == '1' or value.lower() == 'true'
            # Convert known integer settings
            elif key in ['max_badges_display']:
                settings[key] = int(value) if value.isdigit() else 4
            else:
                settings[key] = value
        
        conn.close()
        return settings
    
    def should_include_source(self, source_name: str, item_data: Dict[str, Any] = None) -> bool:
        """Check if a source should be included based on conditions and item data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT enabled, conditions 
            FROM review_sources 
            WHERE source_name = ?
        """, (source_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row['enabled']:
            return False
        
        # Check conditions if they exist
        if row['conditions']:
            try:
                conditions = json.loads(row['conditions'])
                return self._evaluate_conditions(conditions, item_data)
            except (json.JSONDecodeError, TypeError):
                # If conditions can't be parsed, default to including the source
                return True
        
        return True
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], item_data: Dict[str, Any] = None) -> bool:
        """Evaluate conditions against item data"""
        if not conditions or not item_data:
            return True
        
        # Check content type condition
        if 'content_type' in conditions:
            required_type = conditions['content_type'].lower()
            
            # Determine if this is anime content
            if required_type == 'anime':
                return self._is_anime_content(item_data)
            # Add other content type checks here as needed
        
        return True
    
    def _is_anime_content(self, item_data: Dict[str, Any]) -> bool:
        """Check if the item is anime content"""
        if not item_data:
            return False
        
        # Check for explicit anime genres
        genres = item_data.get('Genres', [])
        anime_genres = ['anime', 'animation']
        
        for genre in genres:
            if genre.lower() in anime_genres:
                return True
        
        # Check for provider IDs that indicate anime
        provider_ids = item_data.get('ProviderIds', {})
        anime_providers = ['AniDb', 'AniList', 'MyAnimeList']
        
        for provider in anime_providers:
            if provider in provider_ids:
                return True
        
        # Check production locations for Japan (common for anime)
        production_locations = item_data.get('ProductionLocations', [])
        if 'Japan' in production_locations:
            # Additional check - if it's also animation, likely anime
            if any(genre.lower() == 'animation' for genre in genres):
                return True
        
        return False
    
    def get_max_badges_to_display(self) -> int:
        """Get the maximum number of badges to display"""
        settings = self.get_review_settings()
        return settings.get('max_badges_display', 4)
    
    def filter_and_order_reviews(self, reviews: List[Dict[str, Any]], item_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Filter and order reviews based on user preferences"""
        # Get enabled sources and settings
        enabled_sources = self.get_enabled_sources()
        max_badges = self.get_max_badges_to_display()
        
        print(f"🔍 Enabled sources: {[s['name'] for s in enabled_sources]}")
        print(f"🔍 Max badges to display: {max_badges}")
        
        # Create a mapping of source names to their settings
        source_settings = {source['name']: source for source in enabled_sources}
        
        # Map review source names to database source names
        source_name_mapping = {
            'Rotten Tomatoes': 'Rotten Tomatoes Critics',
            'IMDb Top 250': 'IMDb',
            'IMDb Top 1000': 'IMDb',
            # Direct mappings (no change needed)
            'IMDb': 'IMDb',
            'Metacritic': 'Metacritic',
            'TMDb': 'TMDb',
            'AniDB': 'AniDB',
            'MyAnimeList': 'MyAnimeList'
        }
        
        # Filter reviews to only include enabled sources
        filtered_reviews = []
        source_variant_counts = {}  # Track how many variants we've added for each source
        
        for review in reviews:
            source_name = review.get('source')
            if not source_name:
                continue
            
            # Map the source name to the database source name
            db_source_name = source_name_mapping.get(source_name, source_name)
            
            # Check if this source is enabled and should be included
            if db_source_name not in source_settings:
                print(f"🔍 Skipping {source_name} (mapped to {db_source_name}) - not in enabled sources")
                continue
            
            source_config = source_settings[db_source_name]
            
            # Check conditions using database source name
            if not self.should_include_source(db_source_name, item_data):
                print(f"🔍 Skipping {source_name} - conditions not met")
                continue
            
            # Check max variants for this database source (group variants together)
            current_count = source_variant_counts.get(db_source_name, 0)
            max_variants = source_config.get('max_variants', 1)
            
            if current_count >= max_variants:
                print(f"🔍 Skipping {source_name} - max variants ({max_variants}) reached for {db_source_name}")
                continue
            
            # Add the review with priority information
            review_with_priority = review.copy()
            review_with_priority['_priority'] = source_config['priority']
            review_with_priority['_display_order'] = source_config['display_order']
            
            filtered_reviews.append(review_with_priority)
            source_variant_counts[db_source_name] = current_count + 1
            
            print(f"✅ Including {source_name} (variant {current_count + 1}/{max_variants} for {db_source_name})")
        
        # Sort by display order, then by priority
        filtered_reviews.sort(key=lambda x: (x.get('_display_order', 999), x.get('_priority', 999)))
        
        # Remove internal fields
        for review in filtered_reviews:
            review.pop('_priority', None)
            review.pop('_display_order', None)
        
        # Limit to max badges
        if max_badges > 0:
            filtered_reviews = filtered_reviews[:max_badges]
        
        print(f"✅ Final filtered reviews ({len(filtered_reviews)}): {[r.get('source') for r in filtered_reviews]}")
        
        return filtered_reviews

# Convenience function for easy import
def get_user_preferences(db_path=None):
    """Get a ReviewPreferences instance"""
    return ReviewPreferences(db_path)

def filter_reviews_by_preferences(reviews: List[Dict[str, Any]], item_data: Dict[str, Any] = None, db_path=None) -> List[Dict[str, Any]]:
    """Convenience function to filter reviews by user preferences"""
    try:
        preferences = ReviewPreferences(db_path)
        return preferences.filter_and_order_reviews(reviews, item_data)
    except Exception as e:
        print(f"⚠️ Error filtering reviews by preferences: {e}")
        print(f"⚠️ Returning unfiltered reviews")
        return reviews
