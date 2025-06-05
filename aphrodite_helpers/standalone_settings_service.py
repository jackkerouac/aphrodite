#!/usr/bin/env python3
# aphrodite_helpers/standalone_settings_service.py
# Standalone version of SettingsService that doesn't require Flask

import sqlite3
import json
import os
import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StandaloneSettingsService:
    """Standalone settings service for use outside Flask context"""
    
    def __init__(self, db_path=None):
        """Initialize the settings service with a database path"""
        if db_path is None:
            # Use default path based on environment
            is_docker = os.path.exists('/.dockerenv')
            if is_docker:
                self.db_path = '/app/data/aphrodite.db'
            else:
                base_dir = Path(os.path.abspath(__file__)).parents[1]
                self.db_path = os.path.join(base_dir, 'data', 'aphrodite.db')
        else:
            self.db_path = db_path
        
        logger.debug(f"Standalone SettingsService initialized with db_path: {self.db_path}")
    
    def _get_connection(self):
        """Get a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def get_current_version(self):
        """Get the current settings version"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT MAX(version) AS version FROM settings_version')
            row = cursor.fetchone()
            
            conn.close()
            
            if row and row['version'] is not None:
                return row['version']
            return 0
        except Exception as e:
            logger.error(f"Error getting current version: {e}")
            return 0
    
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
