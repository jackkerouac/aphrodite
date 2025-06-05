# app/services/settings_service.py

import sqlite3
import json
import os
import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SettingsService:
    """Service for managing settings in SQLite database"""
    
    def __init__(self, db_path=None):
        """Initialize the settings service with a database path"""
        if db_path is None:
            # Use default path based on environment
            is_docker = os.path.exists('/.dockerenv')
            if is_docker:
                self.db_path = '/app/data/aphrodite.db'
            else:
                base_dir = Path(os.path.abspath(__file__)).parents[3]
                self.db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
        else:
            self.db_path = db_path
            
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
    def _init_db(self):
        """Initialize the database schema if it doesn't exist"""
        logger.info(f"DEBUG: Initializing database at {self.db_path}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logger.info("DEBUG: Created/verified settings table")
            
            # Create API keys table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                key_name TEXT NOT NULL,
                value TEXT NOT NULL,
                group_id INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service, key_name, group_id)
            )
            ''')
            logger.info("DEBUG: Created/verified api_keys table")
            
            # Create badge settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS badge_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                badge_type TEXT NOT NULL,
                setting_name TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(badge_type, setting_name)
            )
            ''')
            logger.info("DEBUG: Created/verified badge_settings table")
            
            # Create version table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logger.info("DEBUG: Created/verified settings_version table")
            
            # Create application version table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_version TEXT NOT NULL,
                latest_version TEXT,
                update_available BOOLEAN DEFAULT 0,
                release_notes TEXT,
                release_url TEXT,
                published_at TEXT,
                check_successful BOOLEAN DEFAULT 0,
                error_message TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logger.info("DEBUG: Created/verified app_version table")
            
            # Create schedules table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                cron_expression TEXT NOT NULL,
                timezone TEXT NOT NULL DEFAULT 'UTC',
                enabled BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run_at TIMESTAMP,
                next_run_at TIMESTAMP
            )
            ''')
            logger.info("DEBUG: Created/verified schedules table")
            
            # Create schedule processing options table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_processing_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL,
                option_name TEXT NOT NULL,
                option_value TEXT NOT NULL,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
                UNIQUE(schedule_id, option_name)
            )
            ''')
            logger.info("DEBUG: Created/verified schedule_processing_options table")
            
            # Create schedule target directories table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_target_directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL,
                directory_name TEXT NOT NULL,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
                UNIQUE(schedule_id, directory_name)
            )
            ''')
            logger.info("DEBUG: Created/verified schedule_target_directories table")
            
            # Create job execution history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL,
                job_id TEXT,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                message TEXT,
                error_details TEXT,
                workflow_id TEXT,
                result_data TEXT,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
            )
            ''')
            logger.info("DEBUG: Created/verified job_history table")
            
            conn.commit()
            conn.close()
            logger.info("DEBUG: Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"DEBUG: Error initializing database: {e}")
            import traceback
            logger.error(f"DEBUG: Database init traceback: {traceback.format_exc()}")
            if 'conn' in locals():
                conn.close()
            raise
    
    def _get_connection(self):
        """Get a database connection"""
        try:
            logger.debug(f"DEBUG: Connecting to database at {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            logger.debug("DEBUG: Database connection successful")
            return conn
        except Exception as e:
            logger.error(f"DEBUG: Error connecting to database: {e}")
            raise
    
    # General settings methods
    
    def get_setting(self, key, default=None):
        """Get a setting value by key"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return default
        
        value = row['value']
        value_type = row['type']
        
        # Convert value based on type
        if value_type == 'json':
            value = json.loads(value)
        elif value_type == 'integer':
            value = int(value)
        elif value_type == 'float':
            value = float(value)
        elif value_type == 'boolean':
            value = value.lower() == 'true'
        
        conn.close()
        return value
    
    def set_setting(self, key, value, category, description=None):
        """Set a setting value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Determine value type
        if isinstance(value, dict) or isinstance(value, list):
            value_type = 'json'
            value = json.dumps(value)
        elif isinstance(value, bool):
            value_type = 'boolean'
            value = str(value).lower()
        elif isinstance(value, int):
            value_type = 'integer'
            value = str(value)
        elif isinstance(value, float):
            value_type = 'float'
            value = str(value)
        else:
            value_type = 'string'
            value = str(value)
        
        # Insert or update the setting
        cursor.execute('''
        INSERT INTO settings (key, value, type, category, description, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            type = excluded.type,
            category = excluded.category,
            description = excluded.description,
            updated_at = excluded.updated_at
        ''', (
            key, value, value_type, category, description,
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_settings_by_category(self, category):
        """Get all settings in a category"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM settings WHERE category = ?', (category,))
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            key = row['key']
            value = row['value']
            value_type = row['type']
            
            # Convert value based on type
            if value_type == 'json':
                value = json.loads(value)
            elif value_type == 'integer':
                value = int(value)
            elif value_type == 'float':
                value = float(value)
            elif value_type == 'boolean':
                value = value.lower() == 'true'
            
            result[key] = value
        
        conn.close()
        return result
    
    def delete_setting(self, key):
        """Delete a setting by key"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        
        conn.commit()
        conn.close()
    
    def delete_settings_by_category(self, category):
        """Delete all settings in a category"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM settings WHERE category = ?', (category,))
        
        conn.commit()
        conn.close()
    
    # API keys methods
    
    def get_api_keys(self, service=None):
        """Get all API keys for a service, or all services if none specified"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if service:
            cursor.execute('SELECT * FROM api_keys WHERE service = ? ORDER BY group_id, id', (service,))
        else:
            cursor.execute('SELECT * FROM api_keys ORDER BY service, group_id, id')
        
        rows = cursor.fetchall()
        
        # Organize API keys by service and group
        result = {}
        for row in rows:
            service_name = row['service']
            key_name = row['key_name']
            value = row['value']
            group_id = row['group_id']
            
            if service_name not in result:
                result[service_name] = []
            
            # Ensure the group exists
            while len(result[service_name]) <= group_id:
                result[service_name].append({})
            
            # Add the key to the group
            result[service_name][group_id][key_name] = value
        
        conn.close()
        
        # Return just the service if specified
        if service and service in result:
            return result[service]
        
        return result
    
    def set_api_key(self, service, key_name, value, group_id=0):
        """Set an API key value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO api_keys (service, key_name, value, group_id, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(service, key_name, group_id) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        ''', (
            service, key_name, value, group_id,
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_api_keys(self, service, keys_data):
        """Update all API keys for a service"""
        logger.info(f"DEBUG: SettingsService.update_api_keys called for {service} with data: {keys_data}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, delete all existing keys for this service
            logger.info(f"DEBUG: Deleting existing API keys for {service}")
            cursor.execute('DELETE FROM api_keys WHERE service = ?', (service,))
            deleted_count = cursor.rowcount
            logger.info(f"DEBUG: Deleted {deleted_count} existing API keys for {service}")
            
            # Then insert the new keys
            logger.info(f"DEBUG: Inserting new API keys for {service}")
            for group_id, group_data in enumerate(keys_data):
                logger.info(f"DEBUG: Processing group {group_id}: {group_data}")
                for key_name, value in group_data.items():
                    logger.info(f"DEBUG: Inserting {key_name}={value} for {service} group {group_id}")
                    cursor.execute('''
                    INSERT INTO api_keys (service, key_name, value, group_id, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        service, key_name, value, group_id,
                        datetime.datetime.now().isoformat()
                    ))
            
            conn.commit()
            logger.info(f"DEBUG: Successfully committed API keys for {service}")
            conn.close()
        except Exception as e:
            logger.error(f"DEBUG: Error in update_api_keys for {service}: {e}")
            if 'conn' in locals():
                conn.close()
            raise
    
    # Badge settings methods
    
    def get_badge_settings(self, badge_type):
        """Get all settings for a badge type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM badge_settings WHERE badge_type = ?', (badge_type,))
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            setting_name = row['setting_name']
            value = row['value']
            
            # Try to parse as JSON first (for nested structures)
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Try to convert value if it's a number or boolean
                try:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and all(p.isdigit() for p in value.split('.', 1)):
                        value = float(value)
                except (ValueError, AttributeError):
                    pass
            
            result[setting_name] = value
        
        conn.close()
        return result
    
    def update_badge_settings(self, badge_type, settings_data):
        """Update all settings for a badge type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # First, delete all existing settings for this badge type
        cursor.execute('DELETE FROM badge_settings WHERE badge_type = ?', (badge_type,))
        
        # Then insert the new settings
        for setting_name, value in settings_data.items():
            # Convert value to string
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            else:
                value = str(value)
            
            cursor.execute('''
            INSERT INTO badge_settings (badge_type, setting_name, value, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (
                badge_type, setting_name, value,
                datetime.datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    # Version methods
    
    def get_current_settings_version(self):
        """Get the current settings version"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT MAX(version) AS version FROM settings_version')
            row = cursor.fetchone()
            
            conn.close()
            
            if row and row['version'] is not None:
                version = row['version']
                logger.info(f"DEBUG: Current database version: {version}")
                return version
            
            logger.info("DEBUG: No version found in database, returning 0")
            return 0
        except Exception as e:
            logger.error(f"DEBUG: Error getting current version: {e}")
            if 'conn' in locals():
                conn.close()
            return 0
    
    # Backward compatibility
    def get_current_version(self):
        """Backward compatibility method for settings version"""
        return self.get_current_settings_version()
    
    def set_settings_version(self, version):
        """Set the settings version"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO settings_version (version, applied_at)
        VALUES (?, ?)
        ''', (
            version,
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    # Backward compatibility
    def set_version(self, version):
        """Backward compatibility method for settings version"""
        return self.set_settings_version(version)
    
    # Migration helper methods
    
    def import_from_yaml(self, yaml_data, category):
        """Import settings from YAML data for a specific category"""
        if category in yaml_data:
            category_data = yaml_data[category]
            
            # Handle nested structures
            if isinstance(category_data, dict):
                for key, value in category_data.items():
                    full_key = f"{category}.{key}"
                    self.set_setting(full_key, value, category)
            else:
                self.set_setting(category, category_data, category)
    
    def export_to_yaml(self):
        """Export all settings to YAML format"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all settings
        cursor.execute('SELECT * FROM settings')
        settings_rows = cursor.fetchall()
        
        # Get all API keys
        cursor.execute('SELECT * FROM api_keys ORDER BY service, group_id, id')
        api_keys_rows = cursor.fetchall()
        
        # Get all badge settings
        cursor.execute('SELECT * FROM badge_settings ORDER BY badge_type, setting_name')
        badge_settings_rows = cursor.fetchall()
        
        conn.close()
        
        # Build the YAML structure
        result = {}
        
        # Process regular settings
        for row in settings_rows:
            key = row['key']
            value = row['value']
            value_type = row['type']
            category = row['category']
            
            # Convert value based on type
            if value_type == 'json':
                value = json.loads(value)
            elif value_type == 'integer':
                value = int(value)
            elif value_type == 'float':
                value = float(value)
            elif value_type == 'boolean':
                value = value.lower() == 'true'
            
            # Handle nested keys
            if '.' in key:
                parts = key.split('.')
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                result[key] = value
        
        # Process API keys
        api_keys = {}
        for row in api_keys_rows:
            service = row['service']
            key_name = row['key_name']
            value = row['value']
            group_id = row['group_id']
            
            if service not in api_keys:
                api_keys[service] = []
            
            # Ensure the group exists
            while len(api_keys[service]) <= group_id:
                api_keys[service].append({})
            
            # Add the key to the group
            api_keys[service][group_id][key_name] = value
        
        result['api_keys'] = api_keys
        
        # Process badge settings (these will be separate files)
        badge_settings = {}
        for row in badge_settings_rows:
            badge_type = row['badge_type']
            setting_name = row['setting_name']
            value = row['value']
            
            # Try to parse as JSON first
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Try to convert value if it's a number or boolean
                try:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and all(p.isdigit() for p in value.split('.', 1)):
                        value = float(value)
                except (ValueError, AttributeError):
                    pass
            
            if badge_type not in badge_settings:
                badge_settings[badge_type] = {}
            
            badge_settings[badge_type][setting_name] = value
        
        return result, badge_settings
    
    # Application version methods
    
    def get_app_version_info(self):
        """Get the current application version information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM app_version ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'current_version': row['current_version'],
                'latest_version': row['latest_version'],
                'update_available': bool(row['update_available']),
                'release_notes': row['release_notes'],
                'release_url': row['release_url'],
                'published_at': row['published_at'],
                'check_successful': bool(row['check_successful']),
                'error': row['error_message'],
                'last_checked': row['last_checked']
            }
        
        return None
    
    def set_app_version_info(self, version_info):
        """Store application version information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO app_version (
            current_version, latest_version, update_available, 
            release_notes, release_url, published_at, 
            check_successful, error_message, last_checked, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_info.get('current_version'),
            version_info.get('latest_version'),
            version_info.get('update_available', False),
            version_info.get('release_notes'),
            version_info.get('release_url'),
            version_info.get('published_at'),
            version_info.get('check_successful', False),
            version_info.get('error'),
            version_info.get('last_checked', datetime.datetime.now().isoformat()),
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_app_version_info(self, version_info):
        """Update the latest application version information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Delete all previous entries and insert the new one
        cursor.execute('DELETE FROM app_version')
        
        cursor.execute('''
        INSERT INTO app_version (
            current_version, latest_version, update_available, 
            release_notes, release_url, published_at, 
            check_successful, error_message, last_checked, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_info.get('current_version'),
            version_info.get('latest_version'),
            version_info.get('update_available', False),
            version_info.get('release_notes'),
            version_info.get('release_url'),
            version_info.get('published_at'),
            version_info.get('check_successful', False),
            version_info.get('error'),
            version_info.get('last_checked', datetime.datetime.now().isoformat()),
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def set_current_app_version(self, version):
        """Set the current application version"""
        # First check if we have any version info
        existing_info = self.get_app_version_info()
        
        if existing_info:
            # Update the current version
            existing_info['current_version'] = version
            self.update_app_version_info(existing_info)
        else:
            # Create new entry with just the current version
            version_info = {
                'current_version': version,
                'latest_version': None,
                'update_available': False,
                'release_notes': None,
                'release_url': None,
                'published_at': None,
                'check_successful': False,
                'error': None,
                'last_checked': datetime.datetime.now().isoformat()
            }
            self.set_app_version_info(version_info)
    
    # Schedule management methods
    
    def get_schedules(self):
        """Get all schedules with their processing options and target directories"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all schedules
        cursor.execute('SELECT * FROM schedules ORDER BY name')
        schedule_rows = cursor.fetchall()
        
        schedules = []
        for row in schedule_rows:
            schedule = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'cron': row['cron_expression'],
                'timezone': row['timezone'],
                'enabled': bool(row['enabled']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'last_run': row['last_run_at'],
                'next_run': row['next_run_at']
            }
            
            # Get processing options
            cursor.execute('SELECT option_name, option_value FROM schedule_processing_options WHERE schedule_id = ?', (row['id'],))
            option_rows = cursor.fetchall()
            
            processing_options = {}
            for option_row in option_rows:
                option_name = option_row['option_name']
                option_value = option_row['option_value']
                
                # Try to parse as boolean/number
                if option_value.lower() == 'true':
                    option_value = True
                elif option_value.lower() == 'false':
                    option_value = False
                elif option_value.isdigit():
                    option_value = int(option_value)
                
                processing_options[option_name] = option_value
            
            # Get target directories
            cursor.execute('SELECT directory_name FROM schedule_target_directories WHERE schedule_id = ? ORDER BY directory_name', (row['id'],))
            dir_rows = cursor.fetchall()
            processing_options['target_directories'] = [dir_row['directory_name'] for dir_row in dir_rows]
            
            schedule['processing_options'] = processing_options
            schedules.append(schedule)
        
        conn.close()
        return schedules
    
    def get_schedule(self, schedule_id):
        """Get a specific schedule by ID"""
        schedules = self.get_schedules()
        for schedule in schedules:
            if schedule['id'] == schedule_id:
                return schedule
        return None
    
    def create_schedule(self, schedule_data):
        """Create a new schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert schedule
            cursor.execute('''
            INSERT INTO schedules (
                id, name, description, cron_expression, timezone, enabled, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_data['id'],
                schedule_data['name'],
                schedule_data.get('description'),
                schedule_data['cron'],
                schedule_data.get('timezone', 'UTC'),
                schedule_data.get('enabled', True),
                datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat()
            ))
            
            # Insert processing options
            processing_options = schedule_data.get('processing_options', {})
            target_directories = processing_options.pop('target_directories', [])
            
            for option_name, option_value in processing_options.items():
                cursor.execute('''
                INSERT INTO schedule_processing_options (schedule_id, option_name, option_value)
                VALUES (?, ?, ?)
                ''', (schedule_data['id'], option_name, str(option_value)))
            
            # Insert target directories
            for directory in target_directories:
                cursor.execute('''
                INSERT INTO schedule_target_directories (schedule_id, directory_name)
                VALUES (?, ?)
                ''', (schedule_data['id'], directory))
            
            conn.commit()
            return schedule_data
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_schedule(self, schedule_id, schedule_data):
        """Update an existing schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Update schedule
            cursor.execute('''
            UPDATE schedules SET
                name = ?, description = ?, cron_expression = ?, timezone = ?,
                enabled = ?, updated_at = ?
            WHERE id = ?
            ''', (
                schedule_data['name'],
                schedule_data.get('description'),
                schedule_data['cron'],
                schedule_data.get('timezone', 'UTC'),
                schedule_data.get('enabled', True),
                datetime.datetime.now().isoformat(),
                schedule_id
            ))
            
            # Delete existing processing options and directories
            cursor.execute('DELETE FROM schedule_processing_options WHERE schedule_id = ?', (schedule_id,))
            cursor.execute('DELETE FROM schedule_target_directories WHERE schedule_id = ?', (schedule_id,))
            
            # Insert new processing options
            processing_options = schedule_data.get('processing_options', {})
            target_directories = processing_options.pop('target_directories', [])
            
            for option_name, option_value in processing_options.items():
                cursor.execute('''
                INSERT INTO schedule_processing_options (schedule_id, option_name, option_value)
                VALUES (?, ?, ?)
                ''', (schedule_id, option_name, str(option_value)))
            
            # Insert new target directories
            for directory in target_directories:
                cursor.execute('''
                INSERT INTO schedule_target_directories (schedule_id, directory_name)
                VALUES (?, ?)
                ''', (schedule_id, directory))
            
            conn.commit()
            schedule_data['id'] = schedule_id
            return schedule_data
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_schedule(self, schedule_id):
        """Delete a schedule and all related data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if schedule exists
            cursor.execute('SELECT id FROM schedules WHERE id = ?', (schedule_id,))
            if not cursor.fetchone():
                raise ValueError(f"Schedule with ID '{schedule_id}' not found")
            
            # Delete related data (cascade should handle this, but be explicit)
            cursor.execute('DELETE FROM schedule_processing_options WHERE schedule_id = ?', (schedule_id,))
            cursor.execute('DELETE FROM schedule_target_directories WHERE schedule_id = ?', (schedule_id,))
            cursor.execute('DELETE FROM job_history WHERE schedule_id = ?', (schedule_id,))
            
            # Delete schedule
            cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_schedule_runtime_info(self, schedule_id, next_run=None, last_run=None):
        """Update schedule runtime information (next_run, last_run)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if next_run is not None:
            updates.append('next_run_at = ?')
            params.append(next_run)
        
        if last_run is not None:
            updates.append('last_run_at = ?')
            params.append(last_run)
        
        if updates:
            updates.append('updated_at = ?')
            params.append(datetime.datetime.now().isoformat())
            params.append(schedule_id)
            
            cursor.execute(f'''
            UPDATE schedules SET {', '.join(updates)}
            WHERE id = ?
            ''', params)
            
            conn.commit()
        
        conn.close()
    
    # Job history methods
    
    def get_job_history(self, schedule_id=None, limit=None):
        """Get job execution history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM job_history'
        params = []
        
        if schedule_id:
            query += ' WHERE schedule_id = ?'
            params.append(schedule_id)
        
        query += ' ORDER BY started_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history_item = {
                'id': row['id'],
                'schedule_id': row['schedule_id'],
                'job_id': row['job_id'],
                'status': row['status'],
                'started_at': row['started_at'],
                'completed_at': row['completed_at'],
                'duration': row['duration_seconds'],
                'message': row['message'],
                'error': row['error_details'],
                'workflow_id': row['workflow_id'],
                'result': row['result_data']
            }
            history.append(history_item)
        
        conn.close()
        return history
    
    def create_job_history_entry(self, schedule_id, job_id=None, status='running', 
                                message=None, workflow_id=None):
        """Create a new job history entry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO job_history (
            schedule_id, job_id, status, started_at, message, workflow_id
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            schedule_id, job_id, status, datetime.datetime.now().isoformat(),
            message, workflow_id
        ))
        
        job_history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_history_id
    
    def update_job_history_entry(self, job_history_id, status=None, message=None,
                                error_details=None, result_data=None):
        """Update a job history entry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
            
            if status in ['success', 'failed']:
                updates.append('completed_at = ?')
                params.append(datetime.datetime.now().isoformat())
                
                # Calculate duration
                cursor.execute('SELECT started_at FROM job_history WHERE id = ?', (job_history_id,))
                row = cursor.fetchone()
                if row:
                    started_at = datetime.datetime.fromisoformat(row['started_at'])
                    completed_at = datetime.datetime.now()
                    duration = (completed_at - started_at).total_seconds()
                    updates.append('duration_seconds = ?')
                    params.append(duration)
        
        if message is not None:
            updates.append('message = ?')
            params.append(message)
        
        if error_details is not None:
            updates.append('error_details = ?')
            params.append(error_details)
        
        if result_data is not None:
            if isinstance(result_data, (dict, list)):
                result_data = json.dumps(result_data)
            updates.append('result_data = ?')
            params.append(result_data)
        
        if updates:
            params.append(job_history_id)
            
            cursor.execute(f'''
            UPDATE job_history SET {', '.join(updates)}
            WHERE id = ?
            ''', params)
            
            conn.commit()
        
        conn.close()
