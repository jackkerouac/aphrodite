#!/usr/bin/env python3
"""
config_from_env.py - Populate configuration files from environment variables

This script checks for environment variables with specific prefixes and 
updates the corresponding configuration files accordingly.

Environment variable naming convention:
- APHRODITE_JELLYFIN_URL: Sets the Jellyfin URL in settings.yaml
- APHRODITE_JELLYFIN_API_KEY: Sets the Jellyfin API key in settings.yaml
- APHRODITE_JELLYFIN_USER_ID: Sets the Jellyfin user ID in settings.yaml
- APHRODITE_OMDB_API_KEY: Sets the OMDB API key in settings.yaml
- APHRODITE_TMDB_API_KEY: Sets the TMDB API key in settings.yaml
- APHRODITE_ANIDB_USERNAME: Sets the aniDB username in settings.yaml
- APHRODITE_ANIDB_PASSWORD: Sets the aniDB password in settings.yaml

- APHRODITE_AUDIO_BADGE_POSITION: Sets the general_badge_position in badge_settings_audio.yml
- APHRODITE_AUDIO_BADGE_SIZE: Sets the general_badge_size in badge_settings_audio.yml

Similar prefixes exist for RESOLUTION_ and REVIEW_ badge settings.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('config_from_env')

# Base directory
BASE_DIR = Path('/app')

# Configuration files
CONFIG_FILES = {
    'settings': BASE_DIR / 'settings.yaml',
    'audio': BASE_DIR / 'badge_settings_audio.yml',
    'resolution': BASE_DIR / 'badge_settings_resolution.yml',
    'review': BASE_DIR / 'badge_settings_review.yml'
}

# Environment variable mappings to config paths
ENV_MAPPINGS = {
    # Main settings
    'APHRODITE_JELLYFIN_URL': ['settings', 'api_keys', 'Jellyfin', 0, 'url'],
    'APHRODITE_JELLYFIN_API_KEY': ['settings', 'api_keys', 'Jellyfin', 0, 'api_key'],
    'APHRODITE_JELLYFIN_USER_ID': ['settings', 'api_keys', 'Jellyfin', 0, 'user_id'],
    'APHRODITE_OMDB_API_KEY': ['settings', 'api_keys', 'OMDB', 0, 'api_key'],
    'APHRODITE_OMDB_CACHE_EXPIRATION': ['settings', 'api_keys', 'OMDB', 0, 'cache_expiration'],
    'APHRODITE_TMDB_API_KEY': ['settings', 'api_keys', 'TMDB', 0, 'api_key'],
    'APHRODITE_TMDB_CACHE_EXPIRATION': ['settings', 'api_keys', 'TMDB', 0, 'cache_expiration'],
    'APHRODITE_TMDB_LANGUAGE': ['settings', 'api_keys', 'TMDB', 0, 'language'],
    'APHRODITE_TMDB_REGION': ['settings', 'api_keys', 'TMDB', 0, 'region'],
    'APHRODITE_ANIDB_USERNAME': ['settings', 'api_keys', 'aniDB', 0, 'username'],
    'APHRODITE_ANIDB_PASSWORD': ['settings', 'api_keys', 'aniDB', 0, 'password'],
    'APHRODITE_ANIDB_VERSION': ['settings', 'api_keys', 'aniDB', 0, 'version'],
    'APHRODITE_ANIDB_CLIENT_NAME': ['settings', 'api_keys', 'aniDB', 0, 'client_name'],
    'APHRODITE_ANIDB_LANGUAGE': ['settings', 'api_keys', 'aniDB', 0, 'language'],
    'APHRODITE_ANIDB_CACHE_EXPIRATION': ['settings', 'api_keys', 'aniDB', 0, 'cache_expiration'],
    
    # Audio badge settings
    'APHRODITE_AUDIO_BADGE_POSITION': ['audio', 'General', 'general_badge_position'],
    'APHRODITE_AUDIO_BADGE_SIZE': ['audio', 'General', 'general_badge_size'],
    'APHRODITE_AUDIO_EDGE_PADDING': ['audio', 'General', 'general_edge_padding'],
    'APHRODITE_AUDIO_TEXT_PADDING': ['audio', 'General', 'general_text_padding'],
    'APHRODITE_AUDIO_DYNAMIC_SIZING': ['audio', 'General', 'use_dynamic_sizing'],
    'APHRODITE_AUDIO_FONT': ['audio', 'Text', 'font'],
    'APHRODITE_AUDIO_TEXT_COLOR': ['audio', 'Text', 'text-color'],
    'APHRODITE_AUDIO_BG_COLOR': ['audio', 'Background', 'background-color'],
    'APHRODITE_AUDIO_BG_OPACITY': ['audio', 'Background', 'background_opacity'],
    
    # Resolution badge settings
    'APHRODITE_RESOLUTION_BADGE_POSITION': ['resolution', 'General', 'general_badge_position'],
    'APHRODITE_RESOLUTION_BADGE_SIZE': ['resolution', 'General', 'general_badge_size'],
    'APHRODITE_RESOLUTION_EDGE_PADDING': ['resolution', 'General', 'general_edge_padding'],
    'APHRODITE_RESOLUTION_TEXT_PADDING': ['resolution', 'General', 'general_text_padding'],
    'APHRODITE_RESOLUTION_DYNAMIC_SIZING': ['resolution', 'General', 'use_dynamic_sizing'],
    'APHRODITE_RESOLUTION_FONT': ['resolution', 'Text', 'font'],
    'APHRODITE_RESOLUTION_TEXT_COLOR': ['resolution', 'Text', 'text-color'],
    'APHRODITE_RESOLUTION_BG_COLOR': ['resolution', 'Background', 'background-color'],
    'APHRODITE_RESOLUTION_BG_OPACITY': ['resolution', 'Background', 'background_opacity'],
    
    # Review badge settings
    'APHRODITE_REVIEW_BADGE_POSITION': ['review', 'General', 'general_badge_position'],
    'APHRODITE_REVIEW_BADGE_SIZE': ['review', 'General', 'general_badge_size'],
    'APHRODITE_REVIEW_EDGE_PADDING': ['review', 'General', 'general_edge_padding'],
    'APHRODITE_REVIEW_TEXT_PADDING': ['review', 'General', 'general_text_padding'],
    'APHRODITE_REVIEW_MAX_BADGES': ['review', 'General', 'max_badges_to_display'],
    'APHRODITE_REVIEW_BADGE_ORIENTATION': ['review', 'General', 'badge_orientation'],
    'APHRODITE_REVIEW_BADGE_SPACING': ['review', 'General', 'badge_spacing'],
    'APHRODITE_REVIEW_DYNAMIC_SIZING': ['review', 'General', 'use_dynamic_sizing'],
    'APHRODITE_REVIEW_FONT': ['review', 'Text', 'font'],
    'APHRODITE_REVIEW_TEXT_COLOR': ['review', 'Text', 'text-color'],
    'APHRODITE_REVIEW_BG_COLOR': ['review', 'Background', 'background-color'],
    'APHRODITE_REVIEW_BG_OPACITY': ['review', 'Background', 'background_opacity']
}


def load_config(config_file: Path) -> Dict[str, Any]:
    """Load a configuration file"""
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            logger.warning(f"Configuration file {config_file} not found")
            return {}
    except Exception as e:
        logger.error(f"Error loading {config_file}: {e}")
        return {}


def save_config(config_file: Path, config_data: Dict[str, Any]) -> bool:
    """Save a configuration file"""
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {config_file}: {e}")
        return False


def set_nested_value(config: Dict[str, Any], path: list, value: Any) -> None:
    """Set a value in a nested dictionary using a path list"""
    if not path:
        return

    current = config
    for i, key in enumerate(path[:-1]):
        # Convert string indices to integers for list access
        if isinstance(key, str) and key.isdigit():
            key = int(key)
            
        # Handle list indices
        if isinstance(key, int):
            # Ensure the list is long enough
            while len(current) <= key:
                current.append({})
            
            # If not a dict, make it one
            if not isinstance(current[key], (dict, list)):
                current[key] = {}
                
            current = current[key]
        else:
            # Handle dictionary keys
            if key not in current or current[key] is None:
                current[key] = {}
            elif not isinstance(current[key], (dict, list)):
                current[key] = {}
            
            # If this is the second-to-last key and the last key is an index,
            # make sure the value is a list
            if i == len(path) - 2 and isinstance(path[-1], int):
                if not isinstance(current[key], list):
                    current[key] = []
                    
            current = current[key]

    # Set the value at the final key
    last_key = path[-1]
    if isinstance(last_key, str) and last_key.isdigit():
        last_key = int(last_key)
        
    if isinstance(last_key, int):
        # Ensure the list is long enough
        while len(current) <= last_key:
            current.append(None)
        current[last_key] = value
    else:
        current[last_key] = value


def update_configs_from_env() -> None:
    """Update configuration files based on environment variables"""
    # Load all config files
    configs = {key: load_config(file_path) for key, file_path in CONFIG_FILES.items()}
    
    # Track which configs were modified
    modified = set()
    
    # Process each known environment variable
    for env_var, path in ENV_MAPPINGS.items():
        if env_var in os.environ:
            config_key = path[0]
            value_path = path[1:]
            
            # Convert value based on the current type in config
            value = os.environ[env_var]
            
            # Type conversion (basic)
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            
            # Set the value in the config
            set_nested_value(configs[config_key], value_path, value)
            modified.add(config_key)
            logger.info(f"Set {env_var} -> {'.'.join(str(p) for p in path[1:])}")
    
    # Save modified configs
    for config_key in modified:
        if save_config(CONFIG_FILES[config_key], configs[config_key]):
            logger.info(f"Updated {CONFIG_FILES[config_key]}")


if __name__ == "__main__":
    logger.info("Processing environment variables for configuration")
    update_configs_from_env()
    logger.info("Configuration update complete")
