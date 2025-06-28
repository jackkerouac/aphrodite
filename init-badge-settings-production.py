#!/usr/bin/env python3
"""
Initialize Badge Settings in Database - Production Ready

This script loads badge settings with proper Docker paths and creates 
initial settings that match your local configuration but with Docker paths.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def initialize_default_settings():
    """Initialize default settings matching your local database but with Docker paths"""
    
    print("🔧 Initializing default badge settings in database...")
    
    try:
        # Import database components
        from api.app.core.database import async_session_factory
        from sqlalchemy import text
        
        # Production-ready badge settings with your current configuration
        badge_settings = {
            "badge_settings_audio.yml": {
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
            "badge_settings_awards.yml": {
                "General": {
                    "enabled": True,
                    "general_badge_size": 351,
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
                    "background_opacity": 0
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
                        "crunchyroll": "crunchyroll.png",
                        "berlinale": "berlinale.png",
                        "venice": "venice.png",
                        "sundance": "sundance.png",
                        "spirit": "spirit.png",
                        "choice": "choice.png",
                        "cesar": "cesar.png",
                        "imdb": "imdb.png",
                        "letterboxd": "letterboxd.png",
                        "metacritic": "metacritic.png",
                        "netflix": "netflix.png",
                        "razzie": "razzie.png",
                        "rotten": "rotten.png"
                    }
                },
                "AwardSources": {
                    "enable_academy_awards": True,
                    "enable_cannes": True,
                    "enable_golden_globes": True,
                    "enable_bafta": True,
                    "enable_emmys": True,
                    "enable_crunchyroll_anime": True,
                    "enable_berlinale": False,
                    "enable_venice": False,
                    "enable_sundance": False,
                    "enable_spirit": False,
                    "enable_critics_choice": False,
                    "enable_cesar": False,
                    "enable_imdb_top": False,
                    "enable_letterboxd": False,
                    "enable_metacritic": False,
                    "enable_netflix": False,
                    "enable_razzie": False,
                    "enable_rotten_tomatoes": False,
                    "enable_rotten_tomatoes_verified": False
                }
            },
            "badge_settings_resolution.yml": {
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
            "badge_settings_review.yml": {
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
        
        async with async_session_factory() as db:
            for key, settings in badge_settings.items():
                print(f"📄 Initializing {key}")
                
                # Check if settings already exist
                result = await db.execute(
                    text("SELECT id FROM system_config WHERE key = :key"),
                    {"key": key}
                )
                existing = result.fetchone()
                
                if existing:
                    # Update existing with Docker paths
                    await db.execute(
                        text("UPDATE system_config SET value = :value WHERE key = :key"),
                        {"key": key, "value": json.dumps(settings)}
                    )
                    print(f"✅ Updated {key} with Docker-compatible paths")
                else:
                    # Insert new
                    await db.execute(
                        text("INSERT INTO system_config (key, value) VALUES (:key, :value)"),
                        {"key": key, "value": json.dumps(settings)}
                    )
                    print(f"✅ Inserted {key} into database")
            
            # Initialize review source settings if not exists
            review_settings = {
                "max_badges_display": 5,
                "source_selection_mode": "priority",
                "show_percentage_only": True,
                "group_related_sources": True,
                "anime_sources_for_anime_only": True,
                "Sources": {
                    "max_badges_to_display": 4,
                    "selection_mode": "priority_order",
                    "show_percentage_only": True,
                    "enable_imdb": True,
                    "imdb_priority": 1,
                    "enable_rotten_tomatoes_critics": True,
                    "rotten_tomatoes_critics_priority": 2,
                    "enable_metacritic": True,
                    "metacritic_priority": 3,
                    "enable_tmdb": True,
                    "tmdb_priority": 4,
                    "enable_anidb": True,
                    "anidb_priority": 5,
                    "enable_rotten_tomatoes_audience": False,
                    "rotten_tomatoes_audience_priority": 6,
                    "enable_letterboxd": False,
                    "letterboxd_priority": 7,
                    "enable_myanimelist": True,
                    "myanimelist_priority": 8,
                    "enable_trakt": False,
                    "trakt_priority": 9,
                    "enable_mdblist": False,
                    "mdblist_priority": 10
                }
            }
            
            result = await db.execute(
                text("SELECT id FROM system_config WHERE key = 'review_source_settings'"),
            )
            if not result.fetchone():
                await db.execute(
                    text("INSERT INTO system_config (key, value) VALUES (:key, :value)"),
                    {"key": "review_source_settings", "value": json.dumps(review_settings)}
                )
                print("✅ Inserted review source settings")
            
            # Initialize placeholder settings.yaml (without sensitive data)
            placeholder_settings = {
                "api_keys": {
                    "Jellyfin": [],
                    "OMDB": [],
                    "TMDB": [],
                    "aniDB": [],
                    "MDBList": []
                }
            }
            
            result = await db.execute(
                text("SELECT id FROM system_config WHERE key = 'settings.yaml'"),
            )
            if not result.fetchone():
                await db.execute(
                    text("INSERT INTO system_config (key, value) VALUES (:key, :value)"),
                    {"key": "settings.yaml", "value": json.dumps(placeholder_settings)}
                )
                print("✅ Inserted placeholder API settings")
            
            # Commit all changes
            await db.commit()
            print("🎉 All settings initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing settings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def check_database_connection():
    """Check if database is accessible"""
    try:
        from api.app.core.database import async_session_factory
        from sqlalchemy import text
        async with async_session_factory() as db:
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main execution"""
    print("🚀 Aphrodite Production Settings Initialization")
    print("=" * 50)
    
    # Check database connection first
    if not await check_database_connection():
        print("❌ Cannot connect to database - make sure it's running")
        return 1
    
    # Initialize settings
    if await initialize_default_settings():
        print("\n🎉 Production settings initialization complete!")
        print("\nSettings initialized:")
        print("• Badge settings with Docker-compatible paths")
        print("• Review source configuration")
        print("• Placeholder API settings (configure via web interface)")
        print("\nReady for production deployment!")
        return 0
    else:
        print("\n❌ Settings initialization failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
