# Aphrodite - Poster Badge Generator for Jellyfin

Aphrodite is a Python-based application that enhances media posters by adding informational badges (audio codec, resolution, and review ratings). Built primarily for Jellyfin media servers, it features a modern Flask web interface with a Vue.js frontend.

## 🚀 Features

- Add audio codec badges to media posters (Dolby Atmos, DTS-HD, TrueHD, etc.)
- Add resolution badges (4K, 1080p, HDR, etc.)
- Add review badges with ratings from IMDb, Rotten Tomatoes, and more
- Modern web interface for easy configuration and operation
- Automatic batch processing of entire libraries
- Customizable badge positioning, colors, and styles
- Real-time job tracking and history

## 🐳 Docker Installation (Recommended)

The easiest way to get started with Aphrodite is via Docker:

```bash
# Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# Create required directories
mkdir -p ./data ./posters/original ./posters/working ./posters/modified

# Copy and edit the template configuration file
cp settings.yaml.template settings.yaml
# Edit settings.yaml with your Jellyfin credentials

# Run the container
docker-compose up -d
```

## ⚙️ Configuration

Before using Aphrodite, you need to configure it with your Jellyfin server details:

1. Copy the template configuration file:
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
     OMDB:
     - api_key: "your-omdb-api-key"  # Optional, for review badges
     TMDB:
     - api_key: "your-tmdb-api-key"  # Optional, for review badges
   ```

3. You can also customize the badge appearance in:
   - `badge_settings_audio.yml`
   - `badge_settings_resolution.yml`
   - `badge_settings_review.yml`

## 🖥️ Traditional Installation

If you prefer not to use Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/jackkerouac/aphrodite.git
   cd aphrodite
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

5. Configure your settings as described above

6. Start the web application:
   ```bash
   python -m aphrodite-web.main
   ```

7. Access the web interface at http://localhost:5000

## 🌐 Web Interface

Aphrodite provides a modern web interface that allows you to:

- Configure all application settings
- Process individual items or entire libraries
- View job history and results
- Preview modified posters

Access it at http://localhost:5000 (or whatever port you've configured)

## 📋 Command Line Usage

Aphrodite can also be used from the command line:

```bash
# Check system settings and Jellyfin connection
python aphrodite.py check

# Process a single item
python aphrodite.py item ITEM_ID

# Process an entire library
python aphrodite.py library LIBRARY_ID [--limit NUM_ITEMS]
```

## 🖌️ Badge Customization

You can customize badges by editing the settings files or through the web interface:

- Position (top-left, top-right, bottom-left, bottom-right)
- Background color and opacity
- Border color, width, and radius
- Text font, color, and size
- Enable/disable shadows and customize shadow appearance
- Use image badges or text badges

## 🛠️ Troubleshooting

### Docker Permissions

If using Docker and encountering permission issues:

```bash
# Find your user/group ID
id -u  # User ID
id -g  # Group ID

# Add to your docker-compose.yml
environment:
  - PUID=1000  # Replace with your user ID
  - PGID=1000  # Replace with your group ID
```

### Connection Issues

If you can't connect to Jellyfin:

1. Verify your Jellyfin URL, API key, and user ID
2. Ensure the Jellyfin server is accessible from your machine
3. Check for firewalls blocking connections
4. Verify that the Jellyfin API is enabled

## 📝 License

[MIT License](LICENSE)
