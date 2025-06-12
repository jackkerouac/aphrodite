"""
Batch Badge Processor

Handles bulk badge processing with progress tracking and error recovery.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from dataclasses import dataclass

from aphrodite_logging import get_logger
from .types import PosterResult
from .audio_processor import AudioBadgeProcessor
from .resolution_processor import ResolutionBadgeProcessor
from .review_processor import ReviewBadgeProcessor
from .awards_processor import AwardsBadgeProcessor


@dataclass
class BatchProgress:
    """Progress tracking for batch operations"""
    total: int
    completed: int
    successful: int
    failed: int
    current_poster: Optional[str] = None
    
    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0


class BatchBadgeProcessor:
    """Handles bulk badge processing operations"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.badge.batch", service="badge")
        
        # Initialize individual processors
        self.processors = {
            "audio": AudioBadgeProcessor(),
            "resolution": ResolutionBadgeProcessor(),
            "review": ReviewBadgeProcessor(),
            "awards": AwardsBadgeProcessor()
        }
    
    async def process_batch(
        self,
        poster_paths: List[str],
        badge_types: List[str],
        output_directory: Optional[str] = None,
        use_demo_data: bool = False,
        batch_size: int = 10,
        progress_callback: Optional[callable] = None
    ) -> List[PosterResult]:
        """Process multiple posters with selected badge types"""
        
        total_posters = len(poster_paths)
        self.logger.info(f"Starting batch processing: {total_posters} posters, badges: {badge_types}")
        
        # Initialize progress tracking
        progress = BatchProgress(
            total=total_posters,
            completed=0,
            successful=0,
            failed=0
        )
        
        # Process posters in batches to avoid overwhelming the system
        all_results = []
        
        for i in range(0, total_posters, batch_size):
            batch_posters = poster_paths[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_posters + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_posters)} posters)")
            
            # Process batch
            batch_results = await self._process_poster_batch(
                batch_posters, badge_types, output_directory, use_demo_data, progress, progress_callback
            )
            
            all_results.extend(batch_results)
            
            # Update progress
            progress.completed += len(batch_posters)
            progress.successful += sum(1 for r in batch_results if r.success)
            progress.failed += sum(1 for r in batch_results if not r.success)
            
            # Call progress callback
            if progress_callback:
                try:
                    await progress_callback(progress)
                except Exception as e:
                    self.logger.warning(f"Progress callback failed: {e}")
            
            # Small delay between batches to prevent overwhelming
            if i + batch_size < total_posters:
                await asyncio.sleep(0.1)
        
        self.logger.info(
            f"Batch processing complete: {progress.successful}/{progress.total} successful, "
            f"{progress.failed} failed"
        )
        
        return all_results
    
    async def _process_poster_batch(
        self,
        poster_paths: List[str],
        badge_types: List[str],
        output_directory: Optional[str],
        use_demo_data: bool,
        progress: BatchProgress,
        progress_callback: Optional[callable] = None
    ) -> List[PosterResult]:
        """Process a single batch of posters"""
        
        results = []
        
        for poster_path in poster_paths:
            progress.current_poster = Path(poster_path).name
            
            try:
                # Process single poster with all selected badge types
                poster_result = await self._process_single_poster_all_badges(
                    poster_path, badge_types, output_directory, use_demo_data
                )
                results.append(poster_result)
                
                # Log individual poster results
                if poster_result.success:
                    self.logger.debug(f"✅ Processed: {poster_path} - badges: {poster_result.applied_badges}")
                else:
                    self.logger.warning(f"❌ Failed: {poster_path} - error: {poster_result.error}")
                
            except Exception as e:
                self.logger.error(f"Error processing poster {poster_path}: {e}", exc_info=True)
                results.append(PosterResult(
                    source_path=poster_path,
                    success=False,
                    error=f"Batch processing error: {str(e)}"
                ))
        
        return results
    
    async def _process_single_poster_all_badges(
        self,
        poster_path: str,
        badge_types: List[str],
        output_directory: Optional[str],
        use_demo_data: bool
    ) -> PosterResult:
        """Apply all selected badge types to a single poster"""
        
        current_poster_path = poster_path
        applied_badges = []
        
        # Calculate final output path
        output_path = None
        if output_directory:
            poster_name = Path(poster_path).name
            output_path = str(Path(output_directory) / poster_name)
        
        try:
            # Apply badges sequentially to avoid conflicts
            for badge_type in badge_types:
                if badge_type not in self.processors:
                    self.logger.warning(f"Unknown badge type: {badge_type}")
                    continue
                
                processor = self.processors[badge_type]
                
                # For sequential badge application, use the result of the previous badge as input
                # For the final badge, use the specified output path
                next_output_path = output_path if badge_type == badge_types[-1] else None
                
                result = await processor.process_single(
                    current_poster_path, next_output_path, use_demo_data
                )
                
                if result.success and result.output_path:
                    current_poster_path = result.output_path
                    applied_badges.append(badge_type)
                    self.logger.debug(f"Applied {badge_type} badge: {result.output_path}")
                else:
                    self.logger.warning(f"Failed to apply {badge_type} badge: {result.error}")
                    # Continue with other badges even if one fails
            
            # Return final result
            return PosterResult(
                source_path=poster_path,
                output_path=current_poster_path if applied_badges else poster_path,
                applied_badges=applied_badges,
                success=len(applied_badges) > 0
            )
            
        except Exception as e:
            self.logger.error(f"Error applying badges to {poster_path}: {e}", exc_info=True)
            return PosterResult(
                source_path=poster_path,
                success=False,
                error=str(e)
            )
    
    async def validate_batch_input(
        self,
        poster_paths: List[str],
        badge_types: List[str]
    ) -> Dict[str, Any]:
        """Validate batch processing input"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "valid_posters": [],
            "invalid_posters": [],
            "valid_badge_types": [],
            "invalid_badge_types": []
        }
        
        # Validate badge types
        for badge_type in badge_types:
            if badge_type in self.processors:
                validation_result["valid_badge_types"].append(badge_type)
            else:
                validation_result["invalid_badge_types"].append(badge_type)
                validation_result["errors"].append(f"Invalid badge type: {badge_type}")
        
        # Validate poster paths
        for poster_path in poster_paths:
            try:
                path = Path(poster_path)
                if path.exists() and path.is_file():
                    # Check if it's a valid image extension
                    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
                    if path.suffix.lower() in valid_extensions:
                        validation_result["valid_posters"].append(poster_path)
                    else:
                        validation_result["invalid_posters"].append(poster_path)
                        validation_result["warnings"].append(f"Invalid image extension: {poster_path}")
                else:
                    validation_result["invalid_posters"].append(poster_path)
                    validation_result["errors"].append(f"File not found: {poster_path}")
                    
            except Exception as e:
                validation_result["invalid_posters"].append(poster_path)
                validation_result["errors"].append(f"Error validating {poster_path}: {str(e)}")
        
        # Set overall validity
        if validation_result["errors"] or not validation_result["valid_posters"] or not validation_result["valid_badge_types"]:
            validation_result["valid"] = False
        
        return validation_result
    
    def estimate_processing_time(
        self,
        poster_count: int,
        badge_types: List[str]
    ) -> float:
        """Estimate total processing time for batch operation"""
        
        # Base time estimates per badge type (in seconds)
        badge_time_estimates = {
            "audio": 2.0,
            "resolution": 2.0,
            "review": 5.0,  # More complex due to multiple reviews
            "awards": 3.0
        }
        
        # Calculate time per poster
        time_per_poster = sum(badge_time_estimates.get(badge_type, 2.0) for badge_type in badge_types)
        
        # Add overhead for batch processing
        overhead_factor = 1.2  # 20% overhead
        
        total_time = poster_count * time_per_poster * overhead_factor
        
        self.logger.debug(f"Estimated processing time: {total_time:.1f}s for {poster_count} posters with {len(badge_types)} badge types")
        
        return total_time
