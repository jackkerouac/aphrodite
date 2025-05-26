# aphrodite_helpers/poster_fetcher.py

import sys
import os
import requests

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def download_poster(jellyfin_url, api_key, item_id, output_dir="posters/original"):
    """
    Downloads a primary poster for a given Jellyfin item ID.
    """
    headers = {"X-Emby-Token": api_key}
    poster_url = f"{jellyfin_url}/Items/{item_id}/Images/Primary"

    try:
        response = requests.get(poster_url, headers=headers, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error retrieving poster for item {item_id}: {e}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{item_id}.jpg")
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    print(f"✅ Poster saved: {file_path}")
    return file_path

if __name__ == "__main__":
    import argparse
    from aphrodite_helpers.check_jellyfin_connection import load_settings

    parser = argparse.ArgumentParser(description="Download a poster from Jellyfin.")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--output", default="posters/original", help="Output directory")

    args = parser.parse_args()

    settings = load_settings()
    jellyfin = settings['api_keys']['Jellyfin'][0]

    download_poster(
        jellyfin_url=jellyfin['url'],
        api_key=jellyfin['api_key'],
        item_id=args.itemid,
        output_dir=args.output
    )