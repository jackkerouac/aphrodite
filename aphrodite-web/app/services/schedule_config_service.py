import os
import yaml
import logging
from pathlib import Path
import re
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class ScheduleConfigService:
    """Service for managing schedule configurations."""
    
    def __init__(self, base_dir=None):
        """Initialize the schedule config service."""
        # Set up base directory
        if base_dir is None:
            is_docker = (
                os.path.exists('/app') and 
                os.path.exists('/app/settings.yaml') and 
                os.path.exists('/.dockerenv')
            )
            
            if is_docker:
                self.base_dir = Path('/app')
            else:
                self.base_dir = Path(os.path.abspath(__file__)).parents[3]
        else:
            self.base_dir = Path(base_dir)
        
        # Schedule configuration file
        self.schedules_file = self.base_dir / 'schedule_settings.yml'
        
        logger.info(f"Schedule config service initialized with base directory: {self.base_dir}")
    
    def get_scheduler_config(self):
        """Get scheduler configuration from settings."""
        try:
            settings_file = self.base_dir / 'settings.yaml'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = yaml.safe_load(f)
                    
                return settings.get('scheduler', {
                    'enabled': True,
                    'timezone': 'UTC',
                    'max_concurrent_jobs': 1,
                    'job_history_limit': 50
                })
        except Exception as e:
            logger.error(f"Error reading scheduler config: {e}")
        
        # Return default config
        return {
            'enabled': True,
            'timezone': 'UTC',
            'max_concurrent_jobs': 1,
            'job_history_limit': 50
        }
    
    def get_schedules(self):
        """Get all schedule configurations."""
        if not self.schedules_file.exists():
            return []
        
        try:
            with open(self.schedules_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('schedules', [])
        except Exception as e:
            logger.error(f"Error reading schedules file: {e}")
            return []
    
    def save_schedules(self, schedules):
        """Save schedule configurations."""
        try:
            data = {'schedules': schedules}
            with open(self.schedules_file, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
            return False
    
    def add_schedule(self, schedule):
        """Add a new schedule configuration."""
        schedules = self.get_schedules()
        
        # Validate schedule
        validation_error = self.validate_schedule(schedule)
        if validation_error:
            raise ValueError(validation_error)
        
        # Check for duplicate IDs
        if any(s.get('id') == schedule.get('id') for s in schedules):
            raise ValueError(f"Schedule with ID '{schedule.get('id')}' already exists")
        
        schedules.append(schedule)
        
        if self.save_schedules(schedules):
            return schedule
        else:
            raise RuntimeError("Failed to save schedule configuration")
    
    def update_schedule(self, schedule_id, updated_schedule):
        """Update an existing schedule configuration."""
        schedules = self.get_schedules()
        
        # Find the schedule to update
        schedule_index = None
        for i, schedule in enumerate(schedules):
            if schedule.get('id') == schedule_id:
                schedule_index = i
                break
        
        if schedule_index is None:
            raise ValueError(f"Schedule with ID '{schedule_id}' not found")
        
        # Validate updated schedule
        validation_error = self.validate_schedule(updated_schedule)
        if validation_error:
            raise ValueError(validation_error)
        
        # Ensure ID matches
        updated_schedule['id'] = schedule_id
        
        # Update the schedule
        schedules[schedule_index] = updated_schedule
        
        if self.save_schedules(schedules):
            return updated_schedule
        else:
            raise RuntimeError("Failed to save schedule configuration")
    
    def remove_schedule(self, schedule_id):
        """Remove a schedule configuration."""
        schedules = self.get_schedules()
        
        # Filter out the schedule to remove
        updated_schedules = [s for s in schedules if s.get('id') != schedule_id]
        
        if len(updated_schedules) == len(schedules):
            raise ValueError(f"Schedule with ID '{schedule_id}' not found")
        
        if self.save_schedules(updated_schedules):
            return True
        else:
            raise RuntimeError("Failed to save schedule configuration")
    
    def get_schedule(self, schedule_id):
        """Get a specific schedule configuration."""
        schedules = self.get_schedules()
        
        for schedule in schedules:
            if schedule.get('id') == schedule_id:
                return schedule
        
        return None
    
    def validate_schedule(self, schedule):
        """Validate a schedule configuration."""
        if not isinstance(schedule, dict):
            return "Schedule must be a dictionary"
        
        # Required fields
        required_fields = ['name', 'cron', 'processing_options']
        for field in required_fields:
            if field not in schedule:
                return f"Missing required field: {field}"
        
        # Validate cron expression
        cron_error = self.validate_cron_expression(schedule['cron'])
        if cron_error:
            return f"Invalid cron expression: {cron_error}"
        
        # Validate timezone if provided
        if 'timezone' in schedule:
            try:
                pytz.timezone(schedule['timezone'])
            except pytz.UnknownTimeZoneError:
                return f"Invalid timezone: {schedule['timezone']}"
        
        # Validate processing options
        processing_options = schedule.get('processing_options', {})
        if not isinstance(processing_options, dict):
            return "Processing options must be a dictionary"
        
        # Validate target directories if provided
        target_directories = processing_options.get('target_directories')
        if target_directories is not None:
            if not isinstance(target_directories, list):
                return "Target directories must be a list"
            if not all(isinstance(d, str) for d in target_directories):
                return "All target directories must be strings"
        
        return None
    
    def validate_cron_expression(self, cron_expr):
        """Validate a cron expression."""
        if not isinstance(cron_expr, str):
            return "Cron expression must be a string"
        
        # Split into parts
        parts = cron_expr.strip().split()
        
        if len(parts) != 5:
            return "Cron expression must have exactly 5 parts (minute hour day month day_of_week)"
        
        minute, hour, day, month, day_of_week = parts
        
        # Validate each part
        validations = [
            (minute, 0, 59, "minute"),
            (hour, 0, 23, "hour"),
            (day, 1, 31, "day"),
            (month, 1, 12, "month"),
            (day_of_week, 0, 7, "day_of_week")  # 0 and 7 both represent Sunday
        ]
        
        for part, min_val, max_val, name in validations:
            error = self._validate_cron_part(part, min_val, max_val, name)
            if error:
                return error
        
        return None
    
    def _validate_cron_part(self, part, min_val, max_val, name):
        """Validate a single part of a cron expression."""
        if part == '*':
            return None
        
        # Handle ranges (e.g., "1-5")
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start_num = int(start)
                end_num = int(end)
                
                if start_num < min_val or start_num > max_val:
                    return f"Invalid {name} range start: {start_num} (must be {min_val}-{max_val})"
                
                if end_num < min_val or end_num > max_val:
                    return f"Invalid {name} range end: {end_num} (must be {min_val}-{max_val})"
                
                if start_num > end_num:
                    return f"Invalid {name} range: start ({start_num}) > end ({end_num})"
                
                return None
            except ValueError:
                return f"Invalid {name} range format: {part}"
        
        # Handle step values (e.g., "*/5" or "1-10/2")
        if '/' in part:
            try:
                base, step = part.split('/', 1)
                step_num = int(step)
                
                if step_num <= 0:
                    return f"Invalid {name} step value: {step_num} (must be positive)"
                
                # Validate the base part recursively
                if base != '*':
                    return self._validate_cron_part(base, min_val, max_val, name)
                
                return None
            except ValueError:
                return f"Invalid {name} step format: {part}"
        
        # Handle comma-separated lists (e.g., "1,3,5")
        if ',' in part:
            try:
                values = [int(v.strip()) for v in part.split(',')]
                for value in values:
                    if value < min_val or value > max_val:
                        return f"Invalid {name} value: {value} (must be {min_val}-{max_val})"
                return None
            except ValueError:
                return f"Invalid {name} list format: {part}"
        
        # Handle single numeric values
        try:
            value = int(part)
            if value < min_val or value > max_val:
                return f"Invalid {name} value: {value} (must be {min_val}-{max_val})"
            return None
        except ValueError:
            return f"Invalid {name} format: {part}"
    
    def cron_to_description(self, cron_expr):
        """Convert a cron expression to a human-readable description."""
        try:
            parts = cron_expr.strip().split()
            if len(parts) != 5:
                return cron_expr
            
            minute, hour, day, month, day_of_week = parts
            
            # Simple descriptions for common patterns
            if cron_expr == "0 0 * * *":
                return "Daily at midnight"
            elif cron_expr == "0 2 * * *":
                return "Daily at 2:00 AM"
            elif cron_expr == "0 0 * * 0":
                return "Weekly on Sunday at midnight"
            elif cron_expr == "0 0 1 * *":
                return "Monthly on the 1st at midnight"
            elif minute == "0" and hour != "*" and day == "*" and month == "*" and day_of_week == "*":
                return f"Daily at {hour}:00"
            elif minute != "*" and hour != "*" and day == "*" and month == "*" and day_of_week == "*":
                return f"Daily at {hour}:{minute.zfill(2)}"
            else:
                return f"At {minute} {hour} {day} {month} {day_of_week}"
        except:
            return cron_expr
    
    def get_common_cron_patterns(self):
        """Get a list of common cron patterns with descriptions."""
        return [
            {
                'pattern': '0 2 * * *',
                'description': 'Daily at 2:00 AM',
                'name': 'Daily (2 AM)'
            },
            {
                'pattern': '0 0 * * *',
                'description': 'Daily at midnight',
                'name': 'Daily (midnight)'
            },
            {
                'pattern': '0 6 * * *',
                'description': 'Daily at 6:00 AM',
                'name': 'Daily (6 AM)'
            },
            {
                'pattern': '0 22 * * *',
                'description': 'Daily at 10:00 PM',
                'name': 'Daily (10 PM)'
            },
            {
                'pattern': '0 2 * * 0',
                'description': 'Weekly on Sunday at 2:00 AM',
                'name': 'Weekly (Sunday 2 AM)'
            },
            {
                'pattern': '0 2 * * 1',
                'description': 'Weekly on Monday at 2:00 AM',
                'name': 'Weekly (Monday 2 AM)'
            },
            {
                'pattern': '0 2 1 * *',
                'description': 'Monthly on the 1st at 2:00 AM',
                'name': 'Monthly (1st, 2 AM)'
            },
            {
                'pattern': '0 2 15 * *',
                'description': 'Monthly on the 15th at 2:00 AM',
                'name': 'Monthly (15th, 2 AM)'
            },
            {
                'pattern': '0 */6 * * *',
                'description': 'Every 6 hours',
                'name': 'Every 6 hours'
            },
            {
                'pattern': '0 */12 * * *',
                'description': 'Every 12 hours',
                'name': 'Every 12 hours'
            }
        ]
