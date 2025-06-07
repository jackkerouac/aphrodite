# Aphrodite

Aphrodite automatically enhances your Jellyfin media library posters with quality indicators like resolution, audio codec, review ratings, and awards.

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example01.png)
![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example02.png)

## IMPORTANT UPGRADE NOTICE:

Beginning with v3.0.0, configuration is now stored in an embedded SQLite database instead of YAML files. When you launch v3.0.0 or later, your existing YAML settings are migrated automatically—no action required.

Support for YAML will be removed entirely in v4.0.0.

(And yes, **I know** the version numbers are borked. Thanks for bearing with me while I iron that out!)

## Features

- **Smart Badge Detection**: Automatically adds resolution (4K, 1080p), audio codec (Atmos, DTS), and review badges to your posters
- **Web Interface**: Easy-to-use web dashboard for configuration and poster management
- **Poster Manager**: Complete control over your poster collection with search, filtering, and bulk operations
- **Jellyfin Integration**: Seamlessly works with your existing Jellyfin server
- **Awards Recognition**: Highlights award-winning content with special badges
- **TV Series Support**: Intelligent dominant badge detection for series based on most common qualities
- **Background Processing**: Process large libraries without blocking the interface

## Docker Quick Start

The easiest way to run Aphrodite is with Docker:

```bash
# Create project directory
mkdir aphrodite && cd aphrodite

# Download docker-compose.yml
curl -o docker-compose.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/main/docker-compose.yml

# Start Aphrodite (configuration files are automatically created)
docker-compose up -d
```

Access the web interface at **http://localhost:2125**

## Manual Installation

If you prefer to run Aphrodite without Docker:

### Prerequisites
- Python 3.10+
- Node.js and npm
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r aphrodite-web/requirements.txt

# Setup frontend
cd aphrodite-web/frontend
npm install
npm run build
cd ../..

# Setup configuration
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your settings

# Create directories
mkdir -p data posters/original posters/working posters/modified

# Download assets from releases page
# Extract fonts.zip to ./fonts and images.zip to ./images
```

### Running
```bash
# Start web interface
cd aphrodite-web
python main.py

# Flask will serve the built Vue frontend from the `/static` path. If you
# refresh a page like `/settings`, the server will automatically return
# `index.html` so client-side routing works correctly.

# Or use command line
python aphrodite.py library YOUR_LIBRARY_ID
```

## Configuration

1. Install via Docker
2. Visit http://localhost:2125 (or wherever you installed it)
3. Visit the Settings page and enter your:
- **Jellyfin URL, API key and User ID**
- **API keys for OMDB, TMDB, aniDB, mdblist** (for ratings)
- **Badge preferences** (which types to apply)

### Notes on API keys:
- **Most** APIs are free to use, but some have limits (i.e. 1,000 calls per day, etc.)

## Contributing

Contributions welcome! Please submit Pull Requests for any improvements.

## License

MIT License - see LICENSE file for details.
