#!/usr/bin/env python3
"""
V2 Badge Processing Subprocess Runner - FIXED DATABASE INITIALIZATION
Isolated runner for V2 badge processing to avoid Celery import conflicts
"""

import sys
import json
import asyncio
import os
import logging
from pathlib import Path

# CRITICAL: Disable v1 legacy imports that cause database table errors
V2_ONLY_MODE = os.environ.get('APHRODITE_V2_ONLY', '0') == '1'

def run_v2_processing():
    """Run V2 badge processing in isolated subprocess"""
    
    # Suppress ALL logging to stdout to keep JSON response clean
    logging.getLogger().handlers = []
    logging.basicConfig(level=logging.CRITICAL)  # Only critical errors
    
    # Suppress SQLAlchemy logs completely
    logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
    
    # Set UTF-8 for Windows console
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        # Read request from stdin
        request_json = sys.stdin.read().strip()
        request_data = json.loads(request_json)
        
        # Convert to absolute paths
        original_cwd = os.getcwd()
        script_dir = Path(__file__).parent
        api_dir = script_dir / "api"
        
        poster_path = request_data["poster_path"]
        output_path = request_data["output_path"]
        
        if not os.path.isabs(poster_path):
            poster_path = os.path.join(original_cwd, poster_path)
        if not os.path.isabs(output_path):
            output_path = os.path.join(original_cwd, output_path)
        
        # Change to API directory
        os.chdir(api_dir)
        sys.path.insert(0, str(api_dir))
        
        async def process_with_database():
            # CRITICAL FIX: Initialize database first
            try:
                from app.core.database import init_db
                await init_db()
                # Log successful database initialization
                print("Database initialized successfully", file=sys.stderr)
            except Exception as db_error:
                print(f"Database initialization failed: {db_error}", file=sys.stderr)
                raise
            
            # Import V2 components after database initialization
            try:
                from app.services.badge_processing.pipeline import UniversalBadgeProcessor
                from app.services.badge_processing.types import SingleBadgeRequest
                print("Imported badge processing components successfully", file=sys.stderr)
            except ImportError as import_error:
                print(f"Import error: {import_error}", file=sys.stderr)
                raise
            
            # Create and run request
            request = SingleBadgeRequest(
                poster_path=poster_path,
                badge_types=request_data["badge_types"],
                output_path=output_path,
                use_demo_data=request_data.get("use_demo_data", False),
                jellyfin_id=request_data.get("jellyfin_id")
            )
            
            processor = UniversalBadgeProcessor()
            result = await processor.process_single(request)
            
            return result
        
        # Run processing with database initialization
        result = asyncio.run(process_with_database())
        
        # Extract results
        applied_badges = []
        final_output_path = None
        
        if result.results and len(result.results) > 0:
            first_result = result.results[0]
            applied_badges = first_result.applied_badges
            final_output_path = first_result.output_path
        
        # Return clean JSON response
        response = {
            "success": result.success,
            "applied_badges": applied_badges,
            "output_path": str(final_output_path) if final_output_path else None,
            "processing_time": result.processing_time,
            "error": result.error
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            "success": False,
            "applied_badges": [],
            "output_path": None,
            "processing_time": 0,
            "error": str(e)
        }
        print(json.dumps(error_response))
        
    finally:
        if 'original_cwd' in locals():
            os.chdir(original_cwd)

if __name__ == "__main__":
    run_v2_processing()
