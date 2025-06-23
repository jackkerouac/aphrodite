#!/usr/bin/env python3
"""
Initialize Badge Settings in Database

This script loads the YAML badge settings files and inserts them into the database
with proper Docker-compatible paths.
"""

import os
import sys
import yaml
import json
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def load_badge_settings():
    """Load badge settings from YAML files and insert into database"""
    
    print("🔧 Initializing badge settings in database...")
    
    try:
        # Import database components
        from api.app.core.database import async_session_factory
        from api.app.models.config import SystemConfigModel
        from sqlalchemy import text
        
        # Badge settings files to load
        badge_files = {
            "audio": "data/config/badge_settings_audio.yml",
            "resolution": "data/config/badge_settings_resolution.yml", 
            "review": "data/config/badge_settings_review.yml"
        }
        
        async with async_session_factory() as db:
            for badge_type, file_path in badge_files.items():
                if not Path(file_path).exists():
                    print(f"⚠️  {file_path} not found, skipping {badge_type}")
                    continue
                
                print(f"📄 Loading {badge_type} settings from {file_path}")
                
                # Load YAML file
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = yaml.safe_load(f)
                
                # Update paths for Docker compatibility
                settings = update_paths_for_docker(settings, badge_type)
                
                # Check if settings already exist
                key = f"badge_settings_{badge_type}"
                result = await db.execute(
                    text("SELECT id FROM system_config WHERE key = :key"),
                    {"key": key}
                )
                existing = result.fetchone()
                
                if existing:
                    # Update existing
                    await db.execute(
                        text("UPDATE system_config SET value = :value WHERE key = :key"),
                        {"key": key, "value": json.dumps(settings)}
                    )
                    print(f"✅ Updated {badge_type} badge settings in database")
                else:
                    # Insert new
                    await db.execute(
                        text("INSERT INTO system_config (key, value) VALUES (:key, :value)"),
                        {"key": key, "value": json.dumps(settings)}
                    )
                    print(f"✅ Inserted {badge_type} badge settings into database")
            
            # Commit all changes
            await db.commit()
            print("🎉 All badge settings initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing badge settings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def update_paths_for_docker(settings, badge_type):
    """Update relative paths to Docker-compatible absolute paths"""
    
    # Font path updates
    if "Text" in settings:
        text_settings = settings["Text"]
        
        # Update font path
        if "font" in text_settings:
            font_file = text_settings["font"]
            if not font_file.startswith("/"):
                text_settings["font"] = f"/app/assets/fonts/{font_file}"
        
        # Update fallback font path
        if "fallback_font" in text_settings:
            fallback_font = text_settings["fallback_font"]
            if not fallback_font.startswith("/"):
                text_settings["fallback_font"] = f"/app/assets/fonts/{fallback_font}"
    
    # Image directory path updates
    if "ImageBadges" in settings:
        image_settings = settings["ImageBadges"]
        
        # Update codec_image_directory
        if "codec_image_directory" in image_settings:
            image_dir = image_settings["codec_image_directory"]
            if not image_dir.startswith("/"):
                image_settings["codec_image_directory"] = f"/app/assets/{image_dir}"
    
    print(f"  📝 Updated paths for {badge_type}:")
    if "Text" in settings:
        print(f"    Font: {settings['Text'].get('font', 'N/A')}")
        print(f"    Fallback: {settings['Text'].get('fallback_font', 'N/A')}")
    if "ImageBadges" in settings:
        print(f"    Images: {settings['ImageBadges'].get('codec_image_directory', 'N/A')}")
    
    return settings

async def check_database_connection():
    """Check if database is accessible"""
    try:
        from api.app.core.database import async_session_factory
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
    print("🚀 Badge Settings Database Initialization")
    print("=" * 50)
    
    # Check database connection first
    if not await check_database_connection():
        print("❌ Cannot connect to database - make sure it's running")
        return 1
    
    # Load badge settings
    if await load_badge_settings():
        print("\n🎉 Badge settings initialization complete!")
        print("\nNext steps:")
        print("1. Restart the Docker container: docker-compose restart aphrodite")
        print("2. Test the preview generation - badges should now work correctly")
        return 0
    else:
        print("\n❌ Badge settings initialization failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
