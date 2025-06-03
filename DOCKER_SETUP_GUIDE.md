# Docker Setup Guide

## Quick Start

1. Create a `docker-compose.yml` file:

```yaml
services:
  aphrodite:
    image: ghcr.io/jackkerouac/aphrodite:latest
    container_name: aphrodite
    ports:
      - "2125:5000"
    volumes:
      # Configuration files (auto-created if missing, fully customizable)
      - ./config:/app/config:rw
      
      # Persistent storage for posters and database
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
      
    environment:
      - TZ=UTC
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
      
    restart: unless-stopped
```

2. (Optional) Create a `.env` file for user configuration:

```bash
# User and Group IDs for file permissions
# Set these to match your host system user
# To find your IDs, run: id $(whoami)
PUID=1000
PGID=1000

# Timezone (optional)
TZ=UTC
```

3. Start the container:

```bash
docker-compose up -d
```

## What's Changed

### Simplified Setup
- **No more separate downloads**: fonts, images, and default configurations are built into the Docker image
- **Auto-initialization**: Configuration files are automatically created on first run if they don't exist
- **One command setup**: Just run `docker-compose up -d` and you're ready to go

### Better Permission Handling
- **PUID/PGID support**: Set your user and group IDs to avoid permission issues
- **Automatic user creation**: Container creates the correct user at runtime
- **Proper file ownership**: All files are owned by the correct user

### Cleaner Volume Structure
- **Single config directory**: All configuration files in one place (`./config/`)
- **No external dependencies**: Fonts and images are internal to the container
- **Persistent data**: Only posters and database are mounted externally

## Configuration

### User and Group IDs (PUID/PGID)

To avoid permission issues, set PUID and PGID to match your host system user:

```bash
# Find your user and group IDs
id $(whoami)
```

This will output something like:
```
uid=1000(username) gid=1000(groupname)
```

Use these values in your `.env` file or directly in docker-compose.yml.

### Configuration Files

Configuration files are automatically copied to `./config/` on first run:
- `settings.yaml` - Main application settings
- `badge_settings_audio.yml` - Audio badge configuration
- `badge_settings_resolution.yml` - Resolution badge configuration  
- `badge_settings_review.yml` - Review badge configuration
- `badge_settings_awards.yml` - Awards badge configuration
- `version.yml` - Version information

You can customize these files and restart the container to apply changes.

### Directory Structure

After first run, you'll have:
```
./
├── docker-compose.yml
├── .env (optional)
├── config/
│   ├── settings.yaml
│   ├── badge_settings_*.yml
│   └── version.yml
├── posters/
│   ├── original/
│   ├── working/
│   └── modified/
└── data/
    └── aphrodite.db
```

## Troubleshooting

### Permission Issues
If you get permission errors:
1. Check your PUID/PGID values match your host user
2. Ensure the directories are writable by your user
3. Try running: `sudo chown -R $(id -u):$(id -g) ./config ./posters ./data`

### Configuration Issues
If configuration seems wrong:
1. Delete the `./config/` directory
2. Restart the container to regenerate defaults
3. Customize the regenerated files as needed

### Image/Font Issues
If badges aren't appearing correctly:
- This should no longer happen as all assets are built into the image
- If issues persist, check the container logs for specific errors

## Migration from Old Setup

If you're upgrading from the old Docker setup:

1. **Backup your configuration**:
   ```bash
   mkdir -p ./config
   cp settings.yaml badge_settings_*.yml version.yml ./config/
   ```

2. **Update docker-compose.yml** to the new format (shown above)

3. **Remove old volume mounts**:
   - Remove `./fonts:/app/fonts:ro`
   - Remove `./images:/app/images:ro`
   - Remove individual config file mounts

4. **Restart the container**:
   ```bash
   docker-compose down
   docker-compose pull
   docker-compose up -d
   ```

The new setup will use your existing configuration files and provide a much simpler experience going forward.
