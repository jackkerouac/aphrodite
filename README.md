# Aphrodite

A Python-based application that adds badges and other visual elements to media posters. Aphrodite enhances your media library posters with quality indicators like resolution, audio codec, and review ratings.

![Example poster with badges](https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docs/example_poster.jpg)

## Features

- Add resolution badges (4K, 1080p, etc.)
- Add audio codec badges (Atmos, DTS, etc.)
- Add review/rating badges (IMDb, RT, etc.)
- Web-based configuration interface
- Docker support for easy deployment
- Integration with media servers like Jellyfin

## Quick Start (Docker)

The easiest way to get started is using the pre-built Docker image:

```bash
# Create a directory for Aphrodite
mkdir aphrodite && cd aphrodite

# Download docker-compose.yml and configuration files
# For PowerShell:
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docker-compose.yml -OutFile docker-compose.yml
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/settings.yaml.template -OutFile settings.yaml.template
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_audio.yml -OutFile badge_settings_audio.yml
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_resolution.yml -OutFile badge_settings_resolution.yml
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_review.yml -OutFile badge_settings_review.yml

# For Bash/Linux/Mac:
# curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docker-compose.yml
# curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/settings.yaml.template
# curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_audio.yml
# curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_resolution.yml
# curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_review.yml

# Create required directories
# For PowerShell:
New-Item -ItemType Directory -Force -Path .\data
New-Item -ItemType Directory -Force -Path .\posters\original
New-Item -ItemType Directory -Force -Path .\posters\working
New-Item -ItemType Directory -Force -Path .\posters\modified

# For Bash/Linux/Mac:
# mkdir -p ./data ./posters/original ./posters/working ./posters/modified ./fonts ./images

# Download fonts and images
# For PowerShell:
New-Item -ItemType Directory -Force -Path .\fonts
New-Item -ItemType Directory -Force -Path .\images

# You need to download badge images and fonts from the repository release page
# Visit: https://github.com/jackkerouac/aphrodite/releases
# Download fonts.zip and images.zip
# Extract these files to the respective directories

# Create your configuration file
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your preferred text editor

# Run the container (no .env file needed)
docker-compose up -d
```

The docker-compose.yml file is configured to pull the image directly from GitHub Packages, so you don't need to clone the repository or build the image yourself.

## Accessing the Web Interface

Once the container is running, you can access the web interface at:

```
http://localhost:2125
```

## Configuration

### Required API Keys

For full functionality, you'll need:
- OMDB API key (for IMDb ratings)
- TMDB API key (for movie metadata)
- Jellyfin credentials (if using Jellyfin integration)

Update your `settings.yaml` with these credentials.

## Directory Structure

- `/posters/original` - Place your original posters here
- `/posters/working` - Temporary working directory
- `/posters/modified` - Final posters with badges will appear here

## Usage

### Processing Posters

1. Place your original poster images in the `/posters/original` directory
2. Access the web interface at http://localhost:2125
3. Configure your badge settings
4. Click "Process Posters"
5. Processed posters will be available in the `/posters/modified` directory

### API Endpoints

Aphrodite provides a RESTful API for integration with other applications:

- `GET /api/config/` - Get current configuration
- `POST /api/config/` - Update configuration
- `GET /api/images/` - List available images
- `POST /api/process/` - Process posters
- `GET /api/check/` - Test connection

## Advanced: Installation from Source

If you prefer to build from source:

```bash
# Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# Create required directories
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Copy and edit the template configuration file
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your credentials

# Build and run with Docker
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Common Issues

- **Settings not saving**: Check that the container has write access to the settings files
- **Processing errors**: Check logs with `docker-compose logs -f`

### Docker Permissions

If you encounter permission issues, ensure the directories have the proper permissions:

```bash
chmod -R 755 ./posters ./data
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.