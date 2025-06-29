"""
Parallel processing for TV series resolution detection.
Improves performance by processing episodes concurrently.
"""

import asyncio
from typing import List, Optional, Dict, Any
from collections import Counter
from aphrodite_logging import get_logger

from .resolution_types import ResolutionInfo
from .resolution_detector import EnhancedResolutionDetector


class ParallelResolutionProcessor:
    """
    Handles parallel processing of TV series episodes for resolution detection.
    Provides significant performance improvements for series with many episodes.
    """
    
    def __init__(self, detector: Optional[EnhancedResolutionDetector] = None):
        self.logger = get_logger("aphrodite.resolution.parallel", service="badge")
        self.detector = detector or EnhancedResolutionDetector()
        
        # Configuration
        self.max_concurrent_requests = 5
        self.default_episode_sample_size = 5
        self.timeout_per_episode = 10.0  # seconds
    
    async def get_series_resolution_parallel(
        self, 
        jellyfin_service,
        series_id: str,
        max_episodes: int = 5
    ) -> Optional[ResolutionInfo]:
        """
        Get series resolution by processing episodes in parallel.
        
        Args:
            jellyfin_service: Jellyfin service instance
            series_id: Series ID to analyze
            max_episodes: Maximum episodes to sample
            
        Returns:
            Dominant resolution info across sampled episodes
        """
        try:
            self.logger.debug(f"Starting parallel resolution analysis for series: {series_id}")
            
            # Get series episodes
            episodes = await jellyfin_service.get_series_episodes(series_id, limit=max_episodes * 2)
            
            if not episodes:
                self.logger.warning(f"No episodes found for series: {series_id}")
                return self._get_default_resolution()
            
            # Sample episodes strategically
            sampled_episodes = self._sample_episodes_strategically(episodes, max_episodes)
            
            self.logger.debug(f"Sampled {len(sampled_episodes)} episodes for analysis")
            
            # Process episodes in parallel
            resolution_results = await self._process_episodes_parallel(
                jellyfin_service, sampled_episodes
            )
            
            # Determine dominant resolution
            dominant_resolution = self._find_dominant_resolution(resolution_results)
            
            if dominant_resolution:
                self.logger.info(f"Series resolution determined: {dominant_resolution}")
            else:
                self.logger.warning(f"Could not determine series resolution, using default")
                dominant_resolution = self._get_default_resolution()
            
            return dominant_resolution
            
        except Exception as e:
            self.logger.error(f"Parallel resolution processing error: {e}", exc_info=True)
            return self._get_default_resolution()
    
    def _sample_episodes_strategically(self, episodes: List[Dict], max_episodes: int) -> List[Dict]:
        """
        Sample episodes strategically to get representative resolution data.
        Takes episodes from different parts of the series for better accuracy.
        """
        if len(episodes) <= max_episodes:
            return episodes
        
        # Strategy: Take episodes from beginning, middle, and end
        total_episodes = len(episodes)
        
        if max_episodes == 1:
            # Take the first episode
            return [episodes[0]]
        elif max_episodes == 2:
            # Take first and last
            return [episodes[0], episodes[-1]]
        elif max_episodes <= 5:
            # Distribute across the series
            indices = []
            for i in range(max_episodes):
                index = int((i / (max_episodes - 1)) * (total_episodes - 1))
                indices.append(index)
            
            return [episodes[i] for i in indices]
        else:
            # For larger samples, take more from the beginning (most likely to be consistent)
            beginning_count = max_episodes // 2
            middle_count = max_episodes // 4
            end_count = max_episodes - beginning_count - middle_count
            
            sampled = []
            sampled.extend(episodes[:beginning_count])
            
            if middle_count > 0:
                middle_start = total_episodes // 3
                middle_end = middle_start + middle_count
                sampled.extend(episodes[middle_start:middle_end])
            
            if end_count > 0:
                sampled.extend(episodes[-end_count:])
            
            return sampled
    
    async def _process_episodes_parallel(
        self, 
        jellyfin_service,
        episodes: List[Dict]
    ) -> List[Optional[ResolutionInfo]]:
        """Process multiple episodes concurrently with proper error handling"""
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Create tasks for parallel processing
        tasks = [
            self._process_single_episode_with_semaphore(
                semaphore, jellyfin_service, episode, i
            )
            for i, episode in enumerate(episodes)
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        resolution_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Episode {i+1} processing failed: {result}")
            elif result is not None:
                resolution_results.append(result)
        
        self.logger.debug(f"Successfully processed {len(resolution_results)} out of {len(episodes)} episodes")
        
        return resolution_results
    
    async def _process_single_episode_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        jellyfin_service,
        episode: Dict,
        episode_index: int
    ) -> Optional[ResolutionInfo]:
        """Process a single episode with semaphore control and timeout"""
        
        async with semaphore:
            try:
                # Add timeout to prevent hanging
                return await asyncio.wait_for(
                    self._process_single_episode(jellyfin_service, episode, episode_index),
                    timeout=self.timeout_per_episode
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Episode {episode_index+1} processing timed out")
                return None
            except Exception as e:
                self.logger.warning(f"Episode {episode_index+1} processing error: {e}")
                return None
    
    async def _process_single_episode(
        self,
        jellyfin_service,
        episode: Dict,
        episode_index: int
    ) -> Optional[ResolutionInfo]:
        """Process a single episode to extract resolution info"""
        
        try:
            episode_id = episode.get('Id')
            if not episode_id:
                return None
            
            # Get detailed episode information
            episode_details = await jellyfin_service.get_media_item_by_id(episode_id)
            if not episode_details:
                return None
            
            # Extract resolution using enhanced detector
            resolution_info = self.detector.extract_resolution_info(episode_details)
            
            if resolution_info:
                self.logger.debug(f"Episode {episode_index+1}: {resolution_info}")
            
            return resolution_info
            
        except Exception as e:
            self.logger.warning(f"Episode {episode_index+1} detail processing error: {e}")
            return None
    
    def _find_dominant_resolution(self, resolution_results: List[ResolutionInfo]) -> Optional[ResolutionInfo]:
        """
        Determine the most common resolution across episodes.
        Uses weighted scoring to handle mixed-resolution series intelligently.
        """
        if not resolution_results:
            return None
        
        if len(resolution_results) == 1:
            return resolution_results[0]
        
        # Count resolutions by string representation
        resolution_counts = Counter(str(res) for res in resolution_results)
        
        # Find the most common resolution
        most_common_str = resolution_counts.most_common(1)[0][0]
        
        # Find the corresponding ResolutionInfo object
        for resolution_info in resolution_results:
            if str(resolution_info) == most_common_str:
                self.logger.debug(f"Dominant resolution: {most_common_str} ({resolution_counts[most_common_str]}/{len(resolution_results)} episodes)")
                return resolution_info
        
        # Fallback to first result
        return resolution_results[0]
    
    def _get_default_resolution(self) -> ResolutionInfo:
        """Get default resolution for series when detection fails"""
        from .resolution_types import ResolutionInfo
        
        return ResolutionInfo(
            height=1080,
            width=1920,
            base_resolution="1080p",
            is_hdr=False,
            is_dolby_vision=False,
            is_hdr_plus=False
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring"""
        return {
            "max_concurrent_requests": self.max_concurrent_requests,
            "default_episode_sample_size": self.default_episode_sample_size,
            "timeout_per_episode": self.timeout_per_episode
        }
    
    def update_performance_settings(
        self,
        max_concurrent: Optional[int] = None,
        sample_size: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        """Update performance settings for optimization"""
        if max_concurrent is not None:
            self.max_concurrent_requests = max(1, min(10, max_concurrent))
            
        if sample_size is not None:
            self.default_episode_sample_size = max(1, min(20, sample_size))
            
        if timeout is not None:
            self.timeout_per_episode = max(5.0, min(30.0, timeout))
        
        self.logger.info(f"Performance settings updated: concurrent={self.max_concurrent_requests}, "
                        f"sample_size={self.default_episode_sample_size}, timeout={self.timeout_per_episode}")
