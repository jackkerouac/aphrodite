# Aphrodite Docker Quick Reference

This document provides quick reference examples for common Docker deployment scenarios.

## Basic Configuration Examples

### Minimal Configuration (Environment Variables)

```yaml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite
    ports:
      - "5000:5000"
    volumes:
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    environment:
      - APHRODITE_JELLYFIN_URL=https://jellyfin.example.com
      - APHRODITE_JELLYFIN_API_KEY=your_api_key_here
      - APHRODITE_JELLYFIN_USER_ID=your_user_id_here
    restart: unless-stopped
```

### Standard Configuration (Config Files)

```yaml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite
    ports:
      - "5000:5000"
    volumes:
      # Configuration files
      - ./settings.yaml:/app/settings.yaml:rw
      - ./badge_settings_audio.yml:/app/badge_settings_audio.yml:rw
      - ./badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw
      - ./badge_settings_review.yml:/app/badge_settings_review.yml:rw
      
      # Data directories
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    restart: unless-stopped
```

### Complete Configuration (Mixed Approach)

```yaml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite
    ports:
      - "5000:5000"
    volumes:
      # Configuration files
      - ./settings.yaml:/app/settings.yaml:rw
      - ./badge_settings_audio.yml:/app/badge_settings_audio.yml:rw
      - ./badge_settings_resolution.yml:/app/badge_settings_resolution.yml:rw
      - ./badge_settings_review.yml:/app/badge_settings_review.yml:rw
      
      # Data directories with explicit subdirectories
      - ./posters/original:/app/posters/original:rw
      - ./posters/working:/app/posters/working:rw
      - ./posters/modified:/app/posters/modified:rw
      - ./data:/app/data:rw
      
      # Resource directories
      - ./fonts:/app/fonts:ro
      - ./images:/app/images:ro
    environment:
      # Override specific settings from files
      - APHRODITE_JELLYFIN_URL=https://jellyfin.example.com
      - APHRODITE_JELLYFIN_API_KEY=your_api_key_here
      - APHRODITE_JELLYFIN_USER_ID=your_user_id_here
      
      # Web interface settings
      - WEB_HOST=0.0.0.0
      - WEB_PORT=5000
      - FLASK_DEBUG=0
      
      # User/group permissions
      - PUID=1000
      - PGID=1000
      
      # Timezone
      - TZ=America/New_York
    restart: unless-stopped
```

## Special Use Cases

### Run in CLI Mode

```yaml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite-cli
    volumes:
      - ./settings.yaml:/app/settings.yaml:rw
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    environment:
      - APHRODITE_MODE=cli
    command: library your_library_id --limit 10
    restart: "no"  # Run once and exit
```

### Custom Port Mapping

```yaml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite
    ports:
      - "8080:5000"  # Map container port 5000 to host port 8080
    volumes:
      - ./settings.yaml:/app/settings.yaml:rw
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    environment:
      - APHRODITE_JELLYFIN_URL=https://jellyfin.example.com
      - APHRODITE_JELLYFIN_API_KEY=your_api_key_here
      - APHRODITE_JELLYFIN_USER_ID=your_user_id_here
    restart: unless-stopped
```

### Using .env File

```
# .env file
APHRODITE_JELLYFIN_URL=https://jellyfin.example.com
APHRODITE_JELLYFIN_API_KEY=your_api_key_here
APHRODITE_JELLYFIN_USER_ID=your_user_id_here
WEB_PORT=8080
PUID=1000
PGID=1000
TZ=America/New_York
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  aphrodite:
    image: yourusername/aphrodite:latest
    container_name: aphrodite
    env_file: .env
    ports:
      - "${WEB_PORT:-5000}:5000"
    volumes:
      - ./settings.yaml:/app/settings.yaml:rw
      - ./posters:/app/posters:rw
      - ./data:/app/data:rw
    restart: unless-stopped
```

## Docker Run Command Examples

### Basic Run

```bash
docker run -d \
  --name aphrodite \
  -p 5000:5000 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_JELLYFIN_URL=https://jellyfin.example.com \
  -e APHRODITE_JELLYFIN_API_KEY=your_api_key_here \
  -e APHRODITE_JELLYFIN_USER_ID=your_user_id_here \
  yourusername/aphrodite:latest
```

### Run CLI Command Once

```bash
docker run --rm \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  -e APHRODITE_MODE=cli \
  yourusername/aphrodite:latest item your_item_id
```

### Run with Interactive Shell

```bash
docker run -it --rm \
  -v $(pwd)/settings.yaml:/app/settings.yaml:rw \
  -v $(pwd)/posters:/app/posters:rw \
  -v $(pwd)/data:/app/data:rw \
  yourusername/aphrodite:latest /bin/bash
```
