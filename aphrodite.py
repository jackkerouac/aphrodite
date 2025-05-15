# import aphrodite_helpers
from aphrodite_helpers.settings_validator import run_settings_check
from aphrodite_helpers.check_jellyfin_connection import (
    load_settings,
    get_jellyfin_libraries,
    get_library_item_count
)

def main():
    BANNER = r"""
              _                   _ _ _       
             | |                 | (_) |      
   __ _ _ __ | |__  _ __ ___   __| |_| |_ ___ 
  / _` | '_ \| '_ \| '__/ _ \ / _` | | __/ _ \
 | (_| | |_) | | | | | | (_) | (_| | | ||  __/
  \__,_| .__/|_| |_|_|  \___/ \__,_|_|\__\___|
       | |                                    
       |_|                                    

                    v0.0.1       
"""
    print(BANNER)
    run_settings_check()

    try:
        settings = load_settings()
        jellyfin_settings = settings['api_keys']['Jellyfin'][0]
        url = jellyfin_settings['url']
        api_key = jellyfin_settings['api_key']
        user_id = jellyfin_settings['user_id']

        print(f"\n📡 Connecting to Jellyfin at: {url}")
        libraries = get_jellyfin_libraries(url, api_key, user_id)

        if not libraries:
            print("⚠️  No libraries found in Jellyfin.")
            return

        print("\n📚 Libraries and item counts:")
        for lib in libraries:
            lib_name = lib.get('Name', 'Unnamed')
            lib_id = lib.get('Id')
            count = get_library_item_count(url, api_key, user_id, lib_id)
            print(f"  - {lib_name}: {count} items")

    except Exception as e:
        print(f"\n❌ Failed to connect to Jellyfin or retrieve data:\n{e}")

if __name__ == "__main__":
    main()