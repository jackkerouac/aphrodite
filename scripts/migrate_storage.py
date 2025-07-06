
import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define old and new base paths
OLD_BASE_DIR = Path('.')
NEW_BASE_DIR = Path('/app')

# Define migration mappings
MIGRATION_MAP = {
    'logs': {
        'source': OLD_BASE_DIR / 'logs',
        'destination': NEW_BASE_DIR / 'logs/api'
    },
    'api_logs': {
        'source': OLD_BASE_DIR / 'api/logs',
        'destination': NEW_BASE_DIR / 'logs/api'
    },
    'api_data_logs': {
        'source': OLD_BASE_DIR / 'api/data/logs',
        'destination': NEW_BASE_DIR / 'logs/database'
    },
    'api_debug_logs': {
        'source': OLD_BASE_DIR / 'api/debug_logs',
        'destination': NEW_BASE_DIR / 'logs/debug'
    },
    'cache_posters': {
        'source': OLD_BASE_DIR / 'cache/posters',
        'destination': NEW_BASE_DIR / 'data/cache/posters'
    },
    'api_cache_posters': {
        'source': OLD_BASE_DIR / 'api/cache/posters',
        'destination': NEW_BASE_DIR / 'data/cache/posters'
    },
    'api_cache_placeholders': {
        'source': OLD_BASE_DIR / 'api/cache/placeholders',
        'destination': NEW_BASE_DIR / 'data/cache/thumbnails'
    },
    'audio_cache': {
        'source': OLD_BASE_DIR / 'cache/audio_cache.json',
        'destination': NEW_BASE_DIR / 'data/cache/audio/audio_cache.json'
    },
    'resolution_cache': {
        'source': OLD_BASE_DIR / 'cache/resolution_cache.json',
        'destination': NEW_BASE_DIR / 'data/cache/resolution/resolution_cache.json'
    },
    'api_static_originals': {
        'source': OLD_BASE_DIR / 'api/static/originals',
        'destination': NEW_BASE_DIR / 'api/static/originals/posters'
    },
    'api_static_preview': {
        'source': OLD_BASE_DIR / 'api/static/preview',
        'destination': NEW_BASE_DIR / 'media/preview'
    },
    'api_static_processed': {
        'source': OLD_BASE_DIR / 'api/static/processed',
        'destination': NEW_BASE_DIR / 'media/processed'
    },
    'api_static_temp': {
        'source': OLD_BASE_DIR / 'api/static/temp',
        'destination': NEW_BASE_DIR / 'media/temp'
    },
    'data_config': {
        'source': OLD_BASE_DIR / 'data/config',
        'destination': NEW_BASE_DIR / 'data/config'
    },
    'data_backups': {
        'source': OLD_BASE_DIR / 'data/backups',
        'destination': NEW_BASE_DIR / 'data/backups'
    },
    'database': {
        'source': OLD_BASE_DIR / 'data/aphrodite.db',
        'destination': NEW_BASE_DIR / 'data/database/aphrodite.db'
    }
}

def migrate_files():
    """Migrates files and directories to their new locations."""
    for key, paths in MIGRATION_MAP.items():
        source_path = paths['source']
        destination_path = paths['destination']

        if not source_path.exists():
            logging.warning(f"Source path for '{key}' does not exist, skipping: {source_path}")
            continue

        try:
            # Ensure destination directory exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            if source_path.is_dir():
                # Move directory contents
                for item in source_path.iterdir():
                    destination_item = destination_path / item.name
                    shutil.move(str(item), str(destination_item))
                logging.info(f"Successfully migrated directory '{key}' from {source_path} to {destination_path}")
                # Optionally remove the old directory if it's empty
                if not any(source_path.iterdir()):
                    source_path.rmdir()
            else:
                # Move file
                shutil.move(str(source_path), str(destination_path))
                logging.info(f"Successfully migrated file '{key}' from {source_path} to {destination_path}")

        except Exception as e:
            logging.error(f"Error migrating '{key}': {e}")

if __name__ == "__main__":
    logging.info("Starting storage migration...")
    migrate_files()
    logging.info("Storage migration complete.")
