"""
FastAPI routes for maintenance operations.
Handles connection testing, database operations, and logs management for PostgreSQL.
"""

import os
import json
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.database import get_db_session, DatabaseManager
from app.core.config import get_settings

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/maintenance", tags=["maintenance"])

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

class LogsQueryRequest(BaseModel):
    level: Optional[str] = None
    search: Optional[str] = None
    limit: int = 1000

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

@router.get("/database/status")
async def get_database_status(db: AsyncSession = Depends(get_db_session)):
    """Get PostgreSQL database status and backup information."""
    try:
        logger.info(f"Getting PostgreSQL database status")
        settings = get_settings()
        
        # Get database connection info
        db_manager = DatabaseManager()
        health_info = await db_manager.health_check()
        connection_info = await db_manager.get_connection_info()
        
        # Get database size and table info
        db_size = 0
        table_count = 0
        schema_version = "unknown"
        
        try:
            # Get database size
            size_result = await db.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       pg_database_size(current_database()) as size_bytes
            """))
            size_row = size_result.fetchone()
            if size_row:
                db_size = size_row.size_bytes
                db_size_formatted = size_row.size
            else:
                db_size_formatted = "0 B"
            
            # Get table count
            table_result = await db.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_row = table_result.fetchone()
            if table_row:
                table_count = table_row.table_count
            
            # Try to get schema version (if you have a version table)
            try:
                version_result = await db.execute(text("""
                    SELECT version FROM alembic_version LIMIT 1
                """))
                version_row = version_result.fetchone()
                if version_row:
                    schema_version = f"alembic_{version_row.version[:8]}"
            except Exception:
                # If no alembic_version table, just use table count
                schema_version = f"tables_{table_count}"
                
        except Exception as e:
            logger.warning(f"Could not get detailed database info: {e}")
            db_size_formatted = "Unknown"
        
        # Get backup files
        backups = []
        if BACKUP_DIR.exists():
            backup_files = list(BACKUP_DIR.glob("*.sql*"))
            logger.info(f"Found {len(backup_files)} backup files")
            
            for backup_file in backup_files:
                try:
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "size": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "compressed": backup_file.suffix == ".gz"
                    })
                except Exception as e:
                    logger.warning(f"Error processing backup file {backup_file}: {e}")
        else:
            logger.info(f"Backup directory does not exist: {BACKUP_DIR}")
        
        # Sort backups by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        # Parse database URL for display (hide password)
        db_url_display = settings.database_url
        if '@' in db_url_display:
            # Hide password: postgresql://user:password@host:port/db -> postgresql://user:***@host:port/db
            parts = db_url_display.split('@')
            if len(parts) >= 2:
                before_at = parts[0]
                after_at = '@'.join(parts[1:])
                if ':' in before_at:
                    protocol_user = before_at.rsplit(':', 1)[0]
                    db_url_display = f"{protocol_user}:***@{after_at}"
        
        result = {
            "success": True,
            "database": {
                "exists": health_info["status"] == "healthy",
                "path": db_url_display,
                "size": db_size,
                "size_formatted": db_size_formatted,
                "table_count": table_count,
                "connection_status": health_info["status"]
            },
            "schema_version": schema_version,
            "backups": backups,
            "backup_directory": str(BACKUP_DIR),
            "connection_info": connection_info
        }
        
        logger.info(f"PostgreSQL database status result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error getting database status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get database status: {str(e)}")

@router.get("/logs")
async def get_logs(level: Optional[str] = None, search: Optional[str] = None, limit: int = 1000):
    """Get application logs with optional filtering."""
    try:
        settings = get_settings()
        log_file = Path(settings.log_file_path) if settings.log_file_path else LOGS_DIR / "aphrodite-v2.log"
        
        if not log_file.exists():
            logger.info(f"Log file does not exist: {log_file}")
            return {
                "success": True,
                "logs": [],
                "total_lines": 0,
                "filtered_lines": 0,
                "file_size": 0,
                "file_modified": ""
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
            "file_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")

@router.get("/logs/levels")
async def get_log_levels():
    """Get available log levels."""
    return {
        "success": True,
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    }

@router.delete("/logs/clear")
async def clear_logs():
    """Clear application logs."""
    try:
        settings = get_settings()
        log_file = Path(settings.log_file_path) if settings.log_file_path else LOGS_DIR / "aphrodite-v2.log"
        
        if log_file.exists():
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

@router.post("/database/backup")
async def create_backup(request: BackupCreateRequest, db: AsyncSession = Depends(get_db_session)):
    """Create a PostgreSQL database backup."""
    try:
        logger.info(f"Creating PostgreSQL database backup")
        settings = get_settings()
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = request.backup_name or f"aphrodite_backup_{timestamp}"
        
        # Add .sql extension if not present
        if not backup_name.endswith('.sql'):
            backup_name += '.sql'
        
        backup_file = BACKUP_DIR / backup_name
        
        # Parse database URL to get connection parameters
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(settings.database_url)
        
        # Build pg_dump command
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password or ''
        
        cmd = [
            'pg_dump',
            '-h', parsed.hostname or 'localhost',
            '-p', str(parsed.port or 5432),
            '-U', parsed.username or 'postgres',
            '-d', parsed.path.lstrip('/') if parsed.path else 'aphrodite',
            '--no-password',
            '--verbose',
            '--clean',
            '--if-exists',
            '--create'
        ]
        
        logger.info(f"Running pg_dump command to {backup_file}")
        
        # Run pg_dump
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "pg_dump failed"
            logger.error(f"pg_dump failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Backup failed: {error_msg}")
        
        # Write backup to file
        with open(backup_file, 'wb') as f:
            f.write(stdout)
        
        # Compress if requested
        final_file = backup_file
        if request.compress:
            import gzip
            compressed_file = backup_file.with_suffix('.sql.gz')
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove uncompressed file
            backup_file.unlink()
            final_file = compressed_file
        
        # Get file info
        file_stat = final_file.stat()
        
        logger.info(f"Backup created successfully: {final_file}")
        
        return {
            "success": True,
            "message": "Backup created successfully",
            "filename": final_file.name,
            "size": file_stat.st_size,
            "size_formatted": format_file_size(file_stat.st_size),
            "compressed": request.compress,
            "created": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.post("/database/export")
async def export_database(db: AsyncSession = Depends(get_db_session)):
    """Export database data to JSON format."""
    try:
        logger.info(f"Exporting PostgreSQL database to JSON")
        
        # Get all table names
        tables_result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        tables = [row.table_name for row in tables_result.fetchall()]
        logger.info(f"Found {len(tables)} tables to export: {tables}")
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "database": "aphrodite",
                "tables_count": len(tables)
            },
            "tables": {}
        }
        
        # Export each table
        for table_name in tables:
            try:
                logger.info(f"Exporting table: {table_name}")
                
                # Get table data
                result = await db.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()
                
                # Convert rows to dictionaries
                if rows:
                    columns = list(rows[0]._mapping.keys())
                    table_data = []
                    
                    for row in rows:
                        row_dict = {}
                        for col in columns:
                            value = getattr(row, col)
                            # Convert datetime objects to ISO strings
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            # Convert other non-serializable types
                            elif hasattr(value, '__dict__'):
                                value = str(value)
                            row_dict[col] = value
                        table_data.append(row_dict)
                    
                    export_data["tables"][table_name] = {
                        "columns": columns,
                        "row_count": len(table_data),
                        "data": table_data
                    }
                else:
                    export_data["tables"][table_name] = {
                        "columns": [],
                        "row_count": 0,
                        "data": []
                    }
                    
                logger.info(f"Exported {len(export_data['tables'][table_name]['data'])} rows from {table_name}")
                
            except Exception as table_error:
                logger.error(f"Error exporting table {table_name}: {table_error}")
                export_data["tables"][table_name] = {
                    "error": str(table_error),
                    "row_count": 0,
                    "data": []
                }
        
        # Generate export filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"aphrodite_export_{timestamp}.json"
        export_file = BACKUP_DIR / export_filename
        
        # Write JSON export
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Get file info
        file_stat = export_file.stat()
        
        logger.info(f"Database exported successfully: {export_file}")
        
        return {
            "success": True,
            "message": "Database exported successfully",
            "filename": export_file.name,
            "size": file_stat.st_size,
            "size_formatted": format_file_size(file_stat.st_size),
            "tables_exported": len([t for t in export_data["tables"].values() if "error" not in t]),
            "tables_failed": len([t for t in export_data["tables"].values() if "error" in t]),
            "total_rows": sum(t.get("row_count", 0) for t in export_data["tables"].values()),
            "created": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export database: {str(e)}")

@router.post("/database/restore")
async def restore_database(request: BackupRestoreRequest, db: AsyncSession = Depends(get_db_session)):
    """Restore database from SQL backup file."""
    try:
        logger.info(f"Restoring PostgreSQL database from backup: {request.filename}")
        settings = get_settings()
        
        # Check if backup file exists
        backup_file = BACKUP_DIR / request.filename
        if not backup_file.exists():
            raise HTTPException(status_code=404, detail=f"Backup file not found: {request.filename}")
        
        logger.info(f"Found backup file: {backup_file}")
        
        # Parse database URL to get connection parameters
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(settings.database_url)
        
        # Build psql command for restore
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password or ''
        
        # Determine if file is compressed
        is_compressed = backup_file.suffix == '.gz'
        
        if is_compressed:
            # For compressed files, decompress and pipe to psql
            logger.info(f"Restoring from compressed backup: {backup_file}")
            
            # Use gunzip and pipe to psql
            gunzip_process = await asyncio.create_subprocess_exec(
                'gunzip', '-c', str(backup_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            psql_process = await asyncio.create_subprocess_exec(
                'psql',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path.lstrip('/') if parsed.path else 'aphrodite',
                '--no-password',
                stdin=gunzip_process.stdout,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Wait for both processes
            gunzip_stdout, gunzip_stderr = await gunzip_process.communicate()
            psql_stdout, psql_stderr = await psql_process.communicate()
            
            if gunzip_process.returncode != 0:
                error_msg = gunzip_stderr.decode() if gunzip_stderr else "Failed to decompress backup"
                logger.error(f"Gunzip failed: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Decompression failed: {error_msg}")
            
            if psql_process.returncode != 0:
                error_msg = psql_stderr.decode() if psql_stderr else "Database restore failed"
                logger.error(f"psql restore failed: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Restore failed: {error_msg}")
                
        else:
            # For uncompressed files, restore directly
            logger.info(f"Restoring from uncompressed backup: {backup_file}")
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            psql_process = await asyncio.create_subprocess_exec(
                'psql',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path.lstrip('/') if parsed.path else 'aphrodite',
                '--no-password',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await psql_process.communicate(input=sql_content.encode())
            
            if psql_process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Database restore failed"
                logger.error(f"psql restore failed: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Restore failed: {error_msg}")
        
        logger.info(f"Database restored successfully from: {backup_file}")
        
        return {
            "success": True,
            "message": f"Database restored successfully from {request.filename}",
            "backup_file": request.filename,
            "compressed": is_compressed,
            "restored_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error restoring database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to restore database: {str(e)}")

@router.post("/database/import")
async def import_database_settings(request: DatabaseRestoreRequest, db: AsyncSession = Depends(get_db_session)):
    """Import database settings from JSON export file."""
    try:
        logger.info(f"Importing database settings from JSON: {request.filename}")
        
        # Check if export file exists
        export_file = BACKUP_DIR / request.filename
        if not export_file.exists():
            raise HTTPException(status_code=404, detail=f"Export file not found: {request.filename}")
        
        if not request.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON export")
        
        logger.info(f"Found export file: {export_file}")
        
        # Read and parse JSON export
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Validate export format
        if "export_info" not in export_data or "tables" not in export_data:
            raise HTTPException(status_code=400, detail="Invalid export format - missing required sections")
        
        export_info = export_data["export_info"]
        tables_data = export_data["tables"]
        
        logger.info(f"Import info: {export_info}")
        logger.info(f"Found {len(tables_data)} tables in export")
        
        # Safety check - require confirmation for destructive operation
        if not request.confirm_restore:
            return {
                "success": False,
                "message": "Import requires confirmation - this will overwrite existing data",
                "export_info": export_info,
                "tables_to_import": list(tables_data.keys()),
                "requires_confirmation": True
            }
        
        imported_tables = 0
        failed_tables = 0
        total_rows_imported = 0
        
        # Import each table
        for table_name, table_info in tables_data.items():
            if "error" in table_info:
                logger.warning(f"Skipping table {table_name} - had export error: {table_info['error']}")
                failed_tables += 1
                continue
            
            table_data = table_info.get("data", [])
            if not table_data:
                logger.info(f"Skipping empty table: {table_name}")
                continue
            
            try:
                logger.info(f"Importing table: {table_name} ({len(table_data)} rows)")
                
                # Clear existing data (DANGEROUS!)
                await db.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                
                # Import data row by row
                for row_data in table_data:
                    columns = list(row_data.keys())
                    values = list(row_data.values())
                    
                    # Build parameterized insert query
                    columns_str = ', '.join(columns)
                    placeholders = ', '.join([f":{col}" for col in columns])
                    
                    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    
                    await db.execute(text(insert_query), row_data)
                
                await db.commit()
                imported_tables += 1
                total_rows_imported += len(table_data)
                logger.info(f"Successfully imported {len(table_data)} rows into {table_name}")
                
            except Exception as table_error:
                await db.rollback()
                logger.error(f"Error importing table {table_name}: {table_error}")
                failed_tables += 1
        
        logger.info(f"Import completed: {imported_tables} tables imported, {failed_tables} failed")
        
        return {
            "success": True,
            "message": f"Database settings imported successfully from {request.filename}",
            "export_file": request.filename,
            "tables_imported": imported_tables,
            "tables_failed": failed_tables,
            "total_rows_imported": total_rows_imported,
            "export_info": export_info,
            "imported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error importing database settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to import database settings: {str(e)}")

@router.get("/logs/download")
async def download_logs():
    """Download the log file."""
    try:
        settings = get_settings()
        log_file = Path(settings.log_file_path) if settings.log_file_path else LOGS_DIR / "aphrodite-v2.log"
        
        if not log_file.exists():
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

# Utility functions
def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    if bytes_size == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} PB"
