# Aphrodite

Aphrodite automatically enhances your Jellyfin media library posters with quality indicators like resolution, audio codec, review ratings, and awards.

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example01.png)
![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example02.png)

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

# Or use command line
python aphrodite.py library YOUR_LIBRARY_ID
```

## Configuration

Edit `settings.yaml` with your:
- **Jellyfin URL and API key**
- **API keys for OMDB, TMDB** (for ratings)
- **Badge preferences** (which types to apply)

Required API keys:
- OMDB API key (free at omdbapi.com)
- TMDB API key (free at themoviedb.org)

## Contributing

Contributions welcome! Please submit Pull Requests for any improvements.

## License

MIT License - see LICENSE file for details.
