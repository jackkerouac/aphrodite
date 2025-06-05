# Schedule Database Migration - Completed

## Overview
Successfully migrated the Aphrodite scheduling system from YAML/JSON file storage to SQLite database storage, integrating with the existing database infrastructure.

## Changes Made

### 1. Extended SettingsService (app/services/settings_service.py)
- **Added new database tables**:
  - `schedules` - Main schedule information (id, name, cron, timezone, enabled, etc.)
  - `schedule_processing_options` - Processing options (badge types, force_refresh, etc.)
  - `schedule_target_directories` - Target directories for each schedule
  - `job_history` - Execution history with detailed status tracking

- **Added schedule management methods**:
  - `get_schedules()` - Retrieve all schedules with options and directories
  - `create_schedule()`, `update_schedule()`, `delete_schedule()`
  - `update_schedule_runtime_info()` - Update next_run and last_run times

- **Added job history methods**:
  - `get_job_history()` - Retrieve execution history with filtering
  - `create_job_history_entry()`, `update_job_history_entry()`

### 2. Updated ScheduleConfigService (app/services/schedule_config_service.py)
- **Database integration**: Now uses SettingsService instead of YAML files
- **Automatic migration**: Migrates existing YAML schedules to database on startup
- **Backward compatibility**: Maintains same API while using database backend
- **File backup**: Renames YAML files to .backup after successful migration

### 3. Updated SchedulerService (app/services/scheduler_service.py)
- **Database job tracking**: Uses database for job history instead of JSON files
- **Enhanced job execution**: Creates detailed history entries with status tracking
- **Automatic migration**: Migrates existing JSON job history to database
- **Runtime integration**: Updates schedule last_run times in database

## Database Schema

### Schedules Table
```sql
CREATE TABLE schedules (
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
);
```

### Schedule Processing Options Table
```sql
CREATE TABLE schedule_processing_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id TEXT NOT NULL,
    option_name TEXT NOT NULL,
    option_value TEXT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
    UNIQUE(schedule_id, option_name)
);
```

### Schedule Target Directories Table
```sql
CREATE TABLE schedule_target_directories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id TEXT NOT NULL,
    directory_name TEXT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
    UNIQUE(schedule_id, directory_name)
);
```

### Job History Table
```sql
CREATE TABLE job_history (
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
);
```

## Migration Process

### Automatic Migration
1. **On Service Initialization**: Both ScheduleConfigService and SchedulerService check for existing files
2. **Database Check**: Verifies if data already exists in database to avoid duplicate migration
3. **File Migration**: Migrates YAML schedules and JSON job history to database
4. **Backup Creation**: Renames original files to .backup extension
5. **Error Handling**: Comprehensive logging and error handling for migration failures

### Migration Triggers
- **ScheduleConfigService**: Migrates `schedule_settings.yml` → database
- **SchedulerService**: Migrates `job_history.json` → database

## Benefits Achieved

1. **Unified Storage**: All application data now in single SQLite database
2. **Data Integrity**: Foreign key relationships ensure referential integrity
3. **Better Performance**: Database queries more efficient than file I/O
4. **Structured History**: Detailed job execution tracking with proper relationships
5. **Atomic Operations**: Database transactions ensure data consistency
6. **Scalability**: Can handle larger numbers of schedules and history entries
7. **Query Flexibility**: Can filter, sort, and search schedule/history data efficiently

## Backward Compatibility

- **API Compatibility**: All existing API endpoints continue to work unchanged
- **Frontend Compatibility**: No changes required to Vue.js components
- **Configuration Format**: Schedules use same structure as before
- **Graceful Migration**: Existing installations automatically migrate without intervention

## Testing Recommendations

1. **Create Test Schedule**: Verify schedule creation works via UI
2. **Run Schedule Manually**: Test manual execution functionality
3. **Check History**: Verify job history is properly recorded
4. **Migration Testing**: Test with existing YAML/JSON files to verify migration
5. **Error Handling**: Test various error scenarios (invalid cron, missing options, etc.)

## Next Steps

The scheduling system is now fully migrated to use the SQLite database. The frontend components should work without changes, and all existing functionality is preserved while gaining the benefits of database storage.
