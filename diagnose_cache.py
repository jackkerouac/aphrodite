#!/usr/bin/env python3
"""
Cache Diagnostic Script

This script examines the cache directory to help debug poster restoration issues.
"""

import sys
import json
from pathlib import Path

# Add the API directory to the Python path
api_dir = Path(__file__).parent / "api"
sys.path.insert(0, str(api_dir))

from app.services.poster_management import StorageManager


def analyze_cache_directory():
    """Analyze the cache directory contents"""
    
    print("🔍 CACHE DIRECTORY ANALYSIS")
    print("=" * 50)
    
    storage_manager = StorageManager()
    cache_path = storage_manager.cache_path
    
    print(f"Cache directory: {cache_path}")
    
    if not cache_path.exists():
        print("❌ Cache directory does not exist!")
        return
    
    # Get all files in cache directory
    all_files = list(cache_path.iterdir())
    jpg_files = [f for f in all_files if f.suffix.lower() == '.jpg']
    meta_files = [f for f in all_files if f.suffix.lower() == '.meta']
    
    print(f"\nTotal files: {len(all_files)}")
    print(f"JPG files: {len(jpg_files)}")
    print(f"META files: {len(meta_files)}")
    
    # Analyze JPG files
    print(f"\n📸 CACHED POSTER FILES:")
    print("-" * 30)
    
    jellyfin_ids = {}
    
    for jpg_file in sorted(jpg_files):
        filename = jpg_file.name
        file_size = jpg_file.stat().st_size
        
        print(f"\n📄 {filename}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Parse filename to extract jellyfin_id
        if filename.startswith("jellyfin_") and filename.endswith(".jpg"):
            parts = filename[9:-4].split("_")  # Remove "jellyfin_" prefix and ".jpg" suffix
            if len(parts) >= 2:
                jellyfin_id = "_".join(parts[:-1])  # Everything except the last part (UUID)
                unique_id = parts[-1]
                
                print(f"   Jellyfin ID: {jellyfin_id}")
                print(f"   Unique ID: {unique_id}")
                
                # Track jellyfin_ids
                if jellyfin_id not in jellyfin_ids:
                    jellyfin_ids[jellyfin_id] = []
                jellyfin_ids[jellyfin_id].append({
                    'filename': filename,
                    'unique_id': unique_id,
                    'size': file_size,
                    'path': jpg_file
                })
                
                # Check for corresponding metadata file
                meta_file = jpg_file.with_suffix('.meta')
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r') as f:
                            metadata = json.load(f)
                        
                        print(f"   ✅ Metadata: {metadata.get('jellyfin_id')} (cached at {metadata.get('cached_at')})")
                        
                        # Validate metadata matches filename
                        if metadata.get('jellyfin_id') != jellyfin_id:
                            print(f"   ⚠️  METADATA MISMATCH! File: {jellyfin_id}, Meta: {metadata.get('jellyfin_id')}")
                        
                    except Exception as e:
                        print(f"   ❌ Metadata error: {e}")
                else:
                    print(f"   ⚠️  No metadata file")
        else:
            print(f"   ⚠️  Unexpected filename format")
    
    # Summary by jellyfin_id
    print(f"\n📊 SUMMARY BY JELLYFIN ID:")
    print("-" * 30)
    
    for jellyfin_id, files in jellyfin_ids.items():
        print(f"\n🎬 {jellyfin_id}:")
        print(f"   Cached versions: {len(files)}")
        
        for i, file_info in enumerate(files):
            print(f"   [{i+1}] {file_info['filename']} ({file_info['size']:,} bytes)")
    
    # Check for duplicates (same content, different files)
    print(f"\n🔄 CHECKING FOR DUPLICATES:")
    print("-" * 30)
    
    size_groups = {}
    for jellyfin_id, files in jellyfin_ids.items():
        for file_info in files:
            size = file_info['size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append((jellyfin_id, file_info))
    
    duplicates_found = False
    for size, file_list in size_groups.items():
        if len(file_list) > 1:
            duplicates_found = True
            print(f"\n⚠️  Files with same size ({size:,} bytes):")
            for jellyfin_id, file_info in file_list:
                print(f"   - {jellyfin_id}: {file_info['filename']}")
    
    if not duplicates_found:
        print("✅ No duplicate file sizes found")
    
    return jellyfin_ids


def test_cache_retrieval(jellyfin_ids):
    """Test cache retrieval for each jellyfin_id"""
    
    print(f"\n🧪 TESTING CACHE RETRIEVAL:")
    print("-" * 30)
    
    storage_manager = StorageManager()
    
    for jellyfin_id in jellyfin_ids.keys():
        print(f"\n🔍 Testing retrieval for: {jellyfin_id}")
        
        try:
            cached_path = storage_manager.get_cached_original(jellyfin_id)
            
            if cached_path:
                cached_file = Path(cached_path)
                if cached_file.exists():
                    file_size = cached_file.stat().st_size
                    print(f"   ✅ Retrieved: {cached_file.name} ({file_size:,} bytes)")
                else:
                    print(f"   ❌ File not found: {cached_path}")
            else:
                print(f"   ❌ No cached original found")
                
        except Exception as e:
            print(f"   💥 Error: {e}")


def main():
    """Main diagnostic function"""
    
    print("🩺 POSTER CACHE DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Analyze cache directory
    jellyfin_ids = analyze_cache_directory()
    
    if jellyfin_ids:
        # Test cache retrieval
        test_cache_retrieval(jellyfin_ids)
    
    print(f"\n" + "=" * 60)
    print("🏁 DIAGNOSTIC COMPLETE")
    print("\nIf you see the same file being returned for different Jellyfin IDs,")
    print("that explains why the wrong poster is being restored.")


if __name__ == "__main__":
    main()
