"""
FastAPI routes for maintenance operations.
Handles connection testing, database operations, and logs management for PostgreSQL.
"""

import os
import json
import asyncio
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

@router.post("/database/backup")
async def create_backup(request: BackupCreateRequest, db: AsyncSession = Depends(get_db_session)):
    """Create a PostgreSQL database backup using pg_dump or SQLAlchemy fallback."""
    try:
        settings = get_settings()
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = request.backup_name or f"aphrodite_v2_backup_{timestamp}"
        
        # Try pg_dump first, fallback to SQLAlchemy
        try:
            return await _create_backup_pgdump(request, backup_name, settings)
        except FileNotFoundError:
            logger.info("pg_dump not found, using SQLAlchemy fallback method")
            return await _create_backup_sqlalchemy(request, backup_name, db, settings)
    
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

async def _create_backup_pgdump(request: BackupCreateRequest, backup_name: str, settings):
    """Create backup using pg_dump (preferred method)."""
    # Parse database URL to get connection parameters
    db_url = settings.database_url
    # Remove the driver part (+asyncpg)
    if '://' in db_url:
        if '+' in db_url:
            protocol, rest = db_url.split('://', 1)
            protocol = protocol.split('+')[0]  # Remove +asyncpg
            db_url = f"{protocol}://{rest}"
    
    # Parse connection details
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432
    database = parsed.path.lstrip('/') if parsed.path else 'aphrodite_v2'
    username = parsed.username or 'aphrodite'
    password = parsed.password or 'development'
    
    backup_filename = f"{backup_name}.sql"
    if request.compress:
        backup_filename += ".gz"
    
    backup_path = BACKUP_DIR / backup_filename
    
    # Create pg_dump command
    import subprocess
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    pg_dump_cmd = [
        'pg_dump',
        '-h', host,
        '-p', str(port),
        '-U', username,
        '-d', database,
        '--no-password',
        '--verbose',
        '--clean',
        '--if-exists',
        '--create'
    ]
    
    if request.compress:
        pg_dump_cmd.extend(['--compress=9'])
    
    logger.info(f"Creating PostgreSQL backup with pg_dump: {backup_filename}")
    logger.info(f"Command: {' '.join(pg_dump_cmd[:-1])} [password hidden]")
    
    # Run pg_dump
    with open(backup_path, 'w' if not request.compress else 'wb') as f:
        result = subprocess.run(
            pg_dump_cmd,
            stdout=f,
            stderr=subprocess.PIPE,
            env=env,
            timeout=300  # 5 minute timeout
        )
    
    if result.returncode != 0:
        error_output = result.stderr.decode() if result.stderr else "Unknown error"
        logger.error(f"pg_dump failed: {error_output}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {error_output}")
    
    # Get backup info
    backup_stat = backup_path.stat()
    
    logger.info(f"PostgreSQL backup created successfully with pg_dump: {backup_filename}")
    
    return {
        "success": True,
        "message": f"PostgreSQL backup created successfully (pg_dump)",
        "backup_filename": backup_filename,
        "backup_size": backup_stat.st_size,
        "backup_size_formatted": format_file_size(backup_stat.st_size),
        "compressed": request.compress,
        "backup_type": "postgresql_dump",
        "method": "pg_dump"
    }

