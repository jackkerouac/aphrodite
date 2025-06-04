#!/bin/bash
set -e

# Function to log with timestamp
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_msg "Starting Aphrodite container initialization..."

# Set default PUID/PGID if not provided
PUID=${PUID:-1000}
PGID=${PGID:-1000}

# Function to setup user and permissions
setup_user() {
    log_msg "Setting up user with PUID=$PUID and PGID=$PGID"
    
    # Create group with specified GID if it doesn't exist
    if ! getent group aphrodite >/dev/null 2>&1; then
        groupadd -g "${PGID}" aphrodite
    else
        # Update existing group
        groupmod -o -g "${PGID}" aphrodite
    fi
    
    # Create user with specified UID if it doesn't exist
    if ! getent passwd aphrodite >/dev/null 2>&1; then
        useradd -o -u "${PUID}" -g aphrodite -s /bin/bash -d /app aphrodite
    else
        # Update existing user
        usermod -o -u "${PUID}" -g "${PGID}" aphrodite
    fi
    
    # Create required directories
    log_msg "Creating required directories..."
    mkdir -p /app/posters/original /app/posters/working /app/posters/modified /app/data /app/config
    
    # Set ownership and permissions only for necessary directories (not the entire /app)
    log_msg "Setting ownership for mounted directories..."
    chown -R "${PUID}":"${PGID}" /app/posters /app/data /app/config
    chmod -R 775 /app/posters /app/data /app/config
    
    # Only change ownership of essential app files, not everything
    log_msg "Setting ownership for essential app files..."
    chown "${PUID}":"${PGID}" /app/entrypoint.sh
    
    # Set ownership for config files that might exist
    for config_file in settings.yaml badge_settings_audio.yml badge_settings_resolution.yml badge_settings_review.yml badge_settings_awards.yml version.yml; do
        if [ -f "/app/$config_file" ]; then
            chown "${PUID}":"${PGID}" "/app/$config_file"
        fi
    done
}

# Function to initialize configuration files
init_config() {
    log_msg "Initializing configuration files..."
    
    # Copy default config files to mounted config directory if they don't exist
    log_msg "Checking for config files to copy..."
    
    # Handle settings.yaml specially - use template if main file doesn't exist
    if [ ! -f "/app/config/settings.yaml" ]; then
        if [ -f "/app/settings.yaml" ]; then
            log_msg "Copying default settings.yaml to config directory"
            cp "/app/settings.yaml" "/app/config/settings.yaml"
        elif [ -f "/app/settings.yaml.template" ]; then
            log_msg "Copying settings.yaml.template to config directory as settings.yaml"
            cp "/app/settings.yaml.template" "/app/config/settings.yaml"
        else
            log_msg "WARNING: No settings.yaml or settings.yaml.template found to copy"
            log_msg "Will create minimal default settings.yaml via auto-repair"
        fi
        if [ -f "/app/config/settings.yaml" ]; then
            chown "${PUID}":"${PGID}" "/app/config/settings.yaml"
            chmod 664 "/app/config/settings.yaml"
            log_msg "Successfully created settings.yaml in config directory"
        fi
    else
        log_msg "Skipping settings.yaml copy (destination already exists)"
    fi
    
    # Auto-repair settings to ensure all required sections exist
    log_msg "Running settings auto-repair to ensure all required sections exist..."
    if [ -f "/app/config/settings.yaml" ]; then
        python /app/aphrodite_helpers/config_auto_repair.py --settings-path "/app/config/settings.yaml" --verbose
        if [ $? -eq 0 ]; then
            log_msg "✅ Settings auto-repair completed successfully"
        else
            log_msg "⚠️ Settings auto-repair encountered issues, but continuing..."
        fi
    else
        log_msg "Creating new settings file via auto-repair..."
        python /app/aphrodite_helpers/config_auto_repair.py --settings-path "/app/config/settings.yaml" --verbose
        if [ $? -eq 0 ]; then
            chown "${PUID}":"${PGID}" "/app/config/settings.yaml"
            chmod 664 "/app/config/settings.yaml"
            log_msg "✅ New settings file created and repaired successfully"
        else
            log_msg "❌ Failed to create settings file via auto-repair"
        fi
    fi
    
    # Handle other config files
    for config_file in badge_settings_audio.yml badge_settings_resolution.yml badge_settings_review.yml badge_settings_awards.yml version.yml; do
        if [ -f "/app/$config_file" ] && [ ! -f "/app/config/$config_file" ]; then
            log_msg "Copying default $config_file to config directory"
            cp "/app/$config_file" "/app/config/$config_file"
            chown "${PUID}":"${PGID}" "/app/config/$config_file"
            chmod 664 "/app/config/$config_file"
        else
            log_msg "Skipping $config_file (source missing or destination exists)"
        fi
    done
    
    # Create symlinks from config directory to app directory for compatibility
    log_msg "Creating symlinks for config files..."
    for config_file in settings.yaml badge_settings_audio.yml badge_settings_resolution.yml badge_settings_review.yml badge_settings_awards.yml version.yml; do
        if [ -f "/app/config/$config_file" ] && [ ! -L "/app/$config_file" ]; then
            # Remove original file if it exists and isn't a symlink
            if [ -f "/app/$config_file" ]; then
                log_msg "Removing original $config_file to create symlink"
                rm "/app/$config_file"
            fi
            # Create symlink
            log_msg "Creating symlink for $config_file"
            ln -s "/app/config/$config_file" "/app/$config_file"
        else
            log_msg "Skipping symlink for $config_file (config missing or symlink exists)"
        fi
    done
    log_msg "Configuration file initialization completed"
}

