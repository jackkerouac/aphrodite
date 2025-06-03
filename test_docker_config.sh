#!/bin/bash

# Test script to validate Docker configuration initialization
# This simulates what happens when Docker starts from a blank directory

echo "=== Aphrodite Docker Configuration Test ==="
echo

# Create temporary test directory
TEST_DIR="/tmp/aphrodite_docker_test_$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Created test directory: $TEST_DIR"

# Create directory structure that Docker would see
mkdir -p config posters data

echo "📁 Created directory structure"

# Test the entrypoint initialization logic
echo "🧪 Testing configuration initialization logic..."

# Simulate the config initialization part of entrypoint.sh
PUID=1000
PGID=1000

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Copy the settings template to simulate what's in the Docker image
cp "/path/to/aphrodite/settings.yaml.template" "./settings.yaml.template" 2>/dev/null || {
    echo "⚠️  Could not find settings.yaml.template, creating mock template"
    cat > "./settings.yaml.template" << 'EOF'
api_keys:
  Jellyfin:
  - url: https://your-jellyfin-server.com
    api_key: YOUR_JELLYFIN_API_KEY
    user_id: YOUR_JELLYFIN_USER_ID
  OMDB:
  - api_key: YOUR_OMDB_API_KEY
    cache_expiration: 60
  TMDB:
  - api_key: YOUR_TMDB_API_KEY
    cache_expiration: 60
    language: en
    region: US
EOF
}

# Test the fixed initialization logic
log_msg "Testing settings.yaml initialization..."

if [ ! -f "./config/settings.yaml" ]; then
    if [ -f "./settings.yaml" ]; then
        log_msg "Copying default settings.yaml to config directory"
        cp "./settings.yaml" "./config/settings.yaml"
    elif [ -f "./settings.yaml.template" ]; then
        log_msg "Copying settings.yaml.template to config directory as settings.yaml"
        cp "./settings.yaml.template" "./config/settings.yaml"
    else
        log_msg "WARNING: No settings.yaml or settings.yaml.template found to copy"
        log_msg "Creating minimal default settings.yaml"
        cat > "./config/settings.yaml" << 'EOF'
api_keys:
  Jellyfin:
  - url: https://your-jellyfin-server.com
    api_key: YOUR_JELLYFIN_API_KEY
    user_id: YOUR_JELLYFIN_USER_ID
EOF
    fi
    if [ -f "./config/settings.yaml" ]; then
        log_msg "Successfully created settings.yaml in config directory"
    else
        log_msg "ERROR: Failed to create settings.yaml"
    fi
else
    log_msg "Skipping settings.yaml (destination already exists)"
fi

# Verify the result
echo
echo "🔍 Verification Results:"
if [ -f "./config/settings.yaml" ]; then
    echo "✅ settings.yaml was successfully created"
    echo "📄 Content preview:"
    head -10 "./config/settings.yaml" | sed 's/^/    /'
else
    echo "❌ settings.yaml was NOT created"
fi

# Cleanup
echo
echo "🧹 Cleaning up test directory..."
rm -rf "$TEST_DIR"
echo "✅ Test completed"
