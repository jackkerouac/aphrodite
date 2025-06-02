# Aphrodite

A Python-based application that adds badges and other visual elements to media posters. Aphrodite enhances your media library posters with quality indicators like resolution, audio codec, and review ratings.

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example01.png)

## Features

- Integration with your Jellyfin server
- Add resolution badges (4K, 1080p, etc.)
- Add audio codec badges (Atmos, DTS, etc.)
- Add review/rating badges (IMDb, RT, etc.)
- Automatic dominant badge detection for TV series based on most common codec/resolution across episodes
- Track which items have been processed with automatic metadata tags
- Web-based configuration interface
- Docker support for easy deployment

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example02.png)

## Quick Start (Docker)

The easiest way to get started is using the pre-built Docker image from GitHub Container Registry:

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
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_review.yml -OutFile badge_settings_awards.yml

# For Command Prompt (DOS):
curl -o docker-compose.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docker-compose.yml
curl -o settings.yaml.template https://raw.githubusercontent.com/jackkerouac/aphrodite/main/settings.yaml.template
curl -o badge_settings_audio.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_audio.yml
curl -o badge_settings_resolution.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_resolution.yml
curl -o badge_settings_review.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_review.yml
curl -o badge_settings_review.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_awards.yml

# For Bash/Linux/Mac:
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/settings.yaml.template
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_audio.yml
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_resolution.yml
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_review.yml
curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/badge_settings_awards.yml

# Create required directories
# For PowerShell:
New-Item -ItemType Directory -Force -Path .\data
New-Item -ItemType Directory -Force -Path .\posters\original
New-Item -ItemType Directory -Force -Path .\posters\working
New-Item -ItemType Directory -Force -Path .\posters\modified
New-Item -ItemType Directory -Force -Path .\fonts
New-Item -ItemType Directory -Force -Path .\images

# For Command Prompt (DOS):
mkdir data posters\original posters\working posters\modified fonts images

# For Bash/Linux/Mac:
mkdir -p ./data ./posters/original ./posters/working ./posters/modified ./fonts ./images

# You need to download badge images and fonts from the repository release page
Visit: https://github.com/jackkerouac/aphrodite/releases
Download fonts.zip and images.zip
Extract these files to the respective directories

# Create your configuration file
# For PowerShell/DOS:
copy settings.yaml.template settings.yaml
# For Bash/Linux/Mac:
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your preferred text editor

# Run the container
docker-compose up -d
```

The docker-compose.yml file is configured to pull the image directly from GitHub Container Registry (`ghcr.io/jackkerouac/aphrodite:latest`), so you don't need to clone the repository or build the image yourself.

## Accessing the Web Interface

Once the container is running, you can access the web interface at:

```
http://localhost:2125 (or whatever port you have specified in the Docker Compose file)
```

## Running the Script

You can run Aphrodite in various modes depending on your needs:

### Web Interface Mode (Default)
```bash
# Start the web interface (default)
docker-compose up -d

# Or run directly with Docker:
docker run -d -p 2125:5000 -v ./settings.yaml:/app/settings.yaml ghcr.io/jackkerouac/aphrodite:latest
```

### Command Line Processing
```bash
# Process all items once and exit
docker run --rm -v ./settings.yaml:/app/settings.yaml -v ./posters:/app/posters ghcr.io/jackkerouac/aphrodite:latest process

# Process specific library by ID
docker run --rm -v ./settings.yaml:/app/settings.yaml -v ./posters:/app/posters ghcr.io/jackkerouac/aphrodite:latest process --library-id "12345"

# Dry run mode (test without making changes)
docker run --rm -v ./settings.yaml:/app/settings.yaml -v ./posters:/app/posters ghcr.io/jackkerouac/aphrodite:latest process --dry-run

