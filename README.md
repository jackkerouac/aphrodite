# Aphrodite - Poster Enhancement for Media Servers

<div align="center">

**Transform your movie and TV show posters with intelligent badge overlays** 🎭

[![License](https://img.shields.io/github/license/jackkerouac/aphrodite)](LICENSE.md)
[![GitHub Release](https://img.shields.io/github/v/release/jackkerouac/aphrodite)](https://github.com/jackkerouac/aphrodite/releases)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/jackkerouac/aphrodite/releases/tag/v4.0.0)


Aphrodite is a service that automatically enhances your media posters by adding badges for audio formats, video resolution, awards, and review scores. It is designed to work with media servers like Jellyfin and Plex.

</div>

<div align="center">
<img src="https://github.com/jackkerouac/aphrodite/blob/main/example01.png" alt="Example 1" width="400"/>
<br />
<img src="https://github.com/jackkerouac/aphrodite/blob/main/example02.png" alt="Example 2" width="400"/>
</div>

## Quick Start with Docker

Aphrodite is designed to be run with Docker. It supports both AMD64 (Intel/AMD) and ARM64 (Apple Silicon, Raspberry Pi 4+) architectures.

**1. Download the necessary files:**

Create a directory for Aphrodite and download the configuration files.

```bash
# Create a directory and navigate into it
mkdir aphrodite && cd aphrodite

# Download the Docker Compose file and an example environment file
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml -o docker-compose.yml
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/default.env.example -o .env
```

**2. Configure your environment:**

Edit the `.env` file to set your passwords and other essential settings. For security, you must change the default passwords.

```env
# SECURITY - CHANGE THESE FOR PRODUCTION!
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here
SECRET_KEY=your_very_long_secret_key_64_characters_minimum_for_security

# Network (change if ports conflict)
API_PORT=8000
FRONTEND_PORT=3000
```

**3. Start Aphrodite:**

```bash
docker compose up -d
```

Once started, you can access the web interface at **http://localhost:8000** to connect to your media server and configure your badges.

## Configuration

All configuration is handled through the web interface. After the initial setup, you can connect to your media server, let Aphrodite discover your libraries, and customize the appearance and position of the badges.

## Management

Here are the basic commands for managing your Aphrodite instance:

- **Start services:** `docker compose up -d`
- **Stop services:** `docker compose down`
- **View logs:** `docker compose logs -f`
- **Update to the latest version:** `docker compose pull && docker compose up -d`

## Troubleshooting

**Services won't start:**
- Check the logs for errors: `docker compose logs`
- Make sure the ports specified in your `.env` file (e.g., 8000, 3000) are not already in use by another application.

**Permission issues on Linux/macOS:**
- If you encounter permission errors with the `posters` or `images` directories, you may need to set the user and group IDs in your `.env` file.
  ```bash
  echo "PUID=$(id -u)" >> .env
  echo "PGID=$(id -g)" >> .env
  ```
- After adding these lines, restart the services with `docker compose up -d`.

## Credits

Built with:
- FastAPI(https://fastapi.tiangolo.com/)
- [https://react.dev/]React
- [https://www.postgresql.org/]PostgreSQL
- [https://redis.io/]Redis
- [https://www.docker.com/]Docker

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.