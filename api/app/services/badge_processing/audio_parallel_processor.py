"""
Handles parallel processing of TV series episodes for audio detection.
Direct adaptation of successful ParallelResolutionProcessor.
"""

import asyncio
from typing import List, Optional, Dict, Any
from collections import Counter
from aphrodite_logging import get_logger

from .audio_types import AudioInfo
from .audio_detector import EnhancedAudioDetector


class ParallelAudioProcessor:
    """
    Handles parallel processing of TV series episodes for audio detection.
    Direct adaptation of successful ParallelResolutionProcessor.
    """
    
    def __init__(self, detector: Optional[EnhancedAudioDetector] = None):
        self.logger = get_logger("aphrodite.audio.parallel", service="badge")
        self.detector = detector or EnhancedAudioDetector()
        
        # Configuration (same as resolution processor)
        self.max_concurrent_requests = 5
        self.default_episode_sample_size = 5
        self.timeout_per_episode = 10.0  # seconds
    
    async def get_series_audio_parallel(self, 
                                      jellyfin_service,
                                      series_id: str,
                                      max_episodes: int = 5) -> Optional[AudioInfo]:
        """
        Get series audio by processing episodes in parallel.
        Mirror of get_series_resolution_parallel() success pattern.
        """
        try:
            start_time = asyncio.get_event_loop().time()
            self.logger.debug(f"Starting parallel audio processing for series: {series_id}")
            
            # Get episode list
            episodes = await jellyfin_service.get_series_episodes(series_id, limit=max_episodes)
            if not episodes:
                self.logger.warning(f"No episodes found for series: {series_id}")
                return None
            
            # Limit episodes to process
            episodes_to_process = episodes[:max_episodes]
            self.logger.debug(f"Processing {len(episodes_to_process)} episodes in parallel")
            
            # Create semaphore for concurrent requests
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            # Process episodes in parallel
            tasks = [
                self._process_episode_audio(semaphore, jellyfin_service, episode, i)
                for i, episode in enumerate(episodes_to_process)
            ]
            
            # Wait for all tasks with timeout
            try:
                audio_results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout_per_episode * len(episodes_to_process)
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Parallel audio processing timeout for series: {series_id}")
                return None
            
            # Filter successful results
            valid_audio_infos = []
            for i, result in enumerate(audio_results):
                if isinstance(result, Exception):
                    self.logger.warning(f"Episode {i} audio processing failed: {result}")
                elif isinstance(result, AudioInfo):
                    valid_audio_infos.append(result)
            
            if not valid_audio_infos:
                self.logger.warning(f"No valid audio info extracted from {len(episodes_to_process)} episodes")
                return None
            
            # Determine dominant audio format
            dominant_audio = self._determine_dominant_audio(valid_audio_infos)
            
            end_time = asyncio.get_event_loop().time()
            processing_time = int((end_time - start_time) * 1000)
            
            self.logger.debug(f"Parallel audio processing completed in {processing_time}ms")
            self.logger.debug(f"Processed {len(valid_audio_infos)}/{len(episodes_to_process)} episodes successfully")
            self.logger.debug(f"Dominant audio: {dominant_audio}")
            
            return dominant_audio
            
        except Exception as e:
            self.logger.error(f"Parallel audio processing error: {e}", exc_info=True)
            return None
    
    async def _process_episode_audio(self, 
                                   semaphore: asyncio.Semaphore,
                                   jellyfin_service,
                                   episode: Dict[str, Any],
                                   episode_index: int) -> Optional[AudioInfo]:
        """Process single episode audio with semaphore control"""
        async with semaphore:
            try:
                episode_id = episode.get('Id')
                if not episode_id:
                    return None
                
                # Get episode details
                episode_details = await jellyfin_service.get_item_details(episode_id)
                if not episode_details:
                    return None
                
                # Extract audio info
                audio_info = self.detector.extract_audio_info(episode_details)
                
                if audio_info:
                    self.logger.debug(f"Episode {episode_index + 1} audio: {audio_info}")
                
                return audio_info
                
            except Exception as e:
                self.logger.warning(f"Episode {episode_index + 1} audio error: {e}")
                return None
    
    def _determine_dominant_audio(self, audio_infos: List[AudioInfo]) -> AudioInfo:
        """Determine dominant audio format from multiple episodes"""
        if len(audio_infos) == 1:
            return audio_infos[0]
        
        # Count audio formats
        format_counter = Counter()
        codec_counter = Counter()
        
        for audio_info in audio_infos:
            format_counter[audio_info.format] += 1
            codec_counter[audio_info.codec] += 1
        
        # Get most common format and codec
        dominant_format = format_counter.most_common(1)[0][0]
        dominant_codec = codec_counter.most_common(1)[0][0]
        
        # Find the first audio_info that matches the dominant format
        for audio_info in audio_infos:
            if audio_info.format == dominant_format:
                # Update codec to be the most common one
                audio_info.codec = dominant_codec
                return audio_info
        
        # Fallback to first audio info
        return audio_infos[0]
