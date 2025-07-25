"""
Main router for maintenance operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from .models import BackupCreateRequest, BackupRestoreRequest, DatabaseImportRequest
from . import logs, database

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.get("/", response_model=dict)
async def maintenance_root():
    """Maintenance API root endpoint"""
    return {
        "success": True,
        "message": "Maintenance API endpoints",
        "endpoints": [
            "/database/status",
            "/database/backup",
            "/database/export",
            "/database/restore",
            "/database/import-settings",
            "/logs",
            "/logs/levels",
            "/logs/download",
            "/logs/clear"
        ]
    }

# Database endpoints
@router.get("/database/status")
async def get_database_status(db: AsyncSession = Depends(get_db_session)):
    """Get PostgreSQL database status and backup information."""
    return await database.get_database_status(db)

@router.post("/database/backup")
async def create_backup(request: BackupCreateRequest, db: AsyncSession = Depends(get_db_session)):
    """Create a PostgreSQL database backup."""
    return await database.create_backup(request, db)

@router.post("/database/export")
async def export_database(db: AsyncSession = Depends(get_db_session)):
    """Export database data to JSON format and return as downloadable file."""
    return await database.export_database(db)

@router.post("/database/restore")
async def restore_database(request: BackupRestoreRequest, db: AsyncSession = Depends(get_db_session)):
    """Restore database from SQL backup file."""
    return await database.restore_database(request, db)

@router.post("/database/import-settings")
async def import_database_settings(request: DatabaseImportRequest, db: AsyncSession = Depends(get_db_session)):
    """Import database settings from JSON export file."""
    return await database.import_database_settings(request, db)

@router.post("/database/import-settings-upload")
async def import_database_settings_upload(
    file: UploadFile = File(...),
    confirm_restore: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """Import database settings from uploaded JSON export file."""
    return await database.import_database_settings_upload(file, confirm_restore, db)

# Logs endpoints
@router.get("/logs")
async def get_logs(level: Optional[str] = None, search: Optional[str] = None, limit: int = 1000):
    """Get application logs with optional filtering."""
    return await logs.get_logs(level, search, limit)

@router.get("/logs/levels")
async def get_log_levels():
    """Get available log levels."""
    return await logs.get_log_levels()

@router.delete("/logs/clear")
async def clear_logs():
    """Clear application logs."""
    return await logs.clear_logs()

@router.get("/logs/download")
async def download_logs():
    """Download the log file."""
    return await logs.download_logs()