# Force reprocess all items (ignore metadata tags)
docker run --rm -v ./settings.yaml:/app/settings.yaml -v ./posters:/app/posters ghcr.io/jackkerouac/aphrodite:latest process --force
```

### Available Script Options
- `web` - Start web interface (default)
- `process` - Process posters once and exit
- `--library-id ID` - Process specific library only
- `--dry-run` - Test run without making changes
- `--force` - Reprocess all items, ignoring metadata tags
- `--help` - Show available options

## Configuration

### Required API Keys

For full functionality, you'll need:
- OMDB API key (for IMDb ratings)
- TMDB API key (for movie metadata)
- aniDB API key (for 'extra' anime metadata)
- Jellyfin API Key and User ID (if using Jellyfin integration)

Update your `settings.yaml` with these credentials.

### Awards Badge Setup (Existing Installations)

If you're upgrading an existing Aphrodite installation to include Awards badge functionality, you'll need to complete these additional steps:

1. **Download the awards mapping file:**
   ```bash
   # For PowerShell:
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/jackkerouac/aphrodite/main/data/awards_mapping.json -OutFile data/awards_mapping.json
   
   # For Command Prompt (DOS):
   curl -o data/awards_mapping.json https://raw.githubusercontent.com/jackkerouac/aphrodite/main/data/awards_mapping.json
   
   # For Bash/Linux/Mac:
   curl -O https://raw.githubusercontent.com/jackkerouac/aphrodite/main/data/awards_mapping.json
   mv awards_mapping.json data/
   ```

2. **Reorganize award images directory:**
   ```bash
   # For PowerShell:
   New-Item -ItemType Directory -Force -Path .\images\awards
   Move-Item .\images\ribbon\* .\images\awards\
   Remove-Item .\images\ribbon
   
   # For Command Prompt (DOS):
   mkdir images\awards
   move images\ribbon\* images\awards\
   rmdir images\ribbon
   
   # For Bash/Linux/Mac:
   mkdir -p ./images/awards
   mv ./images/ribbon/* ./images/awards/
   rmdir ./images/ribbon
   ```

**Note:** New installations automatically include these files and directory structure, so these steps are only necessary for existing users upgrading to Awards badge functionality.

### TV Series Badge Configuration

Aphrodite can automatically add audio codec and resolution badges to TV series by analyzing all episodes and using the most common (dominant) values. To enable this feature:

```yaml
# TV Series Badge Settings
tv_series:
  show_dominant_badges: true  # Show badges for most common codec/resolution across episodes
```

For example, if a TV series has 7 episodes with 1080p and 3 episodes with 4K, the badge will show "1080p" as it's the dominant resolution.

### Metadata Tagging Settings

Aphrodite can automatically add metadata tags to track which items have been processed:

```yaml
# Metadata Tagging Settings
metadata_tagging:
  enabled: true  # Enable/disable metadata tagging globally
  tag_name: "aphrodite-overlay"  # Tag name to add to processed items
  tag_on_success_only: true  # Only tag items that were successfully processed
```

This feature helps you:
- See which items have already been processed in your Jellyfin library
- Avoid reprocessing the same items unnecessarily
- Monitor progress through large libraries
- Use the `--force` flag to reprocess tagged items if needed

When enabled, processed items will be tagged in Jellyfin with the specified tag name. Items that already have this tag will be skipped on subsequent runs unless you use the `--force` option.

See [METADATA_TAGGING.md](METADATA_TAGGING.md) for detailed information about this feature.

## Directory Structure

- `/posters/original` - Original posters stored here
- `/posters/working` - Temporary working directory
- `/posters/modified` - Final posters with badges will appear here

## Usage

### Processing Posters

1. Access the web interface at http://localhost:2125
2. Configure you Jellyfin and Metadata Providers' settings
3. Configure your badge settings
4. Click "Process Posters"
5. Processed posters will be automatically sent to Jellyfin, and also available in the `/posters/modified` directory

### API Endpoints

Aphrodite provides a RESTful API for integration with other applications:

- `GET /api/config/` - Get current configuration
- `POST /api/config/` - Update configuration
- `GET /api/images/` - List available images
- `POST /api/process/` - Process posters
- `GET /api/check/` - Test connection

## Running Without Docker (Local Python Installation)

You can run Aphrodite directly with Python if you prefer not to use Docker:

### Prerequisites
- Python 3.10 or higher
- Node.js and npm (for web interface)
- Git (to clone the repository)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# Create and activate a virtual environment (recommended)
# For Windows:
python -m venv venv
venv\Scripts\activate

# For Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r aphrodite-web/requirements.txt

# Create required directories
# For Windows (PowerShell):
New-Item -ItemType Directory -Force -Path .\data, .\posters\original, .\posters\working, .\posters\modified

# For Windows (Command Prompt):
mkdir data posters\original posters\working posters\modified

# For Linux/Mac:
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Copy and edit the configuration file
# For Windows:
copy settings.yaml.template settings.yaml

# For Linux/Mac:
cp settings.yaml.template settings.yaml

# Edit settings.yaml with your API keys and credentials
```

### Running the Application

#### Web Interface
```bash
# Build the frontend first (one-time setup)
cd aphrodite-web/frontend
npm install
npm run build
cd ../..

# Start the web server
cd aphrodite-web
python main.py --host 0.0.0.0 --port 5000

# Access the web interface at http://localhost:5000
```

#### Command Line Interface
```bash
# Check Jellyfin connection and libraries
python aphrodite.py check

# Process a single item
python aphrodite.py item ITEM_ID

# Process an entire library
python aphrodite.py library LIBRARY_ID

# Process library with options
python aphrodite.py library LIBRARY_ID --limit 10 --no-upload --skip-processed

# Check processing status
python aphrodite.py status LIBRARY_ID

# Clean up poster directories
python aphrodite.py cleanup
```

#### Available CLI Options
- `--limit N` - Process only N items
- `--no-audio` - Skip audio codec badges
- `--no-resolution` - Skip resolution badges
- `--no-reviews` - Skip review/rating badges
- `--no-upload` - Save locally only, don't upload to Jellyfin
- `--no-metadata-tag` - Don't add metadata tags
- `--skip-processed` - Skip items already tagged
- `--retries N` - Number of retry attempts (default: 3)
- `--cleanup` - Clean up directories after processing

### Installing Additional Fonts and Images

```bash
# Download from the releases page
# Visit: https://github.com/jackkerouac/aphrodite/releases
# Download fonts.zip and images.zip

# Extract to the respective directories
# For Windows:
# Extract fonts.zip to ./fonts/
# Extract images.zip to ./images/

# For Linux/Mac:
unzip fonts.zip -d ./fonts/
unzip images.zip -d ./images/
```

## Advanced: Installation from Source (Docker Build)

If you prefer to build the Docker image from source:

```bash
# Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# Create required directories
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Copy and edit the template configuration file
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your credentials

# Build and run the Docker container
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Common Issues

- **Settings not saving**: Check that the container has write access to the settings files
- **Processing errors**: Check logs with `docker-compose logs -f`
- **Missing dependencies**: Rebuild the container with `docker-compose build`

### Docker Permissions

If you encounter permission issues, ensure the directories have the proper permissions:

```bash
# For Linux/Mac:
chmod -R 755 ./posters ./data

# For Windows (PowerShell as Administrator):
icacls .\posters /grant Everyone:F /t
icacls .\data /grant Everyone:F /t
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
