#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_settings.py

import os
import yaml
import logging

def load_badge_settings(settings_file="badge_settings_audio.yml"):
    """Load badge settings from the provided YAML file."""
    # Get project root directory (2 levels up from this file)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(root_dir, settings_file)
    
    try:
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: Badge settings file {settings_file} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing badge settings: {e}")
        return None
