"""
Logging operations for maintenance.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Response
import logging

from app.core.config import get_settings
from .models import LOGS_DIR

logger = logging.getLogger(__name__)

async def get_logs(level: Optional[str] = None, search: Optional[str] = None, limit: int = 1000):
    """Get application logs with optional filtering."""
    try:
        settings = get_settings()
        
        # Try multiple log file locations in order of preference
        potential_log_files = [
            Path(settings.log_file_path),  # Primary: from settings
            LOGS_DIR / "aphrodite-v2.log",  # Fallback: logs_dir + default name
            Path("/app/logs/aphrodite-v2.log"),  # Docker default
            Path("./logs/aphrodite-v2.log"),  # Local relative
            Path("aphrodite-v2.log"),  # Current directory
        ]
        
        log_file = None
        for potential_file in potential_log_files:
            if potential_file.exists():
                log_file = potential_file
                logger.info(f"Found log file at: {log_file}")
                break
        
        if not log_file:
            # Try to find any log file in the logs directory
            if LOGS_DIR.exists():
                log_files = list(LOGS_DIR.glob("*.log"))
                if log_files:
                    log_file = log_files[0]  # Use the first log file found
                    logger.info(f"Using alternative log file: {log_file}")
            
            # If still no log file found, create debug info
            if not log_file:
                debug_info = {
                    "logs_dir": str(LOGS_DIR),
                    "logs_dir_exists": LOGS_DIR.exists(),
                    "settings_log_path": settings.log_file_path,
                    "current_working_dir": str(Path.cwd()),
                    "potential_files_checked": [str(f) for f in potential_log_files],
                }
                
                if LOGS_DIR.exists():
                    debug_info["files_in_logs_dir"] = [f.name for f in LOGS_DIR.iterdir()]
                
                logger.warning(f"No log file found. Debug info: {debug_info}")
                
                return {
                    "success": True,
                    "logs": [],
                    "total_lines": 0,
                    "filtered_lines": 0,
                    "file_size": 0,
                    "file_modified": "",
                    "debug_info": debug_info
                }
        
        # Read log file
        logs = []
        total_lines = 0
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                line = line.strip()
                if not line:
                    continue
                
                # Parse log line - try JSON first (structured logging), then fallback to bracket format
                try:
                    # Try to parse as JSON (structured logging)
                    if line.startswith('{'):
                        log_data = json.loads(line)
                        timestamp = log_data.get('timestamp', '')
                        log_level = log_data.get('level', 'INFO')
                        message = log_data.get('message', line)
                    else:
                        # Parse format: 2025-06-11 10:05:13 [INFO] logger_name:line: message
                        bracket_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[([A-Z]+)\] (.+)$', line)
                        if bracket_match:
                            timestamp = bracket_match.group(1)
                            log_level = bracket_match.group(2)
                            message = bracket_match.group(3)
                        else:
                            # Fallback to simple format: timestamp - level - message
                            parts = line.split(' - ', 2)
                            if len(parts) >= 3:
                                timestamp, log_level, message = parts[0], parts[1], parts[2]
                            else:
                                # Further fallback for malformed lines
                                timestamp = ""
                                log_level = "INFO"
                                message = line
                    
                    # Apply filters
                    if level and log_level.upper() != level.upper():
                        continue
                    
                    if search and search.lower() not in message.lower():
                        continue
                    
                    logs.append({
                        "line_number": line_num,
                        "timestamp": timestamp,
                        "level": log_level,
                        "message": message
                    })
                    
                except Exception:
                    # Skip malformed lines
                    continue
        
        # Limit results (get last N entries)
        if len(logs) > limit:
            logs = logs[-limit:]
        
        # Get file info
        file_stat = log_file.stat()
        
        return {
            "success": True,
            "logs": logs,
            "total_lines": total_lines,
            "filtered_lines": len(logs),
            "file_size": file_stat.st_size,
            "file_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "log_file_path": str(log_file)
        }
    
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")

async def get_log_levels():
    """Get available log levels."""
    return {
        "success": True,
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    }

async def clear_logs():
    """Clear application logs."""
    try:
        settings = get_settings()
        
        # Use the same log file discovery logic as get_logs
        potential_log_files = [
            Path(settings.log_file_path),
            LOGS_DIR / "aphrodite-v2.log",
            Path("/app/logs/aphrodite-v2.log"),
            Path("./logs/aphrodite-v2.log"),
            Path("aphrodite-v2.log"),
        ]
        
        log_file = None
        for potential_file in potential_log_files:
            if potential_file.exists():
                log_file = potential_file
                break
        
        if log_file and log_file.exists():
            # Clear the log file content
            with open(log_file, 'w') as f:
                f.write("")
            
            logger.info("Application logs cleared")
            
            return {
                "success": True,
                "message": "Logs cleared successfully"
            }
        else:
            return {
                "success": True,
                "message": "Log file does not exist"
            }
    
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

async def download_logs():
    """Download the log file."""
    try:
        settings = get_settings()
        
        # Use the same log file discovery logic as get_logs
        potential_log_files = [
            Path(settings.log_file_path),
            LOGS_DIR / "aphrodite-v2.log",
            Path("/app/logs/aphrodite-v2.log"),
            Path("./logs/aphrodite-v2.log"),
            Path("aphrodite-v2.log"),
        ]
        
        log_file = None
        for potential_file in potential_log_files:
            if potential_file.exists():
                log_file = potential_file
                break
        
        if not log_file:
            raise HTTPException(status_code=404, detail="Log file not found")
        
        # Read log file content
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Return as downloadable file
        filename = f"aphrodite-v2-logs-{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        return Response(
            content=content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download logs: {str(e)}")
