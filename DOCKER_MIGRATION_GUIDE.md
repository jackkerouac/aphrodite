# Docker Setup Changes - Migration Guide

## What's New

This update significantly simplifies the Docker setup for Aphrodite. The key improvements are:

### 1. **Simplified Volume Structure**
- **Before**: Required mounting 8+ individual files and directories
- **After**: Only 3 volume mounts needed (`config`, `posters`, `data`)

### 2. **Built-in Assets**
- **Before**: Required downloading `fonts.zip` and `images.zip` separately
- **After**: All fonts and badge images are built into the Docker image

### 3. **Auto-Configuration**
- **Before**: Manual creation of all configuration files required
- **After**: Default configuration files are automatically created on first run

### 4. **PUID/PGID Support**
- **Before**: File permission issues common
- **After**: Set PUID/PGID to match your host user for proper permissions

### 5. **Fixed Preview Generation**
- **Before**: Preview generation failed when mounting empty/corrupted image files
- **After**: Preview generation always works as images are internal to container

## Migration Steps

If you're upgrading from the old Docker setup:

### 1. Backup Your Configuration
```bash
# Create config directory and backup existing files
mkdir -p ./config
cp settings.yaml badge_settings_*.yml version.yml ./config/ 2>/dev/null || true
```

### 2. Update docker-compose.yml
Replace your existing `docker-compose.yml` with:

```yaml
services:
  aphrodite:
    image: ghcr.io/jackkerouac/aphrodite:latest
    container_name: aphrodite
    ports:
      - "2125:5000"
    volumes:
      - ./config:/app/config:rw
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    environment:
      - TZ=UTC
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
    restart: unless-stopped
```

### 3. Set User Permissions (Optional but Recommended)
Create a `.env` file:

```bash
# Find your user/group IDs
id $(whoami)

# Create .env file with your IDs
cat > .env << EOF
PUID=1000
PGID=1000
TZ=UTC
EOF
```

### 4. Restart the Container
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## What You Can Remove

After migrating, you can safely remove:
- `fonts/` directory (if you downloaded it separately)
- `images/` directory (if you downloaded it separately)  
- Individual configuration file mounts in docker-compose.yml
- The old volume mount structure

## Benefits of the New Setup

1. **Faster setup**: One command deployment
2. **Fewer errors**: No missing fonts/images issues
3. **Better permissions**: PUID/PGID prevents permission problems
4. **Easier maintenance**: Fewer files to manage
5. **Preview always works**: No more corrupted image file issues

## Troubleshooting

### Config Files Not Appearing
If configuration files aren't created automatically:
1. Check container logs: `docker-compose logs`
2. Ensure the config directory is writable
3. Try removing the config directory and restarting

### Permission Issues
If you get permission errors:
1. Set PUID/PGID to match your host user
2. Run: `sudo chown -R $(id -u):$(id -g) ./config ./posters ./data`

### Preview Still Not Working
If preview generation still fails:
1. Check that you're not mounting `./images:/app/images:ro`
2. Ensure you're using the new docker-compose.yml format
3. Check container logs for specific error messages
4. Try deleting and recreating the container

### Old Configuration Not Working
If your old configuration seems to be ignored:
1. Ensure config files are in the `./config/` directory
2. Check file permissions: `ls -la ./config/`
3. Restart the container after making changes
4. Check container logs for configuration loading messages

## Technical Details

### How Auto-Configuration Works
- Container checks if `/app/config/` directory has configuration files
- If missing, copies defaults from built-in templates
- Creates symlinks from `/app/config/` to `/app/` for compatibility
- Preserves any existing customizations

### PUID/PGID Implementation
- Container starts as root to setup user/group
- Creates or modifies the `aphrodite` user with specified IDs
- Switches to the `aphrodite` user using `gosu`
- All file operations run with correct permissions

### Asset Management
- Fonts and images are compiled into the Docker image during build
- No external downloads required
- Preview generation uses internal assets, eliminating corruption issues
- Custom fonts/images can still be added via the config system if needed

## Backward Compatibility

The new setup maintains backward compatibility with:
- Existing configuration file formats
- All API endpoints and functionality
- Command-line interface usage
- Environment variable configuration

The only breaking change is the Docker volume mount structure, which requires migration as described above.