async def _create_backup_sqlalchemy(request: BackupCreateRequest, backup_name: str, db: AsyncSession, settings):
    """Create backup using SQLAlchemy (fallback method)."""
    backup_filename = f"{backup_name}_schema.sql"
    backup_path = BACKUP_DIR / backup_filename
    
    logger.info(f"Creating PostgreSQL backup with SQLAlchemy: {backup_filename}")
    
    # Get database schema and data using SQLAlchemy
    backup_content = []
    backup_content.append("-- Aphrodite v2 Database Backup (SQLAlchemy method)")
    backup_content.append(f"-- Created: {datetime.now().isoformat()}")
    backup_content.append(f"-- Database: {settings.database_url.split('/')[-1]}")
    backup_content.append("")
    
    try:
        # Get all table names
        tables_result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row.table_name for row in tables_result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to backup: {tables}")
        
        # For each table, get structure and data
        for table in tables:
            backup_content.append(f"-- Table: {table}")
            
            # Get table structure (simplified)
            columns_result = await db.execute(text(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position
            """))
            columns = columns_result.fetchall()
            
            # Create table statement (simplified)
            backup_content.append(f"DROP TABLE IF EXISTS {table} CASCADE;")
            create_stmt = f"CREATE TABLE {table} ("
            column_defs = []
            for col in columns:
                col_def = f"  {col.column_name} {col.data_type}"
                if col.is_nullable == 'NO':
                    col_def += " NOT NULL"
                if col.column_default:
                    col_def += f" DEFAULT {col.column_default}"
                column_defs.append(col_def)
            create_stmt += ",\n".join(column_defs) + "\n);"
            backup_content.append(create_stmt)
            backup_content.append("")
            
            # Get table data
            try:
                data_result = await db.execute(text(f"SELECT * FROM {table}"))
                rows = data_result.fetchall()
                
                if rows:
                    column_names = [col.column_name for col in columns]
                    backup_content.append(f"-- Data for table {table} ({len(rows)} rows)")
                    
                    for row in rows:
                        values = []
                        for i, value in enumerate(row):
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Escape single quotes
                                escaped = value.replace("'", "''")
                                values.append(f"'{escaped}'")
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                values.append(f"'{str(value)}'")
                        
                        insert_stmt = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(values)});"
                        backup_content.append(insert_stmt)
                    
                    backup_content.append("")
                else:
                    backup_content.append(f"-- No data in table {table}")
                    backup_content.append("")
                    
            except Exception as e:
                logger.warning(f"Could not backup data for table {table}: {e}")
                backup_content.append(f"-- Error backing up data for {table}: {e}")
                backup_content.append("")
    
    except Exception as e:
        logger.error(f"Error during schema backup: {e}")
        backup_content.append(f"-- Error during backup: {e}")
    
    # Write backup file
    backup_text = "\n".join(backup_content)
    
    if request.compress:
        import gzip
        backup_filename += ".gz"
        backup_path = BACKUP_DIR / backup_filename
        with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
            f.write(backup_text)
    else:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_text)
    
    # Get backup info
    backup_stat = backup_path.stat()
    
    logger.info(f"PostgreSQL backup created successfully with SQLAlchemy: {backup_filename}")
    
    return {
        "success": True,
        "message": f"PostgreSQL backup created successfully (SQLAlchemy fallback)",
        "backup_filename": backup_filename,
        "backup_size": backup_stat.st_size,
        "backup_size_formatted": format_file_size(backup_stat.st_size),
        "compressed": request.compress,
        "backup_type": "postgresql_schema",
        "method": "sqlalchemy",
        "note": "Created without pg_dump - install PostgreSQL client tools for full dumps"
    }

@router.post("/database/restore")
async def restore_backup(request: BackupRestoreRequest):
    """Restore PostgreSQL database from backup using psql."""
    try:
        settings = get_settings()
        backup_path = BACKUP_DIR / request.filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # Parse database URL to get connection parameters
        db_url = settings.database_url
        if '://' in db_url:
            if '+' in db_url:
                protocol, rest = db_url.split('://', 1)
                protocol = protocol.split('+')[0]
                db_url = f"{protocol}://{rest}"
        
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        database = parsed.path.lstrip('/') if parsed.path else 'aphrodite_v2'
        username = parsed.username or 'aphrodite'
        password = parsed.password or 'development'
        
        # Create automatic backup before restore
        auto_backup_filename = None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_backup_request = BackupCreateRequest(
                compress=True,
                backup_name=f"aphrodite_v2_pre_restore_{timestamp}"
            )
            backup_result = await create_backup(auto_backup_request)
            auto_backup_filename = backup_result["backup_filename"]
            logger.info(f"Created automatic backup before restore: {auto_backup_filename}")
        except Exception as e:
            logger.warning(f"Could not create automatic backup: {e}")
        
        # Create psql restore command
        import subprocess
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        if request.filename.endswith('.gz'):
            # Compressed file - use zcat | psql
            psql_cmd = ['zcat', str(backup_path)]
            psql2_cmd = [
                'psql',
                '-h', host,
                '-p', str(port),
                '-U', username,
                '-d', database,
                '--no-password'
            ]
            
            logger.info(f"Restoring compressed PostgreSQL backup: {request.filename}")
            
            # Use shell pipeline: zcat backup.sql.gz | psql
            import shlex
            full_cmd = f"zcat {shlex.quote(str(backup_path))} | psql -h {host} -p {port} -U {username} -d {database} --no-password"
            
            result = subprocess.run(
                full_cmd,
                shell=True,
                env=env,
                capture_output=True,
                timeout=600  # 10 minute timeout
            )
        else:
            # Uncompressed file
            psql_cmd = [
                'psql',
                '-h', host,
                '-p', str(port),
                '-U', username,
                '-d', database,
                '--no-password',
                '-f', str(backup_path)
            ]
            
            logger.info(f"Restoring PostgreSQL backup: {request.filename}")
            
            result = subprocess.run(
                psql_cmd,
                env=env,
                capture_output=True,
                timeout=600  # 10 minute timeout
            )
        
        if result.returncode != 0:
            error_output = result.stderr.decode() if result.stderr else "Unknown error"
            logger.error(f"Database restore failed: {error_output}")
            raise HTTPException(status_code=500, detail=f"Restore failed: {error_output}")
        
        logger.info(f"PostgreSQL database restored from backup: {request.filename}")
        
        return {
            "success": True,
            "message": f"PostgreSQL database restored successfully from {request.filename}",
            "restored_from": request.filename,
            "auto_backup_created": auto_backup_filename,
            "restore_type": "postgresql_restore"
        }
    
    except subprocess.TimeoutExpired:
        logger.error("Restore operation timed out")
        raise HTTPException(status_code=500, detail="Restore operation timed out")
    except FileNotFoundError:
        logger.error("psql command not found. Please ensure PostgreSQL client tools are installed.")
        raise HTTPException(status_code=500, detail="psql command not found. PostgreSQL client tools required.")
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")

@router.post("/database/export")
async def export_database(request: dict, db: AsyncSession = Depends(get_db_session)):
    """Export database data to JSON format."""
    try:
        include_sensitive = request.get('includeSensitive', False)
        
        logger.info(f"Exporting database to JSON (include_sensitive: {include_sensitive})")
        
        export_data = {
            "export_info": {
                "created": datetime.now().isoformat(),
                "version": "aphrodite_v2",
                "include_sensitive": include_sensitive,
                "export_type": "database_settings"
            },
            "tables": {}
        }
        
        # Get all table names
        tables_result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row.table_name for row in tables_result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to export: {tables}")
        
        # Define sensitive tables/columns to exclude if include_sensitive is False
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        
        # Export each table
        for table in tables:
            try:
                # Get table structure
                columns_result = await db.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """))
                columns = columns_result.fetchall()
                
                # Filter sensitive columns if needed
                export_columns = []
                if include_sensitive:
                    export_columns = [col.column_name for col in columns]
                else:
                    for col in columns:
                        is_sensitive = any(pattern in col.column_name.lower() for pattern in sensitive_patterns)
                        if not is_sensitive:
                            export_columns.append(col.column_name)
                        else:
                            logger.info(f"Excluding sensitive column: {table}.{col.column_name}")
                
                if not export_columns:
                    logger.info(f"No exportable columns found for table {table}")
                    continue
                
                # Get table data
                select_columns = ', '.join(export_columns)
                data_result = await db.execute(text(f"SELECT {select_columns} FROM {table}"))
                rows = data_result.fetchall()
                
                # Convert to JSON-serializable format
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(export_columns):
                        value = row[i] if i < len(row) else None
                        # Handle special data types
                        if value is not None:
                            if hasattr(value, 'isoformat'):  # datetime objects
                                value = value.isoformat()
                            elif isinstance(value, (bytes, bytearray)):
                                value = value.decode('utf-8', errors='replace')
                            elif isinstance(value, str):
                                # Try to parse JSON strings back to objects for better structure
                                try:
                                    # Check if it looks like JSON (starts with { or [)
                                    if value.strip().startswith(('{', '[')):
                                        parsed_value = json.loads(value)
                                        value = parsed_value
                                except (json.JSONDecodeError, ValueError):
                                    # If it's not valid JSON, keep as string
                                    pass
                        row_dict[col_name] = value
                    table_data.append(row_dict)
                
                export_data["tables"][table] = {
                    "schema": {
                        "columns": [{
                            "name": col.column_name,
                            "type": col.data_type,
                            "nullable": col.is_nullable == 'YES',
                            "default": col.column_default
                        } for col in columns if col.column_name in export_columns]
                    },
                    "data": table_data,
                    "row_count": len(table_data)
                }
                
                logger.info(f"Exported table {table}: {len(table_data)} rows, {len(export_columns)} columns")
                
            except Exception as e:
                logger.warning(f"Could not export table {table}: {e}")
                export_data["tables"][table] = {
                    "error": str(e),
                    "exported": False
                }
        
        # Create JSON content
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sensitive_suffix = "_full" if include_sensitive else "_filtered"
        filename = f"aphrodite_v2_export{sensitive_suffix}_{timestamp}.json"
        
        logger.info(f"Database export completed: {filename} ({len(json_content)} bytes)")
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Error exporting database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export database: {str(e)}")

