import yaml
import sys
from pathlib import Path

REQUIRED_JELLYFIN_FIELDS = ["url", "api_key", "user_id"]
OPTIONAL_API_SECTIONS = ["OMDB", "TMDB", "aniDB"]

def load_settings(filepath="settings.yaml"):
    try:
        with open(filepath, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        sys.exit("❌ Error: settings.yaml file not found.")
    except yaml.YAMLError as e:
        sys.exit(f"❌ Error parsing settings.yaml: {e}")

def validate_settings(settings):
    api_keys = settings.get("api_keys", {})

    # -- Check required Jellyfin keys --
    jellyfin_list = api_keys.get("Jellyfin", [])
    if not jellyfin_list or not isinstance(jellyfin_list, list) or len(jellyfin_list) == 0:
        sys.exit("❌ Error: Jellyfin settings are missing or not formatted correctly.")

    jellyfin = jellyfin_list[0]
    missing = [key for key in REQUIRED_JELLYFIN_FIELDS if not jellyfin.get(key)]
    if missing:
        sys.exit(f"❌ Error: Jellyfin settings missing required fields: {', '.join(missing)}")

    # -- Check optional API keys --
    optional_configured = False
    for section in OPTIONAL_API_SECTIONS:
        entries = api_keys.get(section)
        if entries and isinstance(entries, list) and len(entries) > 0:
            first = entries[0]
            if any(value not in [None, "", 0] for value in first.values()):
                optional_configured = True
                break

    if not optional_configured:
        print("⚠️ Warning: No optional API keys (OMDB, TMDB, aniDB) are configured or populated.")


def run_settings_check():
    settings = load_settings()
    validate_settings(settings)
