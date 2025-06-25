#!/usr/bin/env python3
# aphrodite_helpers/badge_components/badge_settings.py

import os
import json
import logging

def load_badge_settings(settings_file="review_source_settings", force_reload=False):
    """Load badge settings from PostgreSQL database (never YAML)"""
    engine = None
    try:
        # Load badge settings from PostgreSQL using synchronous approach
        from sqlalchemy import create_engine, text
        from app.core.config import get_settings as get_app_settings
        
        # Get database URL from app settings
        app_settings = get_app_settings()
        database_url = app_settings.get_database_url()
        
        # Convert async URL to sync URL
        sync_database_url = database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
        
        # Create synchronous engine with minimal connection pool
        engine = create_engine(
            sync_database_url,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True
        )
        
        # Query the database
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT value FROM system_config WHERE key = :key"),
                {"key": settings_file}
            )
            row = result.fetchone()
            
            if row and row[0]:
                badge_settings = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                logging.info(f"Loaded badge settings from PostgreSQL: {settings_file}")
                return badge_settings
            else:
                logging.warning(f"No badge settings found in database for key: {settings_file}")
                return {}
        
    except Exception as e:
        logging.error(f"Could not load badge settings from PostgreSQL database: {e}")
        # Return empty dict rather than falling back to YAML
        return {}
    finally:
        # Clean up the engine
        if engine:
            try:
                engine.dispose()
            except Exception as cleanup_error:
                logging.warning(f"Error disposing database engine: {cleanup_error}")