@router.post("/database/import-settings")
async def import_database_settings(request: dict, db: AsyncSession = Depends(get_db_session)):
    """Import and restore database settings from JSON export."""
    try:
        json_data = request.get('jsonData')
        if not json_data:
            raise HTTPException(status_code=400, detail="No JSON data provided")
        
        # Parse JSON data if it's a string
        if isinstance(json_data, str):
            import_data = json.loads(json_data)
        else:
            import_data = json_data
        
        # Validate import data structure
        if not import_data.get('export_info') or not import_data.get('tables'):
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        export_info = import_data['export_info']
        tables_data = import_data['tables']
        
        logger.info(f"Importing database settings from export created: {export_info.get('created')}")
        logger.info(f"Export version: {export_info.get('version')}, type: {export_info.get('export_type')}")
        
        # Create automatic backup before import
        auto_backup_filename = None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_backup_request = BackupCreateRequest(
                compress=True,
                backup_name=f"aphrodite_v2_pre_import_{timestamp}"
            )
            backup_result = await create_backup(auto_backup_request)
            auto_backup_filename = backup_result["backup_filename"]
            logger.info(f"Created automatic backup before import: {auto_backup_filename}")
        except Exception as e:
            logger.warning(f"Could not create automatic backup: {e}")
        
        imported_tables = []
        skipped_tables = []
        errors = []
        
        # Process each table in the import
        for table_name, table_info in tables_data.items():
            try:
                if table_info.get('error') or not table_info.get('data'):
                    skipped_tables.append(f"{table_name} (no data or error in export)")
                    continue
                
                table_data = table_info['data']
                if not table_data:
                    skipped_tables.append(f"{table_name} (empty)")
                    continue
                
                # Check if table exists
                table_exists_result = await db.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = '{table_name}' 
                        AND table_schema = 'public'
                    )
                """))
                table_exists = table_exists_result.scalar()
                
                if not table_exists:
                    skipped_tables.append(f"{table_name} (table does not exist)")
                    continue
                
                # Get current table structure
                columns_result = await db.execute(text(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    ORDER BY ordinal_position
                """))
                current_columns = {row.column_name: row.data_type for row in columns_result.fetchall()}
                
                # Clear existing data (be careful!)
                await db.execute(text(f"DELETE FROM {table_name}"))
                
                # Insert imported data
                inserted_count = 0
                for row_data in table_data:
                    # Filter columns that exist in current table
                    valid_columns = {k: v for k, v in row_data.items() if k in current_columns}
                    
                    if not valid_columns:
                        continue
                    
                    # Handle special data types for database insertion
                    processed_columns = {}
                    for col_name, value in valid_columns.items():
                        if value is None:
                            processed_columns[col_name] = None
                        elif isinstance(value, (dict, list)):
                            # Convert complex objects back to JSON strings
                            processed_columns[col_name] = json.dumps(value)
                        elif isinstance(value, str):
                            # Check if this column should be a datetime based on column type
                            col_type = current_columns.get(col_name, '').lower()
                            if 'timestamp' in col_type or 'datetime' in col_type:
                                # This is a datetime column, try to parse the string
                                try:
                                    from datetime import datetime
                                    # Handle both with and without 'Z' suffix and microseconds
                                    if value.endswith('Z'):
                                        dt_value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    else:
                                        dt_value = datetime.fromisoformat(value)
                                    processed_columns[col_name] = dt_value
                                except (ValueError, TypeError):
                                    # If it's not a valid datetime, keep as string
                                    processed_columns[col_name] = value
                            else:
                                processed_columns[col_name] = value
                        else:
                            processed_columns[col_name] = value
                    
                    # Build insert statement
                    columns = list(processed_columns.keys())
                    placeholders = [f":{col}" for col in columns]
                    
                    insert_sql = f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({', '.join(placeholders)})
                    """
                    
                    # Execute insert with proper parameter binding
                    await db.execute(text(insert_sql), processed_columns)
                    inserted_count += 1
                
                imported_tables.append(f"{table_name} ({inserted_count} rows)")
                logger.info(f"Imported {inserted_count} rows into table {table_name}")
                
            except Exception as e:
                error_msg = f"{table_name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error importing table {table_name}: {e}")
        
        # Commit the transaction
        await db.commit()
        
        result = {
            "success": True,
            "message": f"Database settings imported successfully",
            "imported_tables": imported_tables,
            "skipped_tables": skipped_tables,
            "errors": errors,
            "auto_backup_created": auto_backup_filename,
            "import_summary": {
                "total_tables_in_export": len(tables_data),
                "tables_imported": len(imported_tables),
                "tables_skipped": len(skipped_tables),
                "tables_with_errors": len(errors)
            }
        }
        
        if errors:
            result["message"] += f" (with {len(errors)} errors)"
        
        logger.info(f"Database settings import completed: {result['import_summary']}")
        
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing database settings: {e}")
        # Rollback transaction on error
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import database settings: {str(e)}")



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
                
                # Parse log line - try JSON first (structured logging), then fallback to simple
                try:
                    # Try to parse as JSON (structured logging)
                    if line.startswith('{'):
                        import json
                        log_data = json.loads(line)
                        timestamp = log_data.get('timestamp', '')
                        log_level = log_data.get('level', 'INFO')
                        message = log_data.get('message', line)
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

@router.post("/database/export")
async def export_database(request: dict, db: AsyncSession = Depends(get_db_session)):
    """Export database data to JSON format."""
    try:
        include_sensitive = request.get('includeSensitive', False)
        
        logger.info(f"Exporting database to JSON (include_sensitive: {include_sensitive})")
        
        export_data = {
            "export_info": {
                "created": datetime.now().isoformat(),
                "version": "aphrodite_v2",
                "include_sensitive": include_sensitive,
                "export_type": "database_settings"
            },
            "tables": {}
        }
        
        # Get all table names
        tables_result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row.table_name for row in tables_result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to export: {tables}")
        
        # Define sensitive tables/columns to exclude if include_sensitive is False
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        
        # Export each table
        for table in tables:
            try:
                # Get table structure
                columns_result = await db.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """))
                columns = columns_result.fetchall()
                
                # Filter sensitive columns if needed
                export_columns = []
                if include_sensitive:
                    export_columns = [col.column_name for col in columns]
                else:
                    for col in columns:
                        is_sensitive = any(pattern in col.column_name.lower() for pattern in sensitive_patterns)
                        if not is_sensitive:
                            export_columns.append(col.column_name)
                        else:
                            logger.info(f"Excluding sensitive column: {table}.{col.column_name}")
                
                if not export_columns:
                    logger.info(f"No exportable columns found for table {table}")
                    continue
                
                # Get table data
                select_columns = ', '.join(export_columns)
                data_result = await db.execute(text(f"SELECT {select_columns} FROM {table}"))
                rows = data_result.fetchall()
                
                # Convert to JSON-serializable format
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(export_columns):
                        value = row[i] if i < len(row) else None
                        # Handle special data types
                        if value is not None:
                            if hasattr(value, 'isoformat'):  # datetime objects
                                value = value.isoformat()
                            elif isinstance(value, (bytes, bytearray)):
                                value = value.decode('utf-8', errors='replace')
                        row_dict[col_name] = value
                    table_data.append(row_dict)
                
                export_data["tables"][table] = {
                    "schema": {
                        "columns": [{
                            "name": col.column_name,
                            "type": col.data_type,
                            "nullable": col.is_nullable == 'YES',
                            "default": col.column_default
                        } for col in columns if col.column_name in export_columns]
                    },
                    "data": table_data,
                    "row_count": len(table_data)
                }
                
                logger.info(f"Exported table {table}: {len(table_data)} rows, {len(export_columns)} columns")
                
            except Exception as e:
                logger.warning(f"Could not export table {table}: {e}")
                export_data["tables"][table] = {
                    "error": str(e),
                    "exported": False
                }
        
        # Create JSON content
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sensitive_suffix = "_full" if include_sensitive else "_filtered"
        filename = f"aphrodite_v2_export{sensitive_suffix}_{timestamp}.json"
        
        logger.info(f"Database export completed: {filename} ({len(json_content)} bytes)")
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Error exporting database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export database: {str(e)}")


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
