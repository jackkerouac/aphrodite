# Docker Configuration Fix

## Problem

The Docker container was hanging during initialization because the `settings.yaml` file was not being created properly when starting from a blank directory. The logs showed:

```
Warning: /app/settings.yaml does not exist
Warning: Some configuration files are missing or not readable
The application may not function correctly
```

## Root Cause

The issue was in the `entrypoint.sh` script's `init_config()` function. The original logic was:

```bash
for config_file in settings.yaml badge_settings_audio.yml ...; do
    if [ -f "/app/$config_file" ] && [ ! -f "/app/config/$config_file" ]; then
        cp "/app/$config_file" "/app/config/$config_file"
    fi
done
```

This logic failed for `settings.yaml` because:
1. The Docker image only contained `settings.yaml.template`, not `settings.yaml`
2. The condition `[ -f "/app/settings.yaml" ]` would always fail
3. No fallback logic existed to use the template file
4. The container would proceed without creating the required config file

## Solution

### 1. Enhanced Settings File Initialization

Modified `entrypoint.sh` to handle `settings.yaml` specially with a fallback hierarchy:

```bash
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
        log_msg "Creating minimal default settings.yaml"
        # Embedded minimal config creation
    fi
fi
```

### 2. Guaranteed Template Availability

Updated `Dockerfile` to explicitly ensure `settings.yaml.template` is present:

```dockerfile
# Copy application code
COPY . .

# Ensure template files are present for config initialization
COPY settings.yaml.template /app/settings.yaml.template
```

### 3. Failsafe Default Creation

Added embedded minimal config creation as ultimate fallback:

```bash
cat > "/app/config/settings.yaml" << 'EOF'
api_keys:
  Jellyfin:
  - url: https://your-jellyfin-server.com
    api_key: YOUR_JELLYFIN_API_KEY
    user_id: YOUR_JELLYFIN_USER_ID
  # ... minimal required config
EOF
```

### 4. Enhanced Logging and Verification

Added comprehensive logging and verification:

```bash
if [ -f "/app/config/settings.yaml" ]; then
    log_msg "Successfully created settings.yaml in config directory"
else
    log_msg "ERROR: Failed to create settings.yaml"
fi
```

## Files Modified

1. **`entrypoint.sh`**: Enhanced configuration initialization logic
2. **`Dockerfile`**: Explicit template file inclusion
3. **`settings.yaml.template`**: Updated with clear placeholder values

## Testing

The fix ensures that:

1. **Fresh Installation**: Starting with blank directories creates all required config files
2. **Template Fallback**: Uses `settings.yaml.template` when main file doesn't exist
3. **Ultimate Fallback**: Creates minimal config if no template exists
4. **Proper Permissions**: Sets correct ownership and permissions
5. **Clear Logging**: Provides detailed feedback about what's happening

## Verification

After applying this fix, the Docker container should:

1. ✅ Create `settings.yaml` from template on first run
2. ✅ Show successful initialization in logs
3. ✅ Start the web application without hanging
4. ✅ Allow users to customize the generated config file

The logs should show:
```
Copying settings.yaml.template to config directory as settings.yaml
Successfully created settings.yaml in config directory
Successfully validated /app/settings.yaml
```

Instead of:
```
Skipping settings.yaml (source missing or destination exists)
Warning: /app/settings.yaml does not exist
```
