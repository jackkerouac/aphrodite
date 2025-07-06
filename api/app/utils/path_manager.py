"""
Path Management Utility

Centralizes path validation, creation, and health checks for Docker volume usage.
Created as part of storage consolidation validation.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import tempfile

from app.core.config import get_settings
from aphrodite_logging import get_logger


class PathManager:
    """Utility for managing and validating Docker volume paths"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("aphrodite.utils.path_manager", service="path")
        
    def get_all_configured_paths(self) -> Dict[str, str]:
        """Get all configured paths from settings"""
        return {
            "data_dir": self.settings.data_dir,
            "logs_dir": self.settings.logs_dir,
            "media_dir": self.settings.media_dir,
            "cache_dir": self.settings.cache_dir,
            "config_dir": self.settings.config_dir,
            "temp_dir": self.settings.temp_dir,
            "preview_dir": self.settings.preview_dir,
            "processed_dir": self.settings.processed_dir,
            "static_originals_dir": self.settings.static_originals_dir
        }
    
    def validate_paths(self) -> Dict[str, Any]:
        """Validate all configured paths and check Docker volume usage"""
        paths = self.get_all_configured_paths()
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "paths": {},
            "overall_status": "unknown",
            "docker_volume_usage": {},
            "issues": []
        }
        
        for path_name, path_value in paths.items():
            result = self._validate_single_path(path_name, path_value)
            validation_results["paths"][path_name] = result
            
            if not result["valid"]:
                validation_results["issues"].append(f"{path_name}: {result['error']}")
        
        # Check Docker volume usage
        validation_results["docker_volume_usage"] = self._check_docker_volume_usage()
        
        # Determine overall status
        all_valid = all(p["valid"] for p in validation_results["paths"].values())
        validation_results["overall_status"] = "healthy" if all_valid else "issues_found"
        
        return validation_results
    
    def _validate_single_path(self, path_name: str, path_value: str) -> Dict[str, Any]:
        """Validate a single path"""
        result = {
            "path": path_value,
            "valid": False,
            "exists": False,
            "writable": False,
            "docker_volume": False,
            "error": None,
            "info": {}
        }
        
        try:
            path_obj = Path(path_value)
            
            # Check if path exists
            result["exists"] = path_obj.exists()
            
            # Check if it's in a Docker volume path
            result["docker_volume"] = str(path_obj).startswith("/app/")
            
            # Create directory if it doesn't exist
            if not result["exists"]:
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    result["exists"] = True
                    result["info"]["created"] = True
                    self.logger.info(f"Created missing directory: {path_value}")
                except Exception as e:
                    result["error"] = f"Cannot create directory: {e}"
                    return result
            
            # Check if writable
            try:
                test_file = path_obj / f".write_test_{datetime.now().timestamp()}"
                test_file.write_text("test")
                test_file.unlink()
                result["writable"] = True
            except Exception as e:
                result["error"] = f"Path not writable: {e}"
                return result
            
            # Get path statistics
            try:
                stat = path_obj.stat()
                result["info"]["size_mb"] = round(stat.st_size / 1024 / 1024, 2) if path_obj.is_file() else "N/A"
                result["info"]["permissions"] = oct(stat.st_mode)[-3:]
                
                # Count files in directory
                if path_obj.is_dir():
                    file_count = len(list(path_obj.iterdir()))
                    result["info"]["file_count"] = file_count
            except Exception:
                pass  # Statistics are optional
            
            result["valid"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _check_docker_volume_usage(self) -> Dict[str, Any]:
        """Check if paths are actually using Docker volumes"""
        volume_info = {
            "volumes_detected": [],
            "volume_mounts": {},
            "analysis": {}
        }
        
        try:
            # Check if we're in a Docker container
            is_docker = os.path.exists('/.dockerenv')
            volume_info["in_docker_container"] = is_docker
            
            if is_docker:
                # Try to detect volume mounts by checking /proc/mounts
                try:
                    with open('/proc/mounts', 'r') as f:
                        mounts = f.read()
                    
                    # Look for volume mounts that match our paths
                    for line in mounts.split('\n'):
                        parts = line.split()
                        if len(parts) >= 2:
                            mount_point = parts[1]
                            if mount_point.startswith('/app/'):
                                volume_info["volumes_detected"].append(mount_point)
                                volume_info["volume_mounts"][mount_point] = parts[0]
                except Exception as e:
                    volume_info["mount_detection_error"] = str(e)
            
            # Analyze which configured paths are using volumes
            paths = self.get_all_configured_paths()
            for path_name, path_value in paths.items():
                is_volume_path = any(path_value.startswith(vol) for vol in volume_info["volumes_detected"])
                volume_info["analysis"][path_name] = {
                    "path": path_value,
                    "uses_volume": is_volume_path,
                    "volume_mount": next((vol for vol in volume_info["volumes_detected"] if path_value.startswith(vol)), None)
                }
        
        except Exception as e:
            volume_info["error"] = str(e)
        
        return volume_info
    
    def create_all_directories(self) -> Dict[str, Any]:
        """Ensure all configured directories exist"""
        paths = self.get_all_configured_paths()
        results = {
            "created": [],
            "already_existed": [],
            "failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for path_name, path_value in paths.items():
            try:
                path_obj = Path(path_value)
                
                if path_obj.exists():
                    results["already_existed"].append(path_name)
                else:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    results["created"].append(path_name)
                    self.logger.info(f"Created directory for {path_name}: {path_value}")
                    
            except Exception as e:
                results["failed"].append({
                    "path_name": path_name,
                    "path_value": path_value,
                    "error": str(e)
                })
                self.logger.error(f"Failed to create directory for {path_name} ({path_value}): {e}")
        
        return results
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test basic file operations in each configured directory"""
        paths = self.get_all_configured_paths()
        results = {
            "tests": {},
            "overall_success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        for path_name, path_value in paths.items():
            test_result = {
                "path": path_value,
                "write_test": False,
                "read_test": False,
                "delete_test": False,
                "error": None
            }
            
            try:
                path_obj = Path(path_value)
                
                # Ensure directory exists
                path_obj.mkdir(parents=True, exist_ok=True)
                
                # Test file operations
                test_filename = f"path_test_{datetime.now().timestamp()}.txt"
                test_file = path_obj / test_filename
                test_content = f"Path test for {path_name} at {datetime.now()}"
                
                # Write test
                test_file.write_text(test_content)
                test_result["write_test"] = True
                
                # Read test
                read_content = test_file.read_text()
                test_result["read_test"] = read_content == test_content
                
                # Delete test
                test_file.unlink()
                test_result["delete_test"] = not test_file.exists()
                
                if not all([test_result["write_test"], test_result["read_test"], test_result["delete_test"]]):
                    results["overall_success"] = False
                    
            except Exception as e:
                test_result["error"] = str(e)
                results["overall_success"] = False
                self.logger.error(f"File operation test failed for {path_name}: {e}")
            
            results["tests"][path_name] = test_result
        
        return results
    
    def get_path_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about configured paths"""
        paths = self.get_all_configured_paths()
        stats = {
            "paths": {},
            "summary": {
                "total_paths": len(paths),
                "existing_paths": 0,
                "total_files": 0,
                "total_size_mb": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        for path_name, path_value in paths.items():
            path_stats = {
                "path": path_value,
                "exists": False,
                "is_directory": False,
                "file_count": 0,
                "total_size_mb": 0,
                "largest_file": None,
                "oldest_file": None,
                "newest_file": None
            }
            
            try:
                path_obj = Path(path_value)
                
                if path_obj.exists():
                    path_stats["exists"] = True
                    path_stats["is_directory"] = path_obj.is_dir()
                    stats["summary"]["existing_paths"] += 1
                    
                    if path_obj.is_dir():
                        files = []
                        total_size = 0
                        
                        for item in path_obj.rglob('*'):
                            if item.is_file():
                                try:
                                    file_stat = item.stat()
                                    file_info = {
                                        "path": str(item),
                                        "size": file_stat.st_size,
                                        "modified": datetime.fromtimestamp(file_stat.st_mtime)
                                    }
                                    files.append(file_info)
                                    total_size += file_stat.st_size
                                except Exception:
                                    continue  # Skip files that can't be stat'd
                        
                        path_stats["file_count"] = len(files)
                        path_stats["total_size_mb"] = round(total_size / 1024 / 1024, 2)
                        
                        stats["summary"]["total_files"] += len(files)
                        stats["summary"]["total_size_mb"] += path_stats["total_size_mb"]
                        
                        # Find largest, oldest, newest files
                        if files:
                            largest = max(files, key=lambda f: f["size"])
                            oldest = min(files, key=lambda f: f["modified"])
                            newest = max(files, key=lambda f: f["modified"])
                            
                            path_stats["largest_file"] = {
                                "path": Path(largest["path"]).name,
                                "size_mb": round(largest["size"] / 1024 / 1024, 2)
                            }
                            path_stats["oldest_file"] = {
                                "path": Path(oldest["path"]).name,
                                "modified": oldest["modified"].isoformat()
                            }
                            path_stats["newest_file"] = {
                                "path": Path(newest["path"]).name,
                                "modified": newest["modified"].isoformat()
                            }
                        
            except Exception as e:
                path_stats["error"] = str(e)
            
            stats["paths"][path_name] = path_stats
        
        return stats


# Global instance
_path_manager: Optional[PathManager] = None

def get_path_manager() -> PathManager:
    """Get global PathManager instance"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager
