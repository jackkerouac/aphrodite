# Aphrodite - Jellyfin Poster Badge System

Aphrodite is a Python-based utility for enhancing Jellyfin media posters by adding informational badges (such as audio codec, resolution, and review ratings) to them. The application is available as both a standalone Python package and a ready-to-use Docker container.

## Features

- Add audio codec badges to media posters (Dolby Atmos, DTS-HD, TrueHD, etc.)
- Add resolution badges to media posters (4K, 1080p, HDR, etc.)
- Add review badges with ratings from IMDb, Rotten Tomatoes, etc.
- Modern web interface for easy configuration and operation
- Automatic batch processing of entire libraries
- Customizable badge positioning, colors, and styles
- Real-time job tracking and history

## Docker Installation (Recommended)

The easiest way to use Aphrodite is via Docker:

```bash
# Create basic directories
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Run the container with Docker Compose
docker-compose up -d
```

Or with `docker run`:

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
  -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com \
  -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here \
  -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here \
  yourusername/aphrodite:latest
```

### Docker Configuration

Aphrodite Docker can be configured in two ways:

1. **Environment Variables** (recommended):
   ```bash
   -e APHRODITE_JELLYFIN_URL=https://your-jellyfin-server.com
   -e APHRODITE_JELLYFIN_API_KEY=your-api-key-here
   -e APHRODITE_JELLYFIN_USER_ID=your-user-id-here
   ```

2. **Mounted Configuration Files**:
   ```bash
   -v $(pwd)/settings.yaml:/app/settings.yaml:rw
   -v $(pwd)/badge_settings_audio.yml:/app/badge_settings_audio.yml:rw
   ```

See [Docker Documentation](DOCKER_README.md) for complete instructions and [Environment Variable Configuration](ENV_CONFIG.md) for all available options.

## Traditional Installation

If you prefer to run Aphrodite without Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aphrodite-python.git
   cd aphrodite-python
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure your settings (see Traditional Configuration section)

## Traditional Configuration

1. Copy the example settings file:
   ```bash
   cp settings.yaml.template settings.yaml
   ```

2. Edit `settings.yaml` with your Jellyfin server details:
   ```yaml
   api_keys:
     Jellyfin:
       - url: "https://your-jellyfin-server.com"
         api_key: "your-api-key-here"
         user_id: "your-user-id-here"
   ```

3. Customize badge appearance in `badge_settings_audio.yml`, `badge_settings_resolution.yml`, and `badge_settings_review.yml`

## Usage

### Web Interface (Docker or Traditional)

1. Start the web application:
   - Docker: Already running on port 5000
   - Traditional: Run `python -m aphrodite-web.main`

2. Access the web interface at http://localhost:5000

3. Features available in the web interface:
   - Configure all settings
   - Process individual items or entire libraries
   - View job history and results
   - Preview modified posters

### Command Line (Docker or Traditional)

Aphrodite provides several command-line interfaces for different operations:

#### Check System Settings and Jellyfin Connection

```bash
# Traditional
python aphrodite.py check

# Docker
docker run --rm -e APHRODITE_MODE=cli yourusername/aphrodite:latest check
```

This command verifies your settings and connection to Jellyfin, displaying all available libraries and their item counts.

#### Process a Single Item

```bash
# Traditional
python aphrodite.py item ITEM_ID [--retries MAX_RETRIES]

# Docker
docker run --rm -e APHRODITE_MODE=cli yourusername/aphrodite:latest item ITEM_ID
```

Processes a single Jellyfin item, creating and applying badges with media information.

#### Process an Entire Library

```bash
# Traditional
python aphrodite.py library LIBRARY_ID [--limit NUM_ITEMS] [--retries MAX_RETRIES]

# Docker
docker run --rm -e APHRODITE_MODE=cli yourusername/aphrodite:latest library LIBRARY_ID --limit 10
```

Processes all items in a specific Jellyfin library. Use `--limit` to restrict the number of items processed.

## Docker Volume Mounting Guide

For persistent storage and configuration, mount these volumes:

### Required Volumes

```bash
# Configuration
-v $(pwd)/settings.yaml:/app/settings.yaml:rw

# Data storage
-v $(pwd)/posters:/app/posters:rw
-v $(pwd)/data:/app/data:rw
```

### Optional Volumes

```bash
# Badge configurations
-v $(pwd)/badge_settings_audio.yml:/app/badge_settings_audio.yml:rw
-v $(pwd)/badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw
-v $(pwd)/badge_settings_review.yml:/app/badge_settings_review.yml:rw

# Resources
-v $(pwd)/fonts:/app/fonts:ro
-v $(pwd)/images:/app/images:ro
```

## Docker Environment Variables

Key environment variables:

```bash
# Jellyfin connection
-e APHRODITE_JELLYFIN_URL=https://jellyfin.example.com
-e APHRODITE_JELLYFIN_API_KEY=your_api_key
-e APHRODITE_JELLYFIN_USER_ID=your_user_id

# Web interface
-e WEB_PORT=5000
-e FLASK_DEBUG=0

# Permissions
-e PUID=1000
-e PGID=1000

# Application mode
-e APHRODITE_MODE=web  # or cli
```

See [Environment Variable Configuration](ENV_CONFIG.md) for the complete list.

## Badge Customization

Badges can be customized by:

1. Editing the badge settings files:
   - `badge_settings_audio.yml`
   - `badge_settings_resolution.yml`
   - `badge_settings_review.yml`

2. Setting environment variables (Docker):
   ```bash
   -e APHRODITE_AUDIO_BADGE_POSITION=top-left
   -e APHRODITE_AUDIO_BADGE_SIZE=100
   -e APHRODITE_AUDIO_BG_COLOR=#000000
   ```

Available options include:

- **Background**: Color, opacity
- **Border**: Color, width, radius
- **Shadow**: Enable/disable, blur, offset
- **Text**: Font, color, size
- **Position**: Top-left, top-right, bottom-left, bottom-right
- **Size**: Fixed or dynamic sizing based on text

## Requirements

- Python 3.7+
- Pillow (for image processing)
- requests (for API communication)
- PyYAML (for configuration)
- Flask (for web interface)

Or simply use Docker which includes all dependencies.

## Troubleshooting

### Permission Issues

If you encounter permission errors when using Docker:

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
2. Ensure the Jellyfin server is accessible from your machine or Docker container
3. Check for any firewalls blocking connections
4. Verify Jellyfin API is enabled and permissions are correct

## License

[MIT License](LICENSE)

For more detailed information about Docker deployment, please refer to the [Docker Documentation](DOCKER_README.md).
