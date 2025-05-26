# Aphrodite Docker - Jellyfin Poster Badge System

This Docker container provides a ready-to-use deployment of Aphrodite, a powerful utility for enhancing Jellyfin media posters by adding informational badges such as audio codec, resolution, and review ratings.

![Aphrodite Banner](https://raw.githubusercontent.com/yourusername/aphrodite-python/main/images/banner.png)

## Features

- Add audio codec badges to media posters (Dolby Atmos, DTS-HD, TrueHD, etc.)
- Add resolution badges to media posters (4K, 1080p, HDR, etc.)
- Add review badges with ratings from IMDb, Rotten Tomatoes, etc.
- Modern web interface for easy configuration and operation
- Automatic batch processing of entire libraries
- Customizable badge positioning, colors, and styles
- Real-time job tracking and history

## Quick Start

```bash
# Pull the Docker image
docker pull yourusername/aphrodite:latest

# Create basic directories
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Run the container
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml \
  -v $(pwd)/posters:/app/posters \
  -v $(pwd)/data:/app/data \
  -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com \
  -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here \
  -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here \
  yourusername/aphrodite:latest
```

Then access the web interface at http://localhost:5000

## Installation

### Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aphrodite-python.git
   cd aphrodite-python
   ```

2. Copy the environment template file:
   ```bash
   cp .env.template .env
   ```

3. Edit `.env` with your Jellyfin server details:
   ```
   APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com
   APHRODITE_JELLYFIN_API_KEY=your-api-key-here
   APHRODITE_JELLYFIN_USER_ID=your-user-id-here
   ```

4. Start the container:
   ```bash
   docker-compose up -d
   ```

5. Access the web interface at http://localhost:5000

### Using Docker Run

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/badge_settings_audio.yml:/app/badge_settings_audio.yml:rw \
  -v $(pwd)/badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw \
  -v $(pwd)/badge_settings_review.yml:/app/badge_settings_review.yml:rw \
  -v $(pwd)/posters/original:/app/posters/original:rw \
  -v $(pwd)/posters/working:/app/posters/working:rw \
  -v $(pwd)/posters/modified:/app/posters/modified:rw \
  -v $(pwd)/data:/app/data:rw \
  -v $(pwd)/fonts:/app/fonts:ro \
  -v $(pwd)/images:/app/images:ro \
  -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com \
  -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here \
  -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here \
  yourusername/aphrodite:latest
```

### Building the Image Yourself

```bash
# Clone the repository
git clone https://github.com/yourusername/aphrodite-python.git
cd aphrodite-python

# Build the Docker image
docker build -t aphrodite:latest .

# Run the container
docker-compose up -d
```

## Volume Mounting Guide

Aphrodite uses several directories and configuration files that can be mounted from the host for persistence and customization:

### Configuration Files

| Container Path | Description | Mount Type |
|----------------|-------------|------------|
| /app/settings.yaml | Main configuration file | Read-Write |
| /app/badge_settings_audio.yml | Audio badge configuration | Read-Write |
| /app/badge_settings_resolution.yml | Resolution badge configuration | Read-Write |
| /app/badge_settings_review.yml | Review badge configuration | Read-Write |

### Data Directories

| Container Path | Description | Mount Type |
|----------------|-------------|------------|
| /app/posters/original | Original posters downloaded from Jellyfin | Read-Write |
| /app/posters/working | Temporary working directory for processing | Read-Write |
| /app/posters/modified | Modified posters with badges applied | Read-Write |
| /app/data | Database and application state | Read-Write |
| /app/fonts | Custom fonts for badges | Read-Only |
| /app/images | Custom images for badges | Read-Only |

### Mounting Examples

#### Minimal Setup (Required)

```yaml
volumes:
  - ./settings.yaml:/app/settings.yaml:rw
  - ./posters:/app/posters:rw
  - ./data:/app/data:rw
```

#### Full Setup (Recommended)

```yaml
volumes:
  # Configuration files
  - ./settings.yaml:/app/settings.yaml:rw
  - ./badge_settings_audio.yml:/app/badge_settings_audio.yml:rw
  - ./badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw
  - ./badge_settings_review.yml:/app/badge_settings_review.yml:rw
  
  # Poster directories
  - ./posters/original:/app/posters/original:rw
  - ./posters/working:/app/posters/working:rw
  - ./posters/modified:/app/posters/modified:rw
  
  # Application data
  - ./data:/app/data:rw
  
  # Resources (can be read-only)
  - ./fonts:/app/fonts:ro
  - ./images:/app/images:ro
```

## Configuration Options

### Environment Variables

Aphrodite can be configured using environment variables, which is the recommended approach for Docker deployments. See the [Environment Variable Configuration](ENV_CONFIG.md) for a complete list of available variables.

Key environment variables include:

```yaml
# Jellyfin Connection
APHRODITE_JELLYFIN_URL: Your Jellyfin server URL
APHRODITE_JELLYFIN_API_KEY: Your Jellyfin API key
APHRODITE_JELLYFIN_USER_ID: Your Jellyfin user ID

# Application Mode
APHRODITE_MODE: web (web interface) or cli (command line)

# Web Interface
WEB_HOST: Host to bind to (default: 0.0.0.0)
WEB_PORT: Port to bind to (default: 5000)
FLASK_DEBUG: Enable debug mode (1=True, 0=False)

# User/Group ID Mapping
PUID: User ID to run as (for file permissions)
PGID: Group ID to run as (for file permissions)
```

### Configuration Files

If you prefer to mount and edit configuration files directly:

1. **settings.yaml**: Main configuration file for API connections
2. **badge_settings_audio.yml**: Appearance settings for audio badges
3. **badge_settings_resolution.yml**: Appearance settings for resolution badges
4. **badge_settings_review.yml**: Appearance settings for review badges

See the original [Aphrodite README](README.md) for details on configuration file format.

## Usage Examples

### Running in Web Interface Mode (Default)

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com \
  -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here \
  -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here \
  yourusername/aphrodite:latest
```

### Running in CLI Mode

```bash
# Process a single item
docker run --rm \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_MODE=cli \
  yourusername/aphrodite:latest item 12345abcde

# Process a library
docker run --rm \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_MODE=cli \
  yourusername/aphrodite:latest library 67890fghij --limit 10

# Check connection and library info
docker run --rm \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -e APHRODITE_MODE=cli \
  yourusername/aphrodite:latest check
```

### Using Specific User/Group IDs

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e PUID=1000 \
  -e PGID=1000 \
  -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com \
  -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here \
  -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here \
  yourusername/aphrodite:latest
```

### Customizing Badge Appearance

Either mount the badge settings files:

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/badge_settings_audio.yml:/app/badge_settings_audio.yml:rw \
  -v $(pwd)/badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw \
  -v $(pwd)/badge_settings_review.yml:/app/badge_settings_review.yml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  yourusername/aphrodite:latest
```

Or use environment variables:

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_AUDIO_BADGE_POSITION=top-left \
  -e APHRODITE_AUDIO_BADGE_SIZE=100 \
  -e APHRODITE_AUDIO_BG_COLOR=#000000 \
  -e APHRODITE_AUDIO_BG_OPACITY=40 \
  -e APHRODITE_RESOLUTION_BADGE_POSITION=top-right \
  -e APHRODITE_REVIEW_BADGE_POSITION=bottom-left \
  yourusername/aphrodite:latest
```

## Common Issues and Troubleshooting

### Permission Errors

If you encounter permission errors when mounting volumes:

1. Set the PUID and PGID environment variables to match your host user/group ID:
   ```bash
   # Find your user/group ID
   id -u  # User ID
   id -g  # Group ID
   
   # Add to your docker-compose.yml or docker run command
   -e PUID=1000 -e PGID=1000
   ```

2. Ensure host directories exist and have proper permissions:
   ```bash
   mkdir -p ./posters/original ./posters/working ./posters/modified ./data
   chmod -R 775 ./posters ./data
   ```

### Connection Issues

If you can't connect to Jellyfin:

1. Verify your Jellyfin URL, API key, and user ID
2. Ensure the Jellyfin server is accessible from the Docker container
3. Check for any firewalls blocking connections
4. Verify Jellyfin API is enabled and permissions are correct

## Upgrading

To upgrade to a newer version of Aphrodite:

```bash
# Using docker-compose
docker-compose pull
docker-compose up -d

# Using docker run
docker pull yourusername/aphrodite:latest
docker stop aphrodite
docker rm aphrodite
# Run the container again with your original parameters
```

## License

[MIT License](LICENSE)

For more detailed information about using Aphrodite itself, please refer to the original [Aphrodite README](README.md).
