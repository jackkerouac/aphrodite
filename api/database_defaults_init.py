#!/usr/bin/env python3
"""
Aphrodite Database Default Settings Initializer

This script automatically populates the system_config table with sensible default
badge settings when Aphrodite starts up for the first time. This ensures new users
get a working system without manual configuration.

Based on the sensible defaults specification and existing badge processing system requirements.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class DatabaseDefaultsInitializer:
    """Handles initialization of default badge settings in the database"""
    
    def __init__(self):
        self.logger = None
        self.initialized = False
    
    def setup_logging(self):
        """Setup logging for the initializer"""
        try:
            from aphrodite_logging import get_logger
            self.logger = get_logger("aphrodite.init.defaults", service="init")
        except ImportError:
            # Fallback to print statements if logging not available
            self.logger = None
    
    def log(self, level: str, message: str):
        """Log message with fallback to print"""
        if self.logger:
            getattr(self.logger, level.lower())(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    async def initialize_defaults_if_needed(self) -> bool:
        """Initialize default settings if they don't exist in database"""
        try:
            self.setup_logging()
            
            # Check if we need to initialize
            if not await self._needs_initialization():
                self.log("info", "Badge settings already exist in database, skipping initialization")
                return True
            
            self.log("info", "Initializing default badge settings in database...")
            
            # Initialize all badge settings
            success = await self._initialize_all_settings()
            
            if success:
                self.log("info", "✅ Successfully initialized all default badge settings")
                return True
            else:
                self.log("error", "❌ Failed to initialize some badge settings")
                return False
                
        except Exception as e:
            self.log("error", f"Error during defaults initialization: {e}")
            return False
    
    async def _ensure_database_initialized(self):
        """Ensure the database is properly initialized"""
        try:
            from app.core.database import init_db, async_session_factory
            
            # Check if already initialized
            if async_session_factory is None:
                self.log("info", "Initializing database connection...")
                await init_db()
                self.log("info", "Database connection initialized")
            
        except Exception as e:
            self.log("error", f"Failed to initialize database: {e}")
            raise
    
    async def _needs_initialization(self) -> bool:
        """Check if database needs initialization"""
        try:
            # Ensure database is initialized
            await self._ensure_database_initialized()
            
            from app.core.database import async_session_factory
            from sqlalchemy import text
            
            if not async_session_factory:
                self.log("error", "Database session factory not available")
                return True
            
            async with async_session_factory() as db:
                # Check if any badge settings exist
                result = await db.execute(
                    text("SELECT COUNT(*) FROM system_config WHERE key LIKE 'badge_settings_%.yml'")
                )
                count = result.scalar()
                
                self.log("debug", f"Found {count} existing badge settings in database")
                return count == 0
                
        except Exception as e:
            self.log("warning", f"Could not check database state: {e}")
            # Assume we need initialization if we can't check
            return True
    
    async def _initialize_all_settings(self) -> bool:
        """Initialize all badge settings with sensible defaults"""
        try:
            # Ensure database is initialized first
            await self._ensure_database_initialized()
            
            from app.core.database import async_session_factory
            from app.models.config import SystemConfigModel
            from sqlalchemy import text
            import uuid
            import json
            
            if not async_session_factory:
                self.log("error", "Database session factory not available after initialization")
                return False
            
            async with async_session_factory() as db:
                # Initialize each badge type
                settings_to_create = [
                    ("badge_settings_audio.yml", self._get_audio_defaults()),
                    ("badge_settings_resolution.yml", self._get_resolution_defaults()),
                    ("badge_settings_review.yml", self._get_review_defaults()),
                    ("badge_settings_awards.yml", self._get_awards_defaults()),
                    ("review_source_settings", self._get_review_source_defaults()),
                ]
                
                success_count = 0
                
                for key, settings in settings_to_create:
                    try:
                        # Check if setting already exists using the model
                        result = await db.execute(
                            text("SELECT id FROM system_config WHERE key = :key"),
                            {"key": key}
                        )
                        existing = result.fetchone()
                        
                        if existing:
                            self.log("info", f"Setting {key} already exists, skipping")
                            success_count += 1
                            continue
                        
                        # Create new SystemConfigModel instance with explicit UUID
                        config_model = SystemConfigModel(
                            id=str(uuid.uuid4()),
                            key=key,
                            value=settings
                        )
                        
                        # Add to session and commit
                        db.add(config_model)
                        await db.flush()  # Flush to get any database-generated values
                        
                        self.log("info", f"✅ Created {key}")
                        success_count += 1
                        
                    except Exception as e:
                        self.log("error", f"Failed to create {key}: {e}")
                        # Rollback this transaction to continue with others
                        await db.rollback()
                        # Start a new transaction
                        await db.begin()
                
                # Commit all successful changes
                try:
                    await db.commit()
                except Exception as e:
                    self.log("error", f"Failed to commit changes: {e}")
                    await db.rollback()
                
                self.log("info", f"Successfully created {success_count}/{len(settings_to_create)} settings")
                return success_count == len(settings_to_create)
                
        except Exception as e:
            self.log("error", f"Error initializing settings: {e}")
            return False
    
    def _get_audio_defaults(self) -> Dict[str, Any]:
        """Get sensible defaults for audio badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
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
                "image_padding": 0,
                "fallback_to_text": True,
                "image_mapping": {
                    "AAC": "aac.png",
                    "ATMOS": "Atmos.png",
                    "DOLBY DIGITAL": "dolby-digital.png",
                    "DOLBY DIGITAL PLUS": "DigitalPlus.png",
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
        }
    
    def _get_resolution_defaults(self) -> Dict[str, Any]:
        """Get sensible defaults for resolution badge settings"""
        return {
            "General": {
                "general_badge_size": 100,
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
                "image_padding": 0,
                "fallback_to_text": True,
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
        }
    
    def _get_review_defaults(self) -> Dict[str, Any]:
        """Get sensible defaults for review badge settings"""
        return {
            "General": {
                "general_badge_position": "bottom-left",
                "general_edge_padding": 30,
                "badge_orientation": "vertical",
                "badge_spacing": 15,
                "max_badges_to_display": 4,
                "general_text_padding": 20,
                "general_badge_size": 100,
                "use_dynamic_sizing": True
            },
            "Text": {
                "font": "/app/assets/fonts/AvenirNextLTProBold.otf",
                "fallback_font": "/app/assets/fonts/DejaVuSans.ttf",
                "text_color": "#FFFFFF",
                "text_size": 60
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
                "image_padding": 5,
                "fallback_to_text": True,
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
    
    def _get_review_source_defaults(self) -> Dict[str, Any]:
        """Get sensible defaults for review source settings"""
        return {
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
    
    def _get_awards_defaults(self) -> Dict[str, Any]:
        """Get sensible defaults for awards badge settings"""
        return {
            "General": {
                "enable_awards_badges": True,
                "general_badge_size": 120,
                "general_badge_position": "bottom-right-flush",
                "use_dynamic_sizing": False,
                "general_edge_padding": 0,
                "general_text_padding": 0
            },
            "Awards": {
                "color_scheme": "yellow"
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
        }


async def initialize_database_defaults() -> bool:
    """Main entry point for initializing database defaults"""
    initializer = DatabaseDefaultsInitializer()
    return await initializer.initialize_defaults_if_needed()


def run_initialization():
    """Synchronous wrapper for initialization"""
    try:
        return asyncio.run(initialize_database_defaults())
    except Exception as e:
        print(f"Error during initialization: {e}")
        return False


# Auto-initialization on startup (can be called from main application)
async def auto_initialize_on_startup():
    """Auto-initialize defaults when application starts"""
    try:
        print("🔧 Checking for badge settings initialization...")
        
        success = await initialize_database_defaults()
        
        if success:
            print("✅ Badge settings initialization complete")
        else:
            print("⚠️  Badge settings initialization had issues")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during auto-initialization: {e}")
        return False


if __name__ == "__main__":
    """Direct execution for manual initialization"""
    print("🚀 Aphrodite Database Defaults Initializer")
    print("=" * 50)
    
    success = run_initialization()
    
    if success:
        print("\n✅ Successfully initialized all badge settings!")
        print("🎉 Your Aphrodite instance is ready to use!")
    else:
        print("\n❌ Some settings failed to initialize")
        print("Please check the logs for details")
    
    sys.exit(0 if success else 1)