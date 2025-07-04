"""
Enhanced Batch Processing Debug Logger

Provides comprehensive logging and diagnostics for batch processing jobs.
Can be enabled/disabled by users to debug Jellyfin connection issues.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp

from aphrodite_logging import get_logger


class BatchDebugLogger:
    """Comprehensive debug logger for batch processing operations"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.logger = get_logger(f"aphrodite.batch.debug.{job_id}")
        
        # Check if debug mode is enabled
        self.debug_enabled = self._is_debug_enabled()
        
        # Debug data storage
        self.session_history: List[Dict[str, Any]] = []
        self.request_timings: List[Dict[str, Any]] = []
        self.session_diagnostics: Dict[str, Any] = {}
        self.jellyfin_environment: Dict[str, Any] = {}
        
        # Performance tracking
        self.start_time = datetime.utcnow()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Debug file paths
        self.debug_dir = Path("E:/programming/aphrodite/api/debug_logs/batch_jobs")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.debug_file = self.debug_dir / f"job_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        if self.debug_enabled:
            self.logger.info(f"🔍 Batch debug logging ENABLED for job {job_id}")
            self.logger.info(f"Debug file: {self.debug_file}")
        else:
            self.logger.debug(f"Batch debug logging disabled for job {job_id}")
    
    def _is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled via environment variable or database setting"""
        # Environment variable check (immediate)
        env_debug = os.environ.get('APHRODITE_BATCH_DEBUG', 'false').lower() == 'true'
        if env_debug:
            return True
        
        # TODO: Add database setting check for per-user debug preferences
        # This would require a user settings table/model
        return False
    
    async def log_session_state(self, jellyfin_service, session: Optional[aiohttp.ClientSession] = None):
        """Log current session state and configuration"""
        if not self.debug_enabled:
            return
        
        try:
            session_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "jellyfin_config": {
                    "base_url": jellyfin_service.base_url,
                    "has_api_key": bool(jellyfin_service.api_key),
                    "user_id": jellyfin_service.user_id,
                    "settings_loaded": jellyfin_service._settings_loaded
                },
                "session_info": {
                    "session_exists": session is not None,
                    "session_closed": session.closed if session else None,
                    "session_connector_info": str(session.connector) if session else None
                },
                "rate_limiting": {
                    "last_request_time": jellyfin_service._last_request_time.isoformat() if jellyfin_service._last_request_time else None,
                    "min_request_interval": jellyfin_service._min_request_interval
                }
            }
            
            self.session_history.append(session_info)
            self.logger.debug(f"📊 Session state: {json.dumps(session_info, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log session state: {e}")
    
    async def log_request_attempt(self, poster_id: str, attempt: int, request_details: Dict[str, Any]):
        """Log detailed request attempt information"""
        if not self.debug_enabled:
            return
        
        try:
            request_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "poster_id": poster_id,
                "attempt": attempt,
                "request_details": request_details,
                "total_requests_so_far": self.total_requests
            }
            
            self.request_timings.append(request_info)
            self.logger.debug(f"🔄 Request attempt {attempt} for {poster_id}: {json.dumps(request_details, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log request attempt: {e}")
    
    async def log_response_analysis(self, poster_id: str, response: aiohttp.ClientResponse, response_data: Optional[bytes] = None):
        """Log detailed response analysis"""
        if not self.debug_enabled:
            return
        
        try:
            self.total_requests += 1
            
            response_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "poster_id": poster_id,
                "status_code": response.status,
                "headers": dict(response.headers),
                "content_length": len(response_data) if response_data else 0,
                "content_type": response.headers.get('content-type', 'unknown'),
                "response_time_ms": 0,  # This would need to be calculated by caller
                "url": str(response.url),
                "method": response.method
            }
            
            # Log success/failure
            if response.status == 200:
                self.successful_requests += 1
                self.logger.debug(f"✅ Successful response for {poster_id}: {response.status}")
            else:
                self.failed_requests += 1
                # For failed requests, capture response body for analysis
                if response.status >= 400:
                    try:
                        error_text = await response.text()
                        response_info["error_body"] = error_text
                        self.logger.error(f"❌ Failed response for {poster_id}: {response.status} - {error_text}")
                    except Exception:
                        self.logger.error(f"❌ Failed response for {poster_id}: {response.status} (could not read body)")
            
            # Store in request timings for analysis
            self.request_timings.append({
                "type": "response",
                **response_info
            })
            
        except Exception as e:
            self.logger.error(f"Failed to log response analysis: {e}")
    
    async def log_session_creation(self, session_type: str, session_details: Dict[str, Any]):
        """Log session creation events"""
        if not self.debug_enabled:
            return
        
        try:
            creation_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_type": session_type,
                "session_details": session_details
            }
            
            self.session_diagnostics[f"creation_{len(self.session_diagnostics)}"] = creation_info
            self.logger.debug(f"🔧 Session creation: {session_type} - {json.dumps(session_details, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log session creation: {e}")
    
    async def log_environment_detection(self, environment_data: Dict[str, Any]):
        """Log Jellyfin environment detection results"""
        if not self.debug_enabled:
            return
        
        try:
            self.jellyfin_environment = {
                "timestamp": datetime.utcnow().isoformat(),
                "detection_results": environment_data
            }
            
            self.logger.info(f"🌍 Jellyfin environment: {json.dumps(environment_data, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log environment detection: {e}")
    
    async def log_poster_processing_start(self, poster_id: str, badge_types: List[str]):
        """Log the start of poster processing"""
        if not self.debug_enabled:
            return
        
        self.logger.info(f"🎯 Starting poster processing: {poster_id} with badges: {badge_types}")
    
    async def log_poster_processing_end(self, poster_id: str, success: bool, error_message: Optional[str] = None):
        """Log the end of poster processing"""
        if not self.debug_enabled:
            return
        
        if success:
            self.logger.info(f"✅ Completed poster processing: {poster_id}")
        else:
            self.logger.error(f"❌ Failed poster processing: {poster_id} - {error_message}")
    
    async def generate_debug_summary(self) -> Dict[str, Any]:
        """Generate comprehensive debug summary"""
        if not self.debug_enabled:
            return {"debug_enabled": False}
        
        try:
            end_time = datetime.utcnow()
            duration = end_time - self.start_time
            
            # Calculate success rate
            success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
            
            # Analyze response patterns
            status_codes = {}
            for timing in self.request_timings:
                if timing.get("type") == "response":
                    status = timing.get("status_code", "unknown")
                    status_codes[status] = status_codes.get(status, 0) + 1
            
            # Analyze failure patterns
            failure_patterns = []
            for timing in self.request_timings:
                if timing.get("type") == "response" and timing.get("status_code", 0) >= 400:
                    failure_patterns.append({
                        "poster_id": timing.get("poster_id"),
                        "status_code": timing.get("status_code"),
                        "error_body": timing.get("error_body", "")[:200]  # Truncate
                    })
            
            summary = {
                "debug_enabled": True,
                "job_id": self.job_id,
                "duration_seconds": duration.total_seconds(),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate_percent": round(success_rate, 2),
                "status_code_breakdown": status_codes,
                "failure_patterns": failure_patterns[:10],  # Top 10 failures
                "session_events": len(self.session_history),
                "jellyfin_environment": self.jellyfin_environment,
                "recommendations": self._generate_recommendations()
            }
            
            # Save to debug file
            await self._save_debug_file(summary)
            
            self.logger.info(f"📋 Debug Summary - Success Rate: {success_rate:.1f}% ({self.successful_requests}/{self.total_requests})")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate debug summary: {e}")
            return {"debug_enabled": True, "error": str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on debug data"""
        recommendations = []
        
        try:
            # Analyze success rate
            if self.total_requests > 0:
                success_rate = (self.successful_requests / self.total_requests) * 100
                
                if success_rate < 50:
                    recommendations.append("Low success rate detected. Consider using individual processing mode.")
                    recommendations.append("Check Jellyfin server logs for potential issues.")
                    
                if success_rate < 80:
                    recommendations.append("Consider increasing request interval to reduce server load.")
                    recommendations.append("Use smaller batch sizes (10-20 items) for better reliability.")
            
            # Analyze failure patterns
            failure_codes = set()
            for timing in self.request_timings:
                if timing.get("type") == "response" and timing.get("status_code", 0) >= 400:
                    failure_codes.add(timing.get("status_code"))
            
            if 400 in failure_codes:
                recommendations.append("HTTP 400 errors detected. Some poster IDs may be invalid or corrupted.")
                recommendations.append("Try running individual processing to identify problematic items.")
            
            if 401 in failure_codes:
                recommendations.append("Authentication failures detected. Check Jellyfin API key configuration.")
            
            if 404 in failure_codes:
                recommendations.append("Items not found. Some media may have been deleted from Jellyfin.")
            
            if 429 in failure_codes or 503 in failure_codes:
                recommendations.append("Rate limiting detected. Increase request interval to 500ms or higher.")
                recommendations.append("Consider using conservative session strategy.")
            
            # Session-based recommendations
            if len(self.session_history) > 10:
                recommendations.append("High session activity detected. Consider using per-request session strategy.")
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Error generating recommendations. Check debug logs for details.")
        
        return recommendations
    
    async def _save_debug_file(self, summary: Dict[str, Any]):
        """Save complete debug data to file"""
        try:
            debug_data = {
                "summary": summary,
                "session_history": self.session_history,
                "request_timings": self.request_timings,
                "session_diagnostics": self.session_diagnostics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            with open(self.debug_file, 'w') as f:
                json.dump(debug_data, f, indent=2, default=str)
            
            self.logger.info(f"💾 Debug data saved to: {self.debug_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save debug file: {e}")
    
    @classmethod
    def enable_debug_mode(cls, duration_minutes: int = 30):
        """Enable debug mode for specified duration"""
        try:
            # Set environment variable for immediate effect
            os.environ['APHRODITE_BATCH_DEBUG'] = 'true'
            
            # Schedule disable after duration
            async def disable_after_timeout():
                await asyncio.sleep(duration_minutes * 60)
                os.environ['APHRODITE_BATCH_DEBUG'] = 'false'
                logger = get_logger("aphrodite.debug")
                logger.info(f"🔍 Debug mode automatically disabled after {duration_minutes} minutes")
            
            # Start the timeout task
            asyncio.create_task(disable_after_timeout())
            
            logger = get_logger("aphrodite.debug")
            logger.info(f"🔍 Debug mode enabled for {duration_minutes} minutes")
            
            return True
            
        except Exception as e:
            logger = get_logger("aphrodite.debug")
            logger.error(f"Failed to enable debug mode: {e}")
            return False
    
    @classmethod
    def disable_debug_mode(cls):
        """Disable debug mode immediately"""
        try:
            os.environ['APHRODITE_BATCH_DEBUG'] = 'false'
            
            logger = get_logger("aphrodite.debug")
            logger.info("🔍 Debug mode disabled")
            
            return True
            
        except Exception as e:
            logger = get_logger("aphrodite.debug")
            logger.error(f"Failed to disable debug mode: {e}")
            return False
    
    @classmethod
    def is_debug_enabled_globally(cls) -> bool:
        """Check if debug mode is currently enabled"""
        return os.environ.get('APHRODITE_BATCH_DEBUG', 'false').lower() == 'true'
