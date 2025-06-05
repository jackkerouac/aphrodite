# Aphrodite SQLite Migration - Phase 1 Complete

## Overview

Phase 1 of the SQLite migration has been completed. This phase implements the core database structure and services needed to store Aphrodite settings in SQLite instead of YAML files.

## What's Been Implemented

### 1. Database Structure (`app/services/settings_service.py`)

- **SettingsService class**: Core service for managing settings in SQLite
- **Database schema**: Four tables for organized data storage:
  - `settings`: General settings with key-value pairs, types, and categories
  - `api_keys`: Structured storage for API keys by service and group
  - `badge_settings`: Badge configuration settings by type
  - `settings_version`: Version tracking for migration management

### 2. Migration Tools (`tools/migrate_settings.py`)

- **Migration script**: Converts existing YAML files to SQLite database
- **Non-interactive mode**: Suitable for automated deployments
- **Error handling**: Comprehensive error checking and reporting

### 3. Testing Infrastructure

- **Unit tests** (`tests/test_settings_service.py`): Comprehensive test suite for SettingsService
- **Test runner** (`tests/run_tests.py`): Simple test execution script
- **Migration verification** (`tools/verify_migration.py`): Tool to verify successful migration

## Database Schema

```sql
-- Main settings table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT NOT NULL,         -- json, string, integer, float, boolean
    category TEXT NOT NULL,     -- tv_series, metadata_tagging, scheduler, etc.
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys with service grouping
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,      -- Jellyfin, OMDB, TMDB, etc.
    key_name TEXT NOT NULL,     -- url, api_key, user_id, etc.
    value TEXT NOT NULL,
    group_id INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service, key_name, group_id)
);

-- Badge settings by type
CREATE TABLE badge_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_type TEXT NOT NULL,   -- audio, resolution, review, awards
    setting_name TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(badge_type, setting_name)
);

-- Version tracking
CREATE TABLE settings_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Features

### SettingsService Methods

- **General Settings**: `get_setting()`, `set_setting()`, `get_settings_by_category()`
- **API Keys**: `get_api_keys()`, `set_api_key()`, `update_api_keys()`
- **Badge Settings**: `get_badge_settings()`, `update_badge_settings()`
- **Version Management**: `get_current_version()`, `set_version()`
- **Migration Support**: `import_from_yaml()`, `export_to_yaml()`

### Data Type Support

- Automatic type detection and conversion
- Support for: strings, integers, floats, booleans, JSON objects/arrays
- Proper type restoration when retrieving values

### Migration Features

- Preserves existing YAML structure and data
- Handles complex nested configurations (like badge settings)
- Maintains API key groupings and relationships
- Version tracking for future migrations

## Usage Examples

### Basic Settings Operations

```python
from app.services.settings_service import SettingsService

# Initialize service
settings = SettingsService()

# Set a setting
settings.set_setting('tv_series.show_dominant_badges', True, 'tv_series')

# Get a setting
value = settings.get_setting('tv_series.show_dominant_badges')  # Returns True

# Get all settings in a category
tv_settings = settings.get_settings_by_category('tv_series')
```

### API Keys Management

```python
# Update Jellyfin API keys
jellyfin_keys = [
    {
        'url': 'https://jellyfin.example.com',
        'api_key': 'your-api-key',
        'user_id': 'your-user-id'
    }
]
settings.update_api_keys('Jellyfin', jellyfin_keys)

# Retrieve API keys
keys = settings.get_api_keys('Jellyfin')
```

### Migration

```bash
# Migrate from YAML to SQLite
python tools/migrate_settings.py

# Verify migration
python tools/verify_migration.py

# Run tests
python tests/run_tests.py
```

## Testing

Run the test suite to verify everything is working:

```bash
cd E:\programming\aphrodite
python tests/run_tests.py
```

The tests cover:
- Database initialization
- CRUD operations for all setting types
- Type conversion and preservation
- API keys management
- Badge settings management
- Version tracking
- YAML import/export functionality

## Files Created/Modified

### New Files:
- `app/services/settings_service.py` - Core SQLite settings service
- `tools/migrate_settings.py` - Migration script
- `tools/verify_migration.py` - Migration verification tool
- `tests/test_settings_service.py` - Unit tests
- `tests/run_tests.py` - Test runner
- `tests/__init__.py` - Test package initialization
- `data/` directory - Database storage location

### Database:
- `data/aphrodite.db` - SQLite database (created during migration)

## Next Steps

Phase 1 provides the foundation for the SQLite migration. The next phase will implement:

1. **Compatibility Layer**: Wrapper to maintain backward compatibility with existing YAML-based code
2. **Config Service Updates**: Modify the existing ConfigService to use SQLite while maintaining the same API
3. **Automatic Migration Detection**: Logic to automatically detect and perform migration when needed

The current implementation is fully functional and ready for integration with the existing Aphrodite codebase.
