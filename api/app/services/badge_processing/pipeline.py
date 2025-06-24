from __future__ import annotations

import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from aphrodite_logging import get_logger
from app.core.database import async_session_factory

from .types import (
    UniversalBadgeRequest,
    SingleBadgeRequest,
    BulkBadgeRequest,
    ProcessingResult,
    PosterResult,
    ProcessingMode,
)
from .audio_processor import AudioBadgeProcessor
from .resolution_processor import ResolutionBadgeProcessor
from .review_processor import ReviewBadgeProcessor
from .awards_processor import AwardsBadgeProcessor


class UniversalBadgeProcessor:
    """Universal entry point for badge processing."""

    def __init__(self):
        self.logger = get_logger("aphrodite.badge.pipeline")

    async def process_request(self, request: UniversalBadgeRequest) -> ProcessingResult:
        start = time.perf_counter()

        if request.processing_mode == ProcessingMode.AUTO:
            mode = await self.auto_select_mode(request)
        else:
            mode = request.processing_mode

        # Use database session - try session factory first, fall back to engine
        try:
            from app.core.database import async_session_factory
            if async_session_factory is not None:
                async with async_session_factory() as db_session:
                    result = await self._process_with_session(request, mode, db_session)
            else:
                # Fallback to creating session from engine
                from app.core.database import get_engine
                from sqlalchemy.ext.asyncio import AsyncSession
                engine = get_engine()
                async with AsyncSession(engine) as db_session:
                    result = await self._process_with_session(request, mode, db_session)
        except Exception as e:
            self.logger.error(f"Database session error: {e}")
            result = ProcessingResult(success=False, results=[], error=f"Database session error: {str(e)}")

        result.processing_time = time.perf_counter() - start
        return result
    
    async def _process_with_session(self, request: UniversalBadgeRequest, mode: ProcessingMode, db_session) -> ProcessingResult:
        """Process request with database session"""
        if mode == ProcessingMode.IMMEDIATE and request.single_request:
            result = await self.process_single(request.single_request, db_session)
        elif mode == ProcessingMode.QUEUED and request.bulk_request:
            result = await self.process_bulk_with_session(request.bulk_request, db_session)
        else:
            result = ProcessingResult(success=False, results=[], error="Invalid request")
        return result

    async def process_single(self, request: SingleBadgeRequest, db_session: Optional[AsyncSession] = None) -> ProcessingResult:
        self.logger.debug(f"Processing single poster: {request.poster_path}")
        
        try:
            # Get database session if not provided
            if not db_session:
                try:
                    from app.core.database import async_session_factory
                    if async_session_factory is not None:
                        async with async_session_factory() as db:
                            return await self._process_single_with_session(request, db)
                    else:
                        # Fallback to creating session from engine
                        from app.core.database import get_engine
                        from sqlalchemy.ext.asyncio import AsyncSession
                        engine = get_engine()
                        async with AsyncSession(engine) as db:
                            return await self._process_single_with_session(request, db)
                except Exception as session_error:
                    self.logger.error(f"Failed to create database session: {session_error}")
                    raise
            else:
                return await self._process_single_with_session(request, db_session)
                
        except Exception as e:
            self.logger.error(f"Error processing single poster: {e}", exc_info=True)
            return ProcessingResult(
                success=False,
                results=[],
                error=str(e)
            )
    
    async def _process_single_with_session(self, request: SingleBadgeRequest, db_session: AsyncSession) -> ProcessingResult:
        """Process single poster with database session"""
        from pathlib import Path
        from .poster_resizer import poster_resizer
        from app.services.poster_management import StorageManager
        
        # CRITICAL DEBUG: Log what badges are being processed
        self.logger.info(f"🎯 PROCESSING BADGES: {request.badge_types}")
        self.logger.info(f"🎯 USE_DEMO_DATA: {request.use_demo_data}")
        self.logger.info(f"🎯 JELLYFIN_ID: {request.jellyfin_id}")
        
        # Step 1: Resize poster to standard 1,000px width
        self.logger.debug(f"Resizing poster to standard dimensions: {request.poster_path}")
        resized_poster_path = poster_resizer.resize_poster(request.poster_path)
        
        if not resized_poster_path:
            self.logger.error(f"Failed to resize poster: {request.poster_path}")
            return ProcessingResult(
                success=False,
                results=[],
                error="Failed to resize poster to standard dimensions"
            )
        
        self.logger.info(f"Poster resized to standard dimensions: {resized_poster_path}")
        
        # Step 2: Initialize badge processors
        processors = {
            "audio": AudioBadgeProcessor(),
            "resolution": ResolutionBadgeProcessor(),
            "review": ReviewBadgeProcessor(),
            "awards": AwardsBadgeProcessor()
        }
        
        # Start with the resized poster
        current_poster_path = resized_poster_path
        applied_badges = []
        
        self.logger.info(f"Processing resized poster {resized_poster_path} with badges: {request.badge_types}")
        
        # Apply badges sequentially
        for i, badge_type in enumerate(request.badge_types):
            processor = processors.get(badge_type)
            if not processor:
                self.logger.warning(f"Unknown badge type: {badge_type}, skipping")
                continue
            
            self.logger.info(f"🔄 Applying {badge_type} badge ({i+1}/{len(request.badge_types)})")
            self.logger.info(f"🔄 Current poster path: {current_poster_path}")
            
            # For the last badge, use the final output path if specified
            is_last_badge = (i == len(request.badge_types) - 1)
            output_path = request.output_path if is_last_badge and request.output_path else None
            
            self.logger.info(f"🔄 Output path for {badge_type}: {output_path}")
            
            # Process with the specific badge processor
            result = await processor.process_single(
                current_poster_path,
                output_path,
                request.use_demo_data,
                db_session,
                request.jellyfin_id
            )
            
            self.logger.info(f"🔄 {badge_type} badge result - Success: {result.success}, Applied: {result.applied_badges}, Error: {result.error}")
            
            if result.success:
                self.logger.info(f"✅ {badge_type} badge successful: {current_poster_path} -> {result.output_path}")
                current_poster_path = result.output_path
                applied_badges.extend(result.applied_badges)
            else:
                self.logger.error(f"❌ {badge_type} badge failed: {result.error}")
                # Continue with other badges even if one fails
        
        # CRITICAL FIX: Ensure proper preview path for final output
        storage_manager = StorageManager()
        
        # Step 3: Handle final output path
        if applied_badges:
            # Badges were applied - ensure final path has preview_ prefix
            final_filename = Path(current_poster_path).name
            
            if not final_filename.startswith("preview_"):
                # File needs to be renamed to have preview_ prefix
                proper_preview_path = storage_manager.create_preview_output_path(request.poster_path)
                try:
                    # Copy/move the final result to proper preview location
                    import shutil
                    Path(proper_preview_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(current_poster_path, proper_preview_path)
                    final_output_path = proper_preview_path
                    self.logger.info(f"🔧 Renamed to proper preview path: {final_output_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to rename to preview path: {e}, using original")
                    final_output_path = current_poster_path
            else:
                final_output_path = current_poster_path
            
            final_result = PosterResult(
                source_path=request.poster_path,
                output_path=final_output_path,
                applied_badges=applied_badges,
                success=True
            )
            self.logger.info(f"✅ Successfully processed poster with {len(applied_badges)} badges: {final_output_path}")
        else:
            # No badges were applied - create proper preview path
            proper_preview_path = storage_manager.create_preview_output_path(request.poster_path)
            
            try:
                # Copy resized poster to proper preview location
                import shutil
                Path(proper_preview_path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(resized_poster_path, proper_preview_path)
                
                # Clean up temp resized poster
                if resized_poster_path != request.poster_path:
                    Path(resized_poster_path).unlink(missing_ok=True)
                
                final_output_path = proper_preview_path
                self.logger.info(f"🔧 No badges applied, created proper preview path: {final_output_path}")
                
            except Exception as e:
                self.logger.error(f"Error creating proper preview path: {e}")
                final_output_path = resized_poster_path
            
            final_result = PosterResult(
                source_path=request.poster_path,
                output_path=final_output_path,
                applied_badges=[],
                success=True
            )
        
        # Clean up any remaining temporary resized poster
        try:
            if resized_poster_path != request.poster_path and resized_poster_path != final_result.output_path:
                if Path(resized_poster_path).exists():
                    Path(resized_poster_path).unlink()
                    self.logger.debug(f"🧹 Cleaned up temporary resized poster: {resized_poster_path}")
        except Exception as e:
            self.logger.warning(f"Failed to clean up temporary poster: {e}")
        
        return ProcessingResult(success=True, results=[final_result])

    async def process_bulk_with_session(self, request: BulkBadgeRequest, db_session: AsyncSession) -> ProcessingResult:
        """Process bulk with existing database session"""
        self.logger.debug(f"Processing bulk posters: {len(request.poster_paths)}")
        results: List[PosterResult] = []
        
        for path in request.poster_paths:
            single_result = await self.process_single(
                SingleBadgeRequest(
                    poster_path=path,
                    badge_types=request.badge_types,
                    use_demo_data=request.use_demo_data,
                    output_path=None,
                ),
                db_session
            )
            results.extend(single_result.results)
        
        return ProcessingResult(success=True, results=results)

    async def process_bulk(self, request: BulkBadgeRequest) -> ProcessingResult:
        self.logger.debug(f"Processing bulk posters: {len(request.poster_paths)}")
        
        # Use database session - try session factory first, fall back to engine
        try:
            from app.core.database import async_session_factory
            if async_session_factory is not None:
                async with async_session_factory() as db_session:
                    return await self.process_bulk_with_session(request, db_session)
            else:
                # Fallback to creating session from engine
                from app.core.database import get_engine
                from sqlalchemy.ext.asyncio import AsyncSession
                engine = get_engine()
                async with AsyncSession(engine) as db_session:
                    return await self.process_bulk_with_session(request, db_session)
        except Exception as e:
            self.logger.error(f"Database session error in bulk processing: {e}")
            return ProcessingResult(success=False, results=[], error=f"Database session error: {str(e)}")

    async def auto_select_mode(self, request: UniversalBadgeRequest) -> ProcessingMode:
        if request.bulk_request and len(request.bulk_request.poster_paths) > 5:
            return ProcessingMode.QUEUED
        return ProcessingMode.IMMEDIATE
