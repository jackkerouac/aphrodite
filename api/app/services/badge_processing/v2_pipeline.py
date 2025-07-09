"""
Updated V2 Badge Pipeline

Entry point updated to use pure V2 processors with clear system differentiation.
"""

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

# Import V2 processors
from .v2_audio_processor import V2AudioBadgeProcessor
from .v2_resolution_processor import V2ResolutionBadgeProcessor
from .v2_review_processor import V2ReviewBadgeProcessor
from .v2_awards_processor import V2AwardsBadgeProcessor


class V2UniversalBadgeProcessor:
    """V2 Universal entry point for badge processing with pure V2 processors"""

    def __init__(self):
        self.logger = get_logger("aphrodite.badge.pipeline.v2", service="badge")
        # Import activity tracker
        from app.services.activity_tracking import get_activity_tracker
        self.activity_tracker = get_activity_tracker()

    async def process_request(self, request: UniversalBadgeRequest) -> ProcessingResult:
        start = time.perf_counter()
        
        self.logger.info("🚀 [V2 PIPELINE] UNIVERSAL BADGE PROCESSOR STARTED")

        if request.processing_mode == ProcessingMode.AUTO:
            mode = await self.auto_select_mode(request)
        else:
            mode = request.processing_mode
        
        self.logger.info(f"🚀 [V2 PIPELINE] Processing mode: {mode}")

        # Use single database session throughout pipeline
        try:
            from app.core.database import async_session_factory
            if async_session_factory is not None:
                async with async_session_factory() as db_session:
                    self.logger.info("🚀 [V2 PIPELINE] Database session established")
                    result = await self._process_with_session(request, mode, db_session)
            else:
                # Fallback to creating session from engine
                from app.core.database import get_engine
                from sqlalchemy.ext.asyncio import AsyncSession
                engine = get_engine()
                async with AsyncSession(engine) as db_session:
                    self.logger.info("🚀 [V2 PIPELINE] Fallback database session established")
                    result = await self._process_with_session(request, mode, db_session)
        except Exception as e:
            self.logger.error(f"❌ [V2 PIPELINE] Database session error: {e}")
            result = ProcessingResult(success=False, results=[], error=f"Database session error: {str(e)}")

        result.processing_time = time.perf_counter() - start
        self.logger.info(f"🚀 [V2 PIPELINE] COMPLETED in {result.processing_time:.2f}s")
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
        self.logger.info(f"🚀 [V2 PIPELINE] PROCESSING SINGLE POSTER: {request.poster_path}")
        
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
                    self.logger.error(f"❌ [V2 PIPELINE] Failed to create database session: {session_error}")
                    raise
            else:
                return await self._process_single_with_session(request, db_session)
                
        except Exception as e:
            self.logger.error(f"❌ [V2 PIPELINE] Error processing single poster: {e}", exc_info=True)
            return ProcessingResult(
                success=False,
                results=[],
                error=str(e)
            )
    
    async def _process_single_with_session(self, request: SingleBadgeRequest, db_session: AsyncSession) -> ProcessingResult:
        """Process single poster with database session using V2 processors"""
        from pathlib import Path
        from .poster_resizer import poster_resizer
        from app.services.poster_management.storage import StorageManager
        
        # Start activity tracking
        activity_id = None
        try:
            # Extract media_id from the poster path or use jellyfin_id
            media_id = request.jellyfin_id or Path(request.poster_path).stem
            
            # Create input parameters for tracking
            input_params = {
                'poster_path': request.poster_path,
                'badge_types': request.badge_types,
                'use_demo_data': request.use_demo_data,
                'output_path': request.output_path,
                'jellyfin_id': request.jellyfin_id
            }
            
            # Start activity tracking
            activity_id = await self.activity_tracker.start_activity(
                media_id=media_id,
                activity_type='badge_application',
                activity_subtype='multi_badge' if len(request.badge_types) > 1 else 'single_badge',
                initiated_by='api_call',
                jellyfin_id=request.jellyfin_id,
                input_parameters=input_params,
                db_session=db_session
            )
            
            self.logger.info(f"🎯 [V2 PIPELINE] Started activity tracking: {activity_id}")
        except Exception as track_error:
            self.logger.warning(f"⚠️ [V2 PIPELINE] Failed to start activity tracking: {track_error}")
        
        # Log what badges are being processed
        self.logger.info(f"🎯 [V2 PIPELINE] PROCESSING BADGES: {request.badge_types}")
        self.logger.info(f"🎯 [V2 PIPELINE] USE_DEMO_DATA: {request.use_demo_data}")
        self.logger.info(f"🎯 [V2 PIPELINE] JELLYFIN_ID: {request.jellyfin_id}")
        
        try:
        
        # Step 1: Resize poster to standard 1,000px width
        self.logger.info(f"📏 [V2 PIPELINE] Resizing poster: {request.poster_path}")
        resized_poster_path = poster_resizer.resize_poster(request.poster_path)
        
        if not resized_poster_path:
            self.logger.error(f"❌ [V2 PIPELINE] Failed to resize poster: {request.poster_path}")
            return ProcessingResult(
                success=False,
                results=[],
                error="Failed to resize poster to standard dimensions"
            )
        
        self.logger.info(f"✅ [V2 PIPELINE] Poster resized: {resized_poster_path}")
        
        # Step 2: Initialize V2 badge processors
        processors = {
            "audio": V2AudioBadgeProcessor(),
            "resolution": V2ResolutionBadgeProcessor(),
            "review": V2ReviewBadgeProcessor(),
            "awards": V2AwardsBadgeProcessor()
        }
        
        # Start with the resized poster
        current_poster_path = resized_poster_path
        applied_badges = []
        
        self.logger.info(f"🔄 [V2 PIPELINE] Processing badges: {request.badge_types}")
        
        # Apply badges sequentially
        for i, badge_type in enumerate(request.badge_types):
            processor = processors.get(badge_type)
            if not processor:
                self.logger.warning(f"⚠️ [V2 PIPELINE] Unknown badge type: {badge_type}, skipping")
                continue
            
            self.logger.info(f"🔄 [V2 PIPELINE] STARTING {badge_type.upper()} PROCESSOR ({i+1}/{len(request.badge_types)})")
            self.logger.info(f"🔄 [V2 PIPELINE] Current poster: {current_poster_path}")
            
            # For the last badge, use the final output path if specified
            is_last_badge = (i == len(request.badge_types) - 1)
            output_path = request.output_path if is_last_badge and request.output_path else None
            
            self.logger.info(f"🔄 [V2 PIPELINE] Output path for {badge_type}: {output_path}")
            
            # Process with the specific badge processor
            try:
                result = await processor.process_single(
                    current_poster_path,
                    output_path,
                    request.use_demo_data,
                    db_session,
                    request.jellyfin_id
                )
                
                self.logger.info(f"✅ [V2 PIPELINE] {badge_type.upper()} PROCESSOR COMPLETED")
            except Exception as processor_error:
                self.logger.error(f"🚨 [V2 PIPELINE] {badge_type.upper()} PROCESSOR FAILED: {processor_error}", exc_info=True)
                # Continue processing other badges even if one fails
                self.logger.warning(f"⚠️ [V2 PIPELINE] Continuing with remaining badges despite {badge_type} failure")
                # Create a failed result to continue processing
                result = PosterResult(
                    source_path=current_poster_path,
                    output_path=current_poster_path,
                    applied_badges=[],
                    success=False,
                    error=f"{badge_type} processor exception: {str(processor_error)}"
                )
            
            self.logger.info(f"📊 [V2 PIPELINE] {badge_type} result - Success: {result.success}, Applied: {result.applied_badges}")
            
            if result.success:
                self.logger.info(f"✅ [V2 PIPELINE] {badge_type} SUCCESS: {current_poster_path} -> {result.output_path}")
                current_poster_path = result.output_path
                applied_badges.extend(result.applied_badges)
            else:
                self.logger.error(f"❌ [V2 PIPELINE] {badge_type} FAILED: {result.error}")
                # Continue with other badges even if one fails
                self.logger.info(f"🔄 [V2 PIPELINE] Continuing to next processor despite {badge_type} failure")
        
        # Handle final output path
        storage_manager = StorageManager()
        
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
                    self.logger.info(f"🔧 [V2 PIPELINE] Renamed to proper preview path: {final_output_path}")
                except Exception as e:
                    self.logger.warning(f"⚠️ [V2 PIPELINE] Failed to rename to preview path: {e}")
                    final_output_path = current_poster_path
            else:
                final_output_path = current_poster_path
            
            final_result = PosterResult(
                source_path=request.poster_path,
                output_path=final_output_path,
                applied_badges=applied_badges,
                success=True
            )
            self.logger.info(f"✅ [V2 PIPELINE] SUCCESSFULLY PROCESSED with {len(applied_badges)} badges: {final_output_path}")
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
                self.logger.info(f"🔧 [V2 PIPELINE] No badges applied, created proper preview path: {final_output_path}")
                
            except Exception as e:
                self.logger.error(f"❌ [V2 PIPELINE] Error creating proper preview path: {e}")
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
                        self.logger.debug(f"🧹 [V2 PIPELINE] Cleaned up temporary resized poster: {resized_poster_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ [V2 PIPELINE] Failed to clean up temporary poster: {e}")
            
            # Complete activity tracking on success
            if activity_id:
                try:
                    result_data = {
                        'output_path': final_result.output_path,
                        'applied_badges': final_result.applied_badges,
                        'source_path': final_result.source_path
                    }
                    await self.activity_tracker.complete_activity(
                        activity_id=activity_id,
                        success=True,
                        result_data=result_data,
                        db_session=db_session
                    )
                    self.logger.info(f"✅ [V2 PIPELINE] Completed activity tracking: {activity_id}")
                except Exception as track_error:
                    self.logger.warning(f"⚠️ [V2 PIPELINE] Failed to complete activity tracking: {track_error}")
            
            return ProcessingResult(success=True, results=[final_result])
            
        except Exception as processing_error:
            self.logger.error(f"❌ [V2 PIPELINE] Processing failed: {processing_error}", exc_info=True)
            
            # Complete activity tracking on failure
            if activity_id:
                try:
                    await self.activity_tracker.fail_activity(
                        activity_id=activity_id,
                        error_message=str(processing_error),
                        db_session=db_session
                    )
                    self.logger.info(f"❌ [V2 PIPELINE] Failed activity tracking: {activity_id}")
                except Exception as track_error:
                    self.logger.warning(f"⚠️ [V2 PIPELINE] Failed to track failure: {track_error}")
            
            # Return failed result
            return ProcessingResult(
                success=False,
                results=[],
                error=str(processing_error)
            )

    async def process_bulk_with_session(self, request: BulkBadgeRequest, db_session: AsyncSession) -> ProcessingResult:
        """Process bulk with existing database session"""
        self.logger.info(f"🚀 [V2 PIPELINE] BULK PROCESSING {len(request.poster_paths)} posters")
        results: List[PosterResult] = []
        
        for i, path in enumerate(request.poster_paths):
            self.logger.info(f"🔄 [V2 PIPELINE] BULK ITEM {i+1}/{len(request.poster_paths)}: {path}")
            
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
            
            # Log bulk progress
            if (i + 1) % 5 == 0:
                successful = sum(1 for r in results if r.success)
                self.logger.info(f"📊 [V2 PIPELINE] BULK PROGRESS: {successful}/{len(results)} successful so far")
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"✅ [V2 PIPELINE] BULK COMPLETED: {successful}/{len(results)} successful")
        
        return ProcessingResult(success=True, results=results)

    async def process_bulk(self, request: BulkBadgeRequest) -> ProcessingResult:
        self.logger.info(f"🚀 [V2 PIPELINE] BULK PROCESSING {len(request.poster_paths)} posters")
        
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
            self.logger.error(f"❌ [V2 PIPELINE] Database session error in bulk processing: {e}")
            return ProcessingResult(success=False, results=[], error=f"Database session error: {str(e)}")

    async def auto_select_mode(self, request: UniversalBadgeRequest) -> ProcessingMode:
        if request.bulk_request and len(request.bulk_request.poster_paths) > 5:
            return ProcessingMode.QUEUED
        return ProcessingMode.IMMEDIATE


# Backward compatibility - keep old class name but use V2 implementation
class UniversalBadgeProcessor(V2UniversalBadgeProcessor):
    """Backward compatibility wrapper for V2 processor"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("⚠️ [COMPATIBILITY] Using V2 processor through backward compatibility wrapper")
