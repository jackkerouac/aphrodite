#!/usr/bin/env python3
"""
Manual Production Settings Initialization

Run this to manually initialize production settings in the running container.
"""

import requests
import json

def initialize_production_settings():
    print("🔧 Manually Initializing Production Settings")
    print("=" * 50)
    
    # Production-ready badge settings with Docker paths
    badge_settings = {
        "audio": {
            "General": {
                "general_badge_size": 300,
                "general_edge_padding": 30,
                "general_badge_position": "top-right",
                "general_text_padding": 12,
                "use_dynamic_sizing": True
            },
            "Text": {
                "font": "/app/assets/fonts/AvenirNextLTProBold.otf",
                "fallback_font": "/app/assets/fonts/DejaVuSans.ttf",
                "text_color": "#FFFFFF",
                "text_size": 90
            },
            "Background": {
                "background_color": "#000000",
                "background_opacity": 40
            },
            "Border": {
                "border_color": "#000000",
                "border_radius": 10,
                "border_width": 1
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 8,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "codec_image_directory": "/app/assets/images/codec",
                "fallback_to_text": False,
                "image_padding": 0,
                "image_mapping": {
                    "AAC": "aac.png",
                    "ATMOS": "Atmos.png",
                    "DOLBY DIGITAL": "dolby-digital.png",
                    "DOLBY DIGITAL PLUS": "dolby-digital-plus.png",
                    "DTS-HD MA": "DTS-HD.png",
                    "DTS-X": "DTS-X.png",
                    "TRUEHD": "TrueHD.png",
                    "TRUEHD ATMOS": "TrueHD-Atmos.png",
                    "DV": "DV.png",
                    "DV-ATMOS": "DV-Atmos.png",
                    "DV-DTS-HD": "DV-DTS-HD.png",
                    "DV-DTS-X": "DV-DTS-X.png",
                    "DV-TRUEHD": "DV-TrueHD.png",
                    "DV-TRUEHD-ATMOS": "DV-TrueHD-Atmos.png",
                    "HDR": "HDR.png",
                    "HDR-ATMOS": "HDR-Atmos.png",
                    "HDR-DTS-HD": "HDR-DTS-HD.png",
                    "HDR-DTS-X": "HDR-DTS-X.png",
                    "HDR-TRUEHD": "HDR-TrueHD.png",
                    "HDR-TRUEHD-ATMOS": "HDR-TrueHD-Atmos.png"
                }
            }
        },
        "awards": {
            "General": {
                "enabled": True,
                "general_badge_size": 120,
                "general_badge_position": "bottom-right-flush",
                "general_edge_padding": 0,
                "general_text_padding": 0,
                "use_dynamic_sizing": False,
                "enable_awards_badges": True
            },
            "Awards": {
                "color_scheme": "yellow",
                "award_sources": ["oscars", "emmys", "golden", "bafta", "cannes", "crunchyroll"]
            },
            "Text": {
                "font": "/app/assets/fonts/AvenirNextLTProBold.otf",
                "fallback_font": "/app/assets/fonts/DejaVuSans.ttf",
                "text_color": "#FFFFFF",
                "text_size": 90
            },
            "Background": {
                "background_color": "#000000",
                "background_opacity": 60
            },
            "Border": {
                "border_color": "#000000",
                "border_radius": 10,
                "border_width": 1
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 8,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "codec_image_directory": "/app/assets/images/awards/yellow",
                "fallback_to_text": False,
                "image_padding": 0,
                "image_mapping": {
                    "oscars": "oscars.png",
                    "cannes": "cannes.png",
                    "golden": "golden.png",
                    "bafta": "bafta.png",
                    "emmys": "emmys.png",
                    "crunchyroll": "crunchyroll.png"
                }
            }
        },
        "resolution": {
            "General": {
                "general_badge_size": 300,
                "general_edge_padding": 30,
                "general_badge_position": "top-left",
                "general_text_padding": 12,
                "use_dynamic_sizing": True
            },
            "Text": {
                "font": "/app/assets/fonts/AvenirNextLTProBold.otf",
                "fallback_font": "/app/assets/fonts/DejaVuSans.ttf",
                "text_color": "#FFFFFF",
                "text_size": 90
            },
            "Background": {
                "background_color": "#000000",
                "background_opacity": 40
            },
            "Border": {
                "border_color": "#000000",
                "border_radius": 10,
                "border_width": 1
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 8,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "codec_image_directory": "/app/assets/images/resolution",
                "fallback_to_text": True,
                "image_padding": 20,
                "image_mapping": {
                    "480p": "480p.png",
                    "576p": "576p.png",
                    "720p": "720p.png",
                    "1080p": "1080p.png",
                    "4K": "4k.png",
                    "4K HDR": "4khdr.png",
                    "4K DV": "4kdv.png",
                    "1080p HDR": "1080phdr.png",
                    "1080p DV": "1080pdv.png",
                    "HDR": "hdr.png",
                    "DV": "dv.png"
                }
            }
        },
        "review": {
            "General": {
                "general_badge_size": 100,
                "general_edge_padding": 30,
                "general_badge_position": "bottom-left",
                "general_text_padding": 10,
                "use_dynamic_sizing": True,
                "badge_orientation": "vertical",
                "badge_spacing": 15,
                "max_badges_to_display": 4
            },
            "Sources": {
                "enable_imdb": True,
                "enable_rotten_tomatoes": True,
                "enable_metacritic": True,
                "enable_tmdb": True,
                "enable_myanimelist": False,
                "enable_anidb": False,
                "source_priority": ["imdb", "rotten_tomatoes", "metacritic", "tmdb", "mdblist", "myanimelist", "anidb", "rotten_tomatoes_audience", "letterboxd", "trakt"],
                "minimum_votes_threshold": 100,
                "fallback_behavior": "hide",
                "enable_mdblist": True,
                "enable_rotten_tomatoes_critics": True,
                "enable_rotten_tomatoes_audience": False,
                "enable_letterboxd": False,
                "enable_trakt": False
            },
            "Text": {
                "font": "/app/assets/fonts/AvenirNextLTProBold.otf",
                "fallback_font": "/app/assets/fonts/DejaVuSans.ttf",
                "text_color": "#FFFFFF",
                "text_size": 45
            },
            "Background": {
                "background_color": "#2C2C2C",
                "background_opacity": 60
            },
            "Border": {
                "border_color": "#2C2C2C",
                "border_radius": 10,
                "border_width": 1
            },
            "Shadow": {
                "shadow_enable": False,
                "shadow_blur": 5,
                "shadow_offset_x": 2,
                "shadow_offset_y": 2
            },
            "ImageBadges": {
                "enable_image_badges": True,
                "codec_image_directory": "/app/assets/images/rating",
                "fallback_to_text": True,
                "image_padding": 5,
                "image_mapping": {
                    "IMDb": "imdb.png",
                    "Rotten Tomatoes": "rt.png",
                    "RT-Crit-Fresh": "RT-Crit-Fresh.png",
                    "RT-Crit-Rotten": "RT-Crit-Rotten.png",
                    "Metacritic": "metacritic_logo.png",
                    "TMDb": "tmdb.png",
                    "MyAnimeList": "mal.png",
                    "AniDB": "AniDB.png",
                    "Letterboxd": "Letterboxd.png",
                    "Trakt": "Trakt.png"
                }
            }
        }
    }
    
    print("📄 Uploading badge settings...")
    
    # Upload each badge setting type
    for badge_type, settings in badge_settings.items():
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/config/badge-settings/{badge_type}",
                json=settings,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ {badge_type.title()} badge settings uploaded successfully")
            else:
                print(f"❌ {badge_type.title()} badge settings failed: HTTP {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print(f"❌ {badge_type.title()} badge settings upload failed: {e}")
    
    print("\n🔍 Verifying uploaded settings...")
    
    # Verify the settings were uploaded
    try:
        response = requests.get("http://localhost:8000/api/v1/config/badge-settings", timeout=10)
        if response.status_code == 200:
            settings = response.json()
            uploaded_types = list(settings.keys())
            print(f"✅ Badge settings verified: {', '.join(uploaded_types)}")
            
            # Check first setting for Docker paths
            if uploaded_types:
                first_type = uploaded_types[0]
                font_path = settings[first_type].get('Text', {}).get('font', '')
                if font_path.startswith('/app/assets/fonts/'):
                    print("✅ Docker paths confirmed in uploaded settings")
                else:
                    print(f"⚠️  Font path check: {font_path}")
        else:
            print(f"❌ Verification failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    print("\n🎉 Manual initialization complete!")
    print("Your container now has production-ready badge settings with Docker paths.")

if __name__ == "__main__":
    initialize_production_settings()
