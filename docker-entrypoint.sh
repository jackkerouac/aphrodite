#!/bin/bash
set -e

# Function to check if we're running as root
is_root() {
    [ "$(id -u)" = "0" ]
}

# Function to ensure directory exists and has correct permissions
ensure_directory() {
    local dir="$1"
    local user="aphrodite"
    local group="aphrodite"
    
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
    
    echo "Setting permissions for: $dir"
    if is_root; then
        chown -R "$user:$group" "$dir" 2>/dev/null || echo "Warning: Could not change ownership of $dir"
    fi
    chmod -R 755 "$dir" 2>/dev/null || echo "Warning: Could not change permissions of $dir"
}

# Ensure critical directories exist and have correct permissions
echo "Ensuring directory permissions..."

ensure_directory "/app/logs"
ensure_directory "/app/data"
ensure_directory "/app/media"
ensure_directory "/app/api/static"
ensure_directory "/app/api/static/originals"
ensure_directory "/app/api/static/processed"
ensure_directory "/app/api/static/preview"
ensure_directory "/app/api/static/awards"
ensure_directory "/app/api/static/awards/black"
ensure_directory "/app/api/static/awards/white"

echo "Directory setup complete."

# If running as root and DOCKER_USER is set, switch to that user
if is_root && [ -n "$DOCKER_USER" ]; then
    echo "Switching to user: $DOCKER_USER"
    exec gosu "$DOCKER_USER" "$@"
elif is_root; then
    echo "Switching to user: aphrodite"
    exec gosu aphrodite "$@"
else
    echo "Running as current user: $(whoami)"
    exec "$@"
fi
