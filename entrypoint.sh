#!/bin/bash
set -e

# Function to log with timestamp
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_msg "Starting Aphrodite container initialization..."

# Make HTTP_HOST available from host:port configuration
if [ -n "${WEB_HOST}" ] && [ -n "${WEB_PORT}" ]; then
    export HTTP_HOST="${WEB_HOST}:${WEB_PORT}"
    log_msg "Setting HTTP_HOST to ${HTTP_HOST}"
fi

# Handle the user/group IDs if running as root
if [ "$(id -u)" = "0" ]; then
    log_msg "Running as root, checking for custom user configuration..."
    
    # Check if custom PUID/PGID is set and different from current user
    if [ -n "${PUID}" ] && [ -n "${PGID}" ] && [ "${PUID}" != "$(id -u aphrodite)" ]; then
        log_msg "Updating user ID to ${PUID} and group ID to ${PGID}"
        
        # Recreate the aphrodite group with specified GID
        groupmod -o -g "${PGID}" aphrodite
        
        # Update the aphrodite user with the specified UID
        usermod -o -u "${PUID}" aphrodite
        
        # Update ownership of directories
        chown -R "${PUID}":"${PGID}" /app
    fi
fi

# Create required directories
log_msg "Creating required directories..."
for dir in /app/posters/original /app/posters/working /app/posters/modified /app/data /app/fonts /app/images; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_msg "Created directory: $dir"
    fi
done

# Validate directory permissions
log_msg "Validating directory permissions..."
if [ -w "/app/posters" ] && [ -w "/app/data" ]; then
    chmod -R 775 /app/posters /app/data 2>/dev/null || log_msg "Notice: Running as non-root, permission changes may be limited"
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

# Ensure config files have correct permissions and exist
log_msg "Validating configuration files..."
config_files_valid=true
for config_file in /app/settings.yaml /app/badge_settings_audio.yml /app/badge_settings_resolution.yml /app/badge_settings_review.yml; do
    if [ -f "$config_file" ]; then
        if [ -r "$config_file" ]; then
            log_msg "DEBUG: Successfully read $config_file"
            log_msg "DEBUG: Contents of $config_file:"
            cat "$config_file" | sed 's/^/    /'
        else
            log_msg "ERROR: $config_file exists but is not readable"
            ls -la "$config_file"
            config_files_valid=false
        fi
        
        if [ -w "$config_file" ]; then
            chmod 664 "$config_file" 2>/dev/null || log_msg "Notice: Running as non-root, file permission changes may be limited"
            log_msg "DEBUG: $config_file is writable"
        else
            log_msg "Warning: $config_file exists but is not writable"
            ls -la "$config_file"
            config_files_valid=false
        fi
    else
        log_msg "Error: $config_file does not exist"
        ls -la "$(dirname $config_file)/"
        config_files_valid=false
    fi
done

if [ "$config_files_valid" = false ]; then
    log_msg "Warning: Some configuration files are missing or not writable"
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
