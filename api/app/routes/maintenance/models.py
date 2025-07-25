"""
Shared models and utilities for maintenance operations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Request/Response Models
class ConnectionTestRequest(BaseModel):
    api_type: str
    credentials: Dict[str, Any]

class BackupCreateRequest(BaseModel):
    compress: bool = True
    backup_name: Optional[str] = None

class BackupRestoreRequest(BaseModel):
    filename: str

class DatabaseRestoreRequest(BaseModel):
    filename: str
    confirm_restore: bool = False

class DatabaseImportRequest(BaseModel):
    filename: Optional[str] = None
    jsonData: Optional[Dict[str, Any]] = None
    confirm_restore: bool = False

class LogsQueryRequest(BaseModel):
    level: Optional[str] = None
    search: Optional[str] = None
    limit: int = 1000

# Custom JSON encoder for database types
class DatabaseJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles database-specific types."""
    
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            # For any other complex object, convert to string
            return str(obj)
        return super().default(obj)

def get_directories():
    """Get all required directories based on settings."""
    settings = get_settings()
    
    # Create directories based on settings
    base_dir = Path.cwd()
    backup_dir = base_dir / "data" / "backups"
    logs_dir = Path(settings.log_file_path).parent if settings.log_file_path else base_dir / "logs"
    
    return {
        'backup': backup_dir,
        'logs': logs_dir
    }

def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    if bytes_size == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} PB"

# Initialize paths
try:
    paths = get_directories()
    BACKUP_DIR = paths['backup']
    LOGS_DIR = paths['logs']

    # Ensure directories exist
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Maintenance module initialized:")
    logger.info(f"  Backups: {BACKUP_DIR}")
    logger.info(f"  Logs: {LOGS_DIR}")
    logger.info(f"  Working directory: {Path.cwd()}")
except Exception as e:
    logger.error(f"Error initializing maintenance paths: {e}")
    # Fallback to simple defaults
    BACKUP_DIR = Path("./data/backups")
    LOGS_DIR = Path("./logs")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
