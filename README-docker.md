# Aphrodite Docker

This Docker container provides a user-friendly web interface for the Aphrodite-Python script, which enhances Jellyfin media posters by adding informational badges.

## Quick Start

The easiest way to get started is with Docker Compose:

```bash
docker-compose up -d
```

Then open http://localhost:5000 in your browser.

## Configuration

### Default Configuration

The container comes with default configuration files. You can modify these files through the web interface.

### Persistent Configuration

To make your configuration changes persist between container restarts, mount the configuration files as volumes:

```yaml
volumes:
  - ./settings.yaml:/app/settings.yaml
  - ./badge_settings_audio.yml:/app/badge_settings_audio.yml
  - ./badge_settings_resolution.yml:/app/badge_settings_resolution.yml
  - ./badge_settings_review.yml:/app/badge_settings_review.yml
```

### Data Persistence

To keep your posters and job history between container restarts, mount these directories:

```yaml
volumes:
  - ./posters:/app/posters
  - ./data:/app/data
```

## Full docker-compose.yml Example

```yaml
version: '3'
services:
  aphrodite:
    image: aphrodite:latest
    build: .
    ports:
      - "5000:5000"
    volumes:
      # Configuration files (optional - will use defaults if not mounted)
      - ./settings.yaml:/app/settings.yaml
      - ./badge_settings_audio.yml:/app/badge_settings_audio.yml
      - ./badge_settings_resolution.yml:/app/badge_settings_resolution.yml
      - ./badge_settings_review.yml:/app/badge_settings_review.yml
      
      # Data persistence (recommended)
      - ./posters:/app/posters
      - ./data:/app/data
    restart: unless-stopped
```

## Usage

1. Open http://localhost:5000 in your browser
2. Configure your Jellyfin API settings in the Settings tab
3. Go to the Execute tab to process your media
4. View results in the Preview tab

## Requirements

- Docker and Docker Compose
- A running Jellyfin server

## Building Locally

If you want to build the container locally:

```bash
docker build -t aphrodite:latest .
```

## Notes

- If you don't mount configuration files as volumes, your configuration changes will be lost when the container is restarted.
- The web interface will show whether the configuration files are writable.
- If you make changes to the configuration files directly (not through the web interface), you may need to restart the container.

## License

This project is licensed under the same license as Aphrodite-Python.
