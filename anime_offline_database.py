#!/usr/bin/env python3
"""
Implementation of comprehensive anime mapping using anime-offline-database
"""

import requests
import json
import os
import time
from typing import Dict, Any, Optional


class AnimeOfflineDatabase:
    """
    Comprehensive anime mapping using the anime-offline-database
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.database_file = os.path.join(data_dir, "anime-offline-database-minified.json")
        self.database_url = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json"
        self.mappings = {}
        self.last_update = None
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def download_database(self, force_update: bool = False) -> bool:
        """
        Download the anime offline database
        
        Args:
            force_update: Force download even if file exists
            
        Returns:
            True if successful, False otherwise
        """
        # Check if we need to update
        if not force_update and os.path.exists(self.database_file):
            # Check file age (update weekly)
            file_age = time.time() - os.path.getmtime(self.database_file)
            if file_age < (7 * 24 * 60 * 60):  # 7 days
                print(f"📚 Database file is recent, skipping download")
                return True
        
        print(f"📥 Downloading anime offline database (~50MB)...")
        
        try:
            response = requests.get(self.database_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.database_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Progress: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✅ Database downloaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download database: {e}")
            return False
    
    def load_database(self) -> bool:
        """
        Load the anime database into memory for mapping
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.database_file):
            print(f"📥 Database file not found, downloading...")
            if not self.download_database():
                return False
        
        try:
            print(f"📚 Loading anime database...")
            
            with open(self.database_file, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Extract mapping data
            anime_data = database.get('data', [])
            print(f"📊 Processing {len(anime_data)} anime entries...")
            
            # Build mapping indices
            self.mappings = {
                'anilist_to_mal': {},
                'anidb_to_mal': {},
                'kitsu_to_mal': {},
                'mal_to_anilist': {},
                'title_to_mal': {}
            }
            
            for anime in anime_data:
                sources = anime.get('sources', [])
                title = anime.get('title', '')
                
                # Extract IDs from source URLs
                ids = self._extract_ids_from_sources(sources)
                
                mal_id = ids.get('myanimelist')
                anilist_id = ids.get('anilist')
                anidb_id = ids.get('anidb')
                kitsu_id = ids.get('kitsu')
                
                # Build mapping indices
                if mal_id:
                    if anilist_id:
                        self.mappings['anilist_to_mal'][str(anilist_id)] = mal_id
                        self.mappings['mal_to_anilist'][str(mal_id)] = anilist_id
                    
                    if anidb_id:
                        self.mappings['anidb_to_mal'][str(anidb_id)] = mal_id
                    
                    if kitsu_id:
                        self.mappings['kitsu_to_mal'][str(kitsu_id)] = mal_id
                    
                    if title:
                        # Store title mapping (lowercase for fuzzy matching)
                        title_key = title.lower().strip()
                        self.mappings['title_to_mal'][title_key] = {
                            'mal_id': mal_id,
                            'title': title
                        }
            
            print(f"✅ Database loaded with {len(self.mappings['anilist_to_mal'])} AniList→MAL mappings")
            self.last_update = time.time()
            return True
            
        except Exception as e:
            print(f"❌ Failed to load database: {e}")
            return False
    
    def _extract_ids_from_sources(self, sources: list) -> Dict[str, int]:
        """Extract provider IDs from source URLs"""
        ids = {}
        
        for source in sources:
            if 'myanimelist.net/anime/' in source:
                try:
                    ids['myanimelist'] = int(source.split('/anime/')[1].split('/')[0])
                except (ValueError, IndexError):
                    pass
            
            elif 'anilist.co/anime/' in source:
                try:
                    ids['anilist'] = int(source.split('/anime/')[1].split('/')[0])
                except (ValueError, IndexError):
                    pass
            
            elif 'anidb.net/anime/' in source:
                try:
                    ids['anidb'] = int(source.split('/anime/')[1])
                except (ValueError, IndexError):
                    pass
            
            elif 'kitsu.app/anime/' in source:
                try:
                    ids['kitsu'] = int(source.split('/anime/')[1])
                except (ValueError, IndexError):
                    pass
        
        return ids
    
    def get_mal_id_from_anilist(self, anilist_id: int) -> Optional[int]:
        """Get MAL ID from AniList ID"""
        if not self.mappings:
            if not self.load_database():
                return None
        
        return self.mappings['anilist_to_mal'].get(str(anilist_id))
    
    def get_mal_id_from_anidb(self, anidb_id: int) -> Optional[int]:
        """Get MAL ID from AniDB ID"""
        if not self.mappings:
            if not self.load_database():
                return None
        
        return self.mappings['anidb_to_mal'].get(str(anidb_id))
    
    def get_mapping_info(self) -> Dict[str, Any]:
        """Get information about the loaded mappings"""
        if not self.mappings:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "last_update": self.last_update,
            "anilist_mappings": len(self.mappings['anilist_to_mal']),
            "anidb_mappings": len(self.mappings['anidb_to_mal']),
            "kitsu_mappings": len(self.mappings['kitsu_to_mal']),
            "title_mappings": len(self.mappings['title_to_mal'])
        }


def test_comprehensive_mapping():
    """Test the comprehensive mapping system"""
    print("🧪 Testing Comprehensive Anime Mapping")
    print("=" * 60)
    
    # Initialize the database
    db = AnimeOfflineDatabase()
    
    # Load/download the database
    if not db.load_database():
        print("❌ Failed to load database")
        return False
    
    # Show mapping statistics
    info = db.get_mapping_info()
    print(f"📊 Mapping Statistics:")
    print(f"   AniList→MAL mappings: {info['anilist_mappings']:,}")
    print(f"   AniDB→MAL mappings: {info['anidb_mappings']:,}")
    print(f"   Kitsu→MAL mappings: {info['kitsu_mappings']:,}")
    print(f"   Title mappings: {info['title_mappings']:,}")
    
    # Test with our specific anime
    test_cases = [
        ("AniList ID 126579", 126579, "get_mal_id_from_anilist"),
        ("AniDB ID 17944", 17944, "get_mal_id_from_anidb"),
    ]
    
    print(f"\n🧪 Testing specific mappings:")
    for description, test_id, method_name in test_cases:
        print(f"\n   Testing {description}:")
        method = getattr(db, method_name)
        result = method(test_id)
        
        if result:
            print(f"   ✅ Found MAL ID: {result}")
            
            # Verify this is our target anime
            if result == 54852:
                print(f"   🎉 Correct! This is 'A Returner's Magic Should Be Special'")
        else:
            print(f"   ❌ No mapping found")
    
    return True


if __name__ == "__main__":
    test_comprehensive_mapping()