# Only setup user if running as root
if [ "$(id -u)" = "0" ]; then
    log_msg "Running as root, setting up user..."
    setup_user
    log_msg "User setup completed"
    
    log_msg "Initializing configuration..."
    init_config
    log_msg "Configuration initialization completed"
    
    # Switch to the aphrodite user for the rest of the script
    log_msg "Switching to user aphrodite (PUID=$PUID, PGID=$PGID)"
    exec gosu aphrodite "$0" "$@"
else
    log_msg "Already running as non-root user: $(id -un)"
fi

# From here on, we're running as the aphrodite user

# Make HTTP_HOST available from host:port configuration
if [ -n "${WEB_HOST}" ] && [ -n "${WEB_PORT}" ]; then
    export HTTP_HOST="${WEB_HOST}:${WEB_PORT}"
    log_msg "Setting HTTP_HOST to ${HTTP_HOST}"
fi

# Validate directory permissions
log_msg "Validating directory permissions..."
if [ -w "/app/posters" ] && [ -w "/app/data" ]; then
    log_msg "Directory permissions validated"
else
    log_msg "Warning: Missing write permissions for essential directories"
    ls -la /app/posters /app/data
fi

# Check database directory is writable
if [ ! -w "/app/data" ]; then
    log_msg "Error: Data directory is not writable"
    exit 1
fi

# Ensure config files exist and are readable
log_msg "Validating configuration files..."
config_files_valid=true
for config_file in /app/settings.yaml /app/badge_settings_audio.yml /app/badge_settings_resolution.yml /app/badge_settings_review.yml; do
    if [ -f "$config_file" ] || [ -L "$config_file" ]; then
        if [ -r "$config_file" ]; then
            log_msg "Successfully validated $config_file"
        else
            log_msg "ERROR: $config_file exists but is not readable"
            ls -la "$config_file"
            config_files_valid=false
        fi
    else
        log_msg "Warning: $config_file does not exist"
        config_files_valid=false
    fi
done

if [ "$config_files_valid" = false ]; then
    log_msg "Warning: Some configuration files are missing or not readable"
    log_msg "The application may not function correctly"
fi

# Initialize database if needed
if [ ! -f "/app/data/aphrodite.db" ]; then
    log_msg "Initializing database..."
    touch /app/data/aphrodite.db || log_msg "Warning: Could not create database file"
fi

# Apply configuration from environment variables
log_msg "Applying configuration from environment variables..."
python /app/config_from_env.py

# Log current version information for debugging
log_msg "Checking current version information..."
python -c "
try:
    import yaml
    import os
    from pathlib import Path
    
    # Read version from version.yml
    version_file = Path('/app/version.yml')
    if version_file.exists():
        with open(version_file, 'r') as f:
            version_data = yaml.safe_load(f)
            current_version = version_data.get('version', 'unknown')
        print(f'📋 Current version from version.yml: {current_version}')
        print(f'📁 Version file location: {version_file}')
    else:
        print('❌ Version file not found at /app/version.yml')
        current_version = 'unknown'
    
    # Check if version cache exists
    cache_file = Path('/app/version_cache.json')
    if cache_file.exists():
        import json
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            if 'data' in cache_data and 'current_version' in cache_data['data']:
                cached_version = cache_data['data']['current_version']
                print(f'💾 Cached version: {cached_version}')
            else:
                print('💾 Version cache exists but no version data found')
        except Exception as e:
            print(f'⚠️  Failed to read version cache: {e}')
    else:
        print('💾 No version cache found')
        
    # Test the VersionService directly
    import sys
    sys.path.append('/app')
    from aphrodite_helpers.settings_validator import run_settings_check
    
    # Add the web app path for imports
    sys.path.append('/app/aphrodite-web')
    
    try:
        from app.services.version_service import VersionService
        vs = VersionService('/app')
        service_version = vs.get_current_version()
        print(f'🔧 VersionService reports: {service_version}')
    except Exception as e:
        print(f'⚠️  Failed to load VersionService: {e}')
        
