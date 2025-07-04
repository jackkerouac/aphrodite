"""
Batch Processing Diagnostics

Tool to diagnose batch job failures by checking:
1. Jellyfin connectivity and configuration
2. Item ID validity and poster availability
3. Database configuration consistency
4. Worker environment setup
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from aphrodite_logging import get_logger
from app.services.jellyfin_service import get_jellyfin_service
from app.core.config import get_settings

logger = get_logger("aphrodite.diagnostics.batch")


class BatchJobDiagnostics:
    """Diagnostic tool for batch processing issues"""
    
    def __init__(self):
        self.jellyfin_service = get_jellyfin_service()
        self.settings = get_settings()
    
    async def run_full_diagnosis(self, job_id: Optional[str] = None, item_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run comprehensive diagnosis of batch processing capabilities
        
        Args:
            job_id: Optional job ID to analyze specific failed job
            item_ids: Optional list of item IDs to test
            
        Returns:
            Detailed diagnostic report
        """
        logger.info("Starting batch processing diagnosis")
        
        diagnosis = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": await self._check_environment(),
            "database": await self._check_database_config(),
            "jellyfin": await self._check_jellyfin_config(),
            "connectivity": await self._check_jellyfin_connectivity(),
            "authentication": await self._check_jellyfin_auth(),
            "item_validation": None,
            "job_analysis": None,
            "recommendations": []
        }
        
        # Test specific item IDs if provided
        if item_ids:
            diagnosis["item_validation"] = await self._validate_item_ids(item_ids)
        
        # Analyze specific job if provided
        if job_id:
            diagnosis["job_analysis"] = await self._analyze_failed_job(job_id)
        
        # Generate recommendations based on findings
        diagnosis["recommendations"] = self._generate_recommendations(diagnosis)
        
        return diagnosis
    
    async def _check_environment(self) -> Dict[str, Any]:
        """Check environment configuration"""
        import os
        import socket
        
        env_info = {
            "is_docker": os.path.exists('/.dockerenv'),
            "hostname": socket.gethostname(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "working_directory": os.getcwd(),
            "environment_type": self.settings.environment,
            "debug_mode": self.settings.debug
        }
        
        # Check for Docker environment variables
        docker_vars = {
            "DOCKER_ENV": os.environ.get("DOCKER_ENV"),
            "POSTGRES_HOST": os.environ.get("POSTGRES_HOST"),
            "POSTGRES_PORT": os.environ.get("POSTGRES_PORT"),
            "POSTGRES_DB": os.environ.get("POSTGRES_DB"),
            "POSTGRES_USER": os.environ.get("POSTGRES_USER")
        }
        env_info["docker_vars"] = {k: v for k, v in docker_vars.items() if v is not None}
        
        return env_info
    
    async def _check_database_config(self) -> Dict[str, Any]:
        """Check database configuration and connectivity"""
        try:
            # Test database connectivity
            from sqlalchemy.ext.asyncio import create_async_engine
            from sqlalchemy import text
            
            database_url = self.settings.get_database_url()
            masked_url = database_url.split('@')[1] if '@' in database_url else 'configuration_hidden'
            
            # Test connection
            test_engine = create_async_engine(database_url, pool_size=1, max_overflow=0)
            
            try:
                async with test_engine.begin() as conn:
                    result = await conn.execute(text("SELECT current_database(), current_user, inet_server_addr(), inet_server_port()"))
                    db_info = result.fetchone()
                
                connection_info = {
                    "status": "connected",
                    "database_name": db_info[0] if db_info else "unknown",
                    "database_user": db_info[1] if db_info else "unknown",
                    "server_address": str(db_info[2]) if db_info and db_info[2] else "localhost",
                    "server_port": db_info[3] if db_info else "unknown",
                    "url_pattern": masked_url
                }
                
                # Check if settings are stored in database
                try:
                    from app.models.config import SystemConfigModel
                    from sqlalchemy import select
                    
                    async with test_engine.begin() as conn:
                        stmt = select(SystemConfigModel).where(SystemConfigModel.key == "settings.yaml")
                        result = await conn.execute(stmt)
                        config_model = result.scalar_one_or_none()
                        
                        connection_info["settings_in_db"] = config_model is not None
                        if config_model:
                            # Check if Jellyfin settings exist
                            settings_data = config_model.value
                            if isinstance(settings_data, str):
                                import yaml
                                settings_data = yaml.safe_load(settings_data)
                            
                            jellyfin_configs = settings_data.get('api_keys', {}).get('Jellyfin', []) if settings_data else []
                            connection_info["jellyfin_configs_count"] = len(jellyfin_configs)
                            
                            if jellyfin_configs:
                                first_config = jellyfin_configs[0]
                                connection_info["jellyfin_url_in_db"] = first_config.get('url', 'not_set')
                                connection_info["jellyfin_has_api_key"] = bool(first_config.get('api_key'))
                                connection_info["jellyfin_has_user_id"] = bool(first_config.get('user_id'))
                        
                except Exception as e:
                    connection_info["settings_check_error"] = str(e)
                
            finally:
                await test_engine.dispose()
            
            return connection_info
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "url_pattern": "connection_failed"
            }
    
    async def _check_jellyfin_config(self) -> Dict[str, Any]:
        """Check Jellyfin service configuration"""
        config_info = {
            "settings_loaded": False,
            "base_url": None,
            "has_api_key": False,
            "has_user_id": False,
            "env_fallback": {
                "jellyfin_url": self.settings.jellyfin_url,
                "has_api_key": bool(self.settings.jellyfin_api_key),
                "has_user_id": bool(self.settings.jellyfin_user_id)
            }
        }
        
        try:
            # Force load settings
            await self.jellyfin_service._load_jellyfin_settings()
            
            config_info.update({
                "settings_loaded": self.jellyfin_service._settings_loaded,
                "base_url": self.jellyfin_service.base_url,
                "has_api_key": bool(self.jellyfin_service.api_key),
                "has_user_id": bool(self.jellyfin_service.user_id)
            })
            
        except Exception as e:
            config_info["load_error"] = str(e)
        
        return config_info
    
    async def _check_jellyfin_connectivity(self) -> Dict[str, Any]:
        """Test Jellyfin server connectivity"""
        try:
            success, message = await self.jellyfin_service.test_connection()
            return {
                "status": "success" if success else "failed",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_jellyfin_auth(self) -> Dict[str, Any]:
        """Test Jellyfin authentication by fetching user info"""
        try:
            # Try to get system info (requires valid auth)
            import aiohttp
            from urllib.parse import urljoin
            
            await self.jellyfin_service._load_jellyfin_settings()
            
            if not self.jellyfin_service.base_url or not self.jellyfin_service.api_key:
                return {
                    "status": "misconfigured",
                    "message": "Missing base URL or API key"
                }
            
            # Test authentication with system info endpoint
            url = urljoin(self.jellyfin_service.base_url, "/System/Info")
            session = await self.jellyfin_service._get_session()
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "authenticated",
                            "server_name": data.get("ServerName", "Unknown"),
                            "version": data.get("Version", "Unknown"),
                            "message": "Authentication successful"
                        }
                    elif response.status == 401:
                        return {
                            "status": "unauthorized",
                            "message": "Invalid API key or expired token"
                        }
                    else:
                        response_text = await response.text()
                        return {
                            "status": "failed",
                            "http_status": response.status,
                            "message": response_text[:200]
                        }
            finally:
                await session.close()
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _validate_item_ids(self, item_ids: List[str]) -> Dict[str, Any]:
        """Validate specific item IDs and check poster availability"""
        validation_results = {
            "total_tested": len(item_ids),
            "valid_items": 0,
            "invalid_items": 0,
            "items_with_posters": 0,
            "items_without_posters": 0,
            "detailed_results": [],
            "errors": []
        }
        
        for item_id in item_ids:
            try:
                # Test item metadata retrieval
                metadata = await self.jellyfin_service.get_item_details(item_id)
                item_result = {
                    "item_id": item_id,
                    "metadata_available": metadata is not None,
                    "poster_available": False,
                    "download_success": False,
                    "error": None
                }
                
                if metadata:
                    validation_results["valid_items"] += 1
                    item_result["item_name"] = metadata.get("Name", "Unknown")
                    item_result["item_type"] = metadata.get("Type", "Unknown")
                    
                    # Test poster availability
                    poster_url = await self.jellyfin_service.get_poster_url(item_id)
                    if poster_url:
                        validation_results["items_with_posters"] += 1
                        item_result["poster_available"] = True
                        
                        # Test poster download
                        poster_data = await self.jellyfin_service.download_poster(item_id)
                        if poster_data:
                            item_result["download_success"] = True
                            item_result["poster_size_bytes"] = len(poster_data)
                        else:
                            item_result["error"] = "Poster download failed"
                    else:
                        validation_results["items_without_posters"] += 1
                        item_result["error"] = "No poster URL available"
                else:
                    validation_results["invalid_items"] += 1
                    item_result["error"] = "Item metadata not found (HTTP 404 or invalid ID)"
                
                validation_results["detailed_results"].append(item_result)
                
            except Exception as e:
                validation_results["invalid_items"] += 1
                validation_results["errors"].append(f"Error testing {item_id}: {str(e)}")
                validation_results["detailed_results"].append({
                    "item_id": item_id,
                    "metadata_available": False,
                    "poster_available": False,
                    "download_success": False,
                    "error": str(e)
                })
        
        return validation_results
    
    async def _analyze_failed_job(self, job_id: str) -> Dict[str, Any]:
        """Analyze a specific failed job"""
        try:
            from app.core.database import async_session_factory
            from app.services.workflow.database import JobRepository
            
            if not async_session_factory:
                return {"error": "Database session factory not available"}
            
            async with async_session_factory() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_job_by_id(job_id)
                
                if not job:
                    return {"error": f"Job {job_id} not found"}
                
                analysis = {
                    "job_id": job_id,
                    "status": job.status,
                    "total_posters": job.total_posters,
                    "completed_posters": job.completed_posters,
                    "failed_posters": job.failed_posters,
                    "badge_types": job.badge_types,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "poster_ids_count": len(job.selected_poster_ids),
                    "sample_poster_ids": job.selected_poster_ids[:5] if job.selected_poster_ids else []
                }
                
                # Test a sample of the poster IDs
                if job.selected_poster_ids:
                    sample_ids = job.selected_poster_ids[:3]  # Test first 3
                    analysis["poster_validation"] = await self._validate_item_ids(sample_ids)
                
                return analysis
                
        except Exception as e:
            return {"error": f"Failed to analyze job: {str(e)}"}
    
    def