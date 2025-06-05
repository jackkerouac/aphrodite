# aphrodite_helpers/read_audio_settings.py

import os
import sys

# Ensure the root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the compatibility layer
from aphrodite_helpers.settings_compat import load_badge_settings

def load_yaml_from_root(filename):
    """
    Load a YAML file from the root directory using the compatibility layer.
    """
    return load_badge_settings(filename)

def display_settings(settings: dict, indent=0):
    """
    Recursively print settings in a clean, readable format.
    """
    for key, value in settings.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            display_settings(value, indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")

if __name__ == "__main__":
    filename = "badge_settings_audio.yml"
    settings = load_yaml_from_root(filename)

    if settings:
        print(f"\n📄 Settings from {filename}:\n")
        display_settings(settings)
    else:
        print("⚠️  No settings to display.")