except Exception as e:
    print(f'❌ Error checking version: {e}')
    import traceback
    traceback.print_exc()
" || log_msg "Version check encountered issues"

# Run a quick validation of Jellyfin settings
log_msg "Validating Jellyfin connection..."
python -c "
from aphrodite_helpers.settings_validator import run_settings_check
from aphrodite_helpers.check_jellyfin_connection import load_settings, get_jellyfin_libraries
import sys

# Run basic settings check
if not run_settings_check():
    print('Settings validation failed')
    sys.exit(0)  # Don't exit with error, just warn

# Try to load settings
settings = load_settings()
if not settings:
    print('Failed to load settings')
    sys.exit(0)  # Don't exit with error, just warn

# Check if Jellyfin settings exist
if 'api_keys' not in settings or 'Jellyfin' not in settings['api_keys'] or not settings['api_keys']['Jellyfin']:
    print('Jellyfin settings are missing')
    sys.exit(0)  # Don't exit with error, just warn

# Check if we can connect to Jellyfin
jf = settings['api_keys']['Jellyfin'][0]
url, api_key, user_id = jf.get('url', ''), jf.get('api_key', ''), jf.get('user_id', '')
if not (url and api_key and user_id):
    print('Jellyfin connection settings are incomplete')
    sys.exit(0)  # Don't exit with error, just warn

# Try to get libraries (won't exit with error even if it fails)
try:
    libs = get_jellyfin_libraries(url, api_key, user_id)
    if libs:
        print(f'Successfully connected to Jellyfin at {url}')
        print(f'Found {len(libs)} libraries')
except Exception as e:
    print(f'Could not connect to Jellyfin: {str(e)}')
" || log_msg "Jellyfin validation encountered issues - check your settings"

# Determine the command to run based on environment variables or command line arguments
# Default is to run the web interface
MODE=${APHRODITE_MODE:-web}
log_msg "Starting Aphrodite in $MODE mode..."

if [ "$MODE" = "web" ]; then
    # Start the web application
    WEB_HOST=${WEB_HOST:-0.0.0.0}
    WEB_PORT=${WEB_PORT:-5000}
    FLASK_DEBUG=${FLASK_DEBUG:-0}
    DOCKER_EXPOSED_PORT=${DOCKER_EXPOSED_PORT:-2125}
    
    log_msg "DEBUG: Starting web application on $WEB_HOST:$WEB_PORT (debug: $FLASK_DEBUG)"
    log_msg "DEBUG: Frontend will be accessible at http://${WEB_HOST}:$DOCKER_EXPOSED_PORT"
    log_msg "DEBUG: Docker mapped port is $DOCKER_EXPOSED_PORT"
    
    # Set environment variables for the Flask app
    export FLASK_APP_HOST="$WEB_HOST"
    export FLASK_APP_PORT="$WEB_PORT"
    export FLASK_APP_DEBUG="$FLASK_DEBUG"
    export DOCKER_EXPOSED_PORT="$DOCKER_EXPOSED_PORT"
    export APHRODITE_BASE_URL="http://${WEB_HOST}:$DOCKER_EXPOSED_PORT"
    
    log_msg "Setting APHRODITE_BASE_URL to http://${WEB_HOST}:$DOCKER_EXPOSED_PORT"
    
    # In development mode, rebuild the frontend
    if [ "$FLASK_DEBUG" = "1" ] && [ -d "/app/aphrodite-web/frontend" ]; then
        log_msg "Development mode detected. Rebuilding frontend..."
        cd /app/aphrodite-web/frontend && npm install && npm run build
        if [ $? -eq 0 ]; then
            log_msg "Frontend rebuilt successfully."
        else
            log_msg "WARNING: Frontend rebuild failed. Using existing build if available."
        fi
    fi
    
    cd /app && export PYTHONPATH=$PYTHONPATH:/app && cd /app/aphrodite-web && python -c "from app import create_app; app = create_app(); app.run(host='$WEB_HOST', port=$WEB_PORT, debug=bool($FLASK_DEBUG))"
elif [ "$MODE" = "cli" ]; then
    # Execute the provided command line arguments for CLI mode
    log_msg "Running in CLI mode with arguments: $@"
    cd /app && python aphrodite.py "$@"
else
    # Default to the provided command if MODE is not recognized
    log_msg "Running custom command: $@"
    exec "$@"
fi
