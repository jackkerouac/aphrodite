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

# Determine the correct Python executable
PYTHON_CMD="python3"
if [ -x "/home/aphrodite/.local/bin/python" ]; then
    PYTHON_CMD="/home/aphrodite/.local/bin/python"
elif [ -x "/usr/local/bin/python" ]; then
    PYTHON_CMD="/usr/local/bin/python"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python > /dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "Using Python executable: $PYTHON_CMD"

# Replace any python references in the command with our detected python
COMMAND=("$@")
for i in "${!COMMAND[@]}"; do
    if [[ "${COMMAND[$i]}" == "python" ]] || [[ "${COMMAND[$i]}" == "/home/aphrodite/.local/bin/python" ]]; then
        COMMAND[$i]="$PYTHON_CMD"
    fi
done

# If running as root and DOCKER_USER is set, switch to that user
if is_root && [ -n "$DOCKER_USER" ]; then
    echo "Switching to user: $DOCKER_USER"
    exec gosu "$DOCKER_USER" "${COMMAND[@]}"
elif is_root; then
    echo "Switching to user: aphrodite"
    exec gosu aphrodite "${COMMAND[@]}"
else
    echo "Running as current user: $(whoami)"
    exec "${COMMAND[@]}"
fi
