"""
Database Backup and Restore for Aphrodite

Provides comprehensive backup and restore capabilities for the Aphrodite database,
including processing history, settings, and all tracking data.
"""

import sqlite3
import json
import os
import shutil
import gzip
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DatabaseBackup:
    """
    Handles database backup and restore operations for Aphrodite.
    
    Features:
    - Full database backup with compression
    - Selective table backup/restore
    - Export to JSON for portability
    - Backup verification and integrity checks
    - Automated backup rotation
    """
    
    def __init__(self, db_path: str = "data/aphrodite.db"):
        self.db_path = db_path
        self.backup_dir = "data/backups"
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self, compress: bool = True, 
                          include_timestamp: bool = True) -> str:
        """
        Create a complete backup of the database.
        
        Args:
            compress: Whether to compress the backup
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to the backup file
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        base_name = f"aphrodite_backup_{timestamp}" if timestamp else "aphrodite_backup"
        
        if compress:
            backup_path = os.path.join(self.backup_dir, f"{base_name}.db.gz")
            
            # Create compressed backup
            with open(self.db_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            backup_path = os.path.join(self.backup_dir, f"{base_name}.db")
            shutil.copy2(self.db_path, backup_path)
        
        # Verify backup
        backup_size = os.path.getsize(backup_path)
        original_size = os.path.getsize(self.db_path)
        
        print(f"✅ Database backup created: {backup_path}")
        print(f"   Original size: {self._format_size(original_size)}")
        print(f"   Backup size:   {self._format_size(backup_size)}")
        
        if compress:
            compression_ratio = (1 - backup_size / original_size) * 100
            print(f"   Compression:   {compression_ratio:.1f}%")
        
        return backup_path
    
    def restore_from_backup(self, backup_path: str, 
                           confirm: bool = False) -> bool:
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to the backup file
            confirm: Whether to proceed without confirmation
            
        Returns:
            True if restore successful, False otherwise
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Safety check
        if not confirm:
            print(f"⚠️ This will REPLACE the current database with the backup.")
            print(f"   Current database: {self.db_path}")
            print(f"   Backup file:      {backup_path}")
            response = input("Continue? (yes/no): ").lower().strip()
            if response != 'yes':
                print("Restore cancelled.")
                return False
        
        try:
            # Create backup of current database first
            if os.path.exists(self.db_path):
                current_backup = self.create_full_backup()
                print(f"📦 Current database backed up to: {current_backup}")
            
            # Restore from backup
            if backup_path.endswith('.gz'):
                # Decompress and restore
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Direct copy
                shutil.copy2(backup_path, self.db_path)
            
            # Verify restored database
            if self._verify_database_integrity():
                print(f"✅ Database successfully restored from: {backup_path}")
                return True
            else:
                print(f"❌ Database restore failed - integrity check failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during restore: {e}")
            return False
    
    def export_to_json(self, output_path: Optional[str] = None, 
                      include_sensitive: bool = False) -> str:
        """
        Export database to JSON format for portability.
        
        Args:
            output_path: Custom output path (optional)
            include_sensitive: Whether to include sensitive data like API keys
            
        Returns:
            Path to the exported JSON file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.backup_dir, f"aphrodite_export_{timestamp}.json")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        export_data = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "database_path": self.db_path,
                "include_sensitive": include_sensitive,
                "aphrodite_version": self._get_app_version()
            },
            "tables": {}
        }
        
        try:
            # Get all tables
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Export each table
            for table_name in tables:
                # Skip sensitive tables if not including sensitive data
                if not include_sensitive and table_name in ['api_keys']:
                    continue
                
                cursor = conn.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                table_data = []
                for row in rows:
                    row_dict = dict(row)
                    
                    # Parse JSON fields where applicable
                    if table_name == 'processed_items':
                        json_fields = ['external_ids', 'badges_requested', 'badges_applied', 'metadata_sources_used']
                        for field in json_fields:
                            if row_dict.get(field):
                                try:
                                    row_dict[field] = json.loads(row_dict[field])
                                except json.JSONDecodeError:
                                    pass
                    
                    table_data.append(row_dict)
                
                export_data["tables"][table_name] = {
                    "row_count": len(table_data),
                    "data": table_data
                }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Database exported to JSON: {output_path}")
            print(f"   File size: {self._format_size(file_size)}")
            print(f"   Tables exported: {len(export_data['tables'])}")
            
            return output_path
            
        finally:
            conn.close()
    
    def import_from_json(self, json_path: str, 
                        tables_to_import: Optional[List[str]] = None,
                        merge_mode: bool = False) -> bool:
        """
        Import database from JSON export.
        
        Args:
            json_path: Path to the JSON export file
            tables_to_import: List of specific tables to import (None for all)
            merge_mode: If True, merge with existing data; if False, replace
            
        Returns:
            True if import successful, False otherwise
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "tables" not in import_data:
                raise ValueError("Invalid JSON format - missing 'tables' key")
            
            conn = sqlite3.connect(self.db_path)
            
            imported_tables = []
            
            for table_name, table_info in import_data["tables"].items():
                if tables_to_import and table_name not in tables_to_import:
                    continue
                
                # Check if table exists
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if not cursor.fetchone():
                    print(f"⚠️ Table '{table_name}' does not exist in target database - skipping")
                    continue
                
                # Clear existing data if not in merge mode
                if not merge_mode:
                    conn.execute(f"DELETE FROM {table_name}")
                
                # Insert data
                data_rows = table_info.get("data", [])
                if data_rows:
                    # Get column names from first row
                    columns = list(data_rows[0].keys())
                    
                    # Prepare insert statement
                    placeholders = ",".join(["?" for _ in columns])
                    insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    # Insert rows
                    for row in data_rows:
                        values = []
                        for col in columns:
                            value = row[col]
                            # Convert dictionaries back to JSON strings
                            if isinstance(value, (dict, list)):
                                value = json.dumps(value)
                            values.append(value)
                        
                        conn.execute(insert_sql, values)
                
                imported_tables.append(table_name)
                print(f"✅ Imported {len(data_rows)} rows into table '{table_name}'")
            
            conn.commit()
            conn.close()
            
            print(f"✅ JSON import completed. Tables imported: {', '.join(imported_tables)}")
            return True
            
        except Exception as e:
            print(f"❌ Error during JSON import: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("aphrodite_backup_") and (filename.endswith(".db") or filename.endswith(".db.gz")):
                file_path = os.path.join(self.backup_dir, filename)
                stat_info = os.stat(file_path)
                
                backups.append({
                    "filename": filename,
                    "path": file_path,
                    "size": stat_info.st_size,
                    "size_formatted": self._format_size(stat_info.st_size),
                    "created": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "compressed": filename.endswith(".gz")
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups removed
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        backups_to_remove = backups[keep_count:]
        removed_count = 0
        
        for backup in backups_to_remove:
            try:
                os.remove(backup["path"])
                print(f"🗑️ Removed old backup: {backup['filename']}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Failed to remove {backup['filename']}: {e}")
        
        print(f"✅ Cleanup completed. Removed {removed_count} old backups, keeping {keep_count} most recent.")
        return removed_count
    
    def verify_backup(self, backup_path: str) -> bool:
        """
        Verify the integrity of a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if backup is valid, False otherwise
        """
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            # Create temporary file for verification
            temp_db = "temp_verify.db"
            
            if backup_path.endswith('.gz'):
                # Decompress to temporary file
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, temp_db)
            
            # Verify database integrity
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            # Cleanup temporary file
            os.remove(temp_db)
            
            if result == "ok":
                print(f"✅ Backup verification passed: {backup_path}")
                return True
            else:
                print(f"❌ Backup verification failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying backup: {e}")
            # Cleanup temporary file if it exists
            if os.path.exists("temp_verify.db"):
                os.remove("temp_verify.db")
            return False
    
    def _verify_database_integrity(self) -> bool:
        """Verify the integrity of the current database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            return result == "ok"
        except Exception:
            return False
    
    def _get_app_version(self) -> str:
        """Get the current Aphrodite version."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT version FROM app_version ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else "unknown"
        except Exception:
            return "unknown"
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


# Standalone functions for command-line usage
def create_backup(compress: bool = True) -> str:
    """Create a database backup."""
    backup = DatabaseBackup()
    return backup.create_full_backup(compress=compress)


def restore_backup(backup_path: str, confirm: bool = False) -> bool:
    """Restore from a backup file."""
    backup = DatabaseBackup()
    return backup.restore_from_backup(backup_path, confirm=confirm)


def list_available_backups() -> List[Dict[str, Any]]:
    """List all available backups."""
    backup = DatabaseBackup()
    return backup.list_backups()


def export_database_to_json(output_path: Optional[str] = None) -> str:
    """Export database to JSON format."""
    backup = DatabaseBackup()
    return backup.export_to_json(output_path)


def cleanup_old_backups(keep_count: int = 10) -> int:
    """Clean up old backup files."""
    backup = DatabaseBackup()
    return backup.cleanup_old_backups(keep_count)
