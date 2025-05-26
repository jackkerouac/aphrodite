# aphrodite_helpers/read_audio_settings.py

import os
import sys
import yaml

# Ensure the root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_yaml_from_root(filename):
    """
    Load a YAML file from the root directory.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, filename)

    if not os.path.exists(full_path):
        print(f"❌ File not found: {filename}")
        return None

    with open(full_path, "r") as file:
        return yaml.safe_load(file)

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
