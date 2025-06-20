# Aphrodite v4.0.0 - Modern Media Poster Enhancement System

<div align="center">

🎬 **Transform your movie and TV show posters with intelligent badge overlays** 🎭

[![License](https://img.shields.io/github/license/jackkerouac/aphrodite)](LICENSE.md)
[![GitHub Release](https://img.shields.io/github/v/release/jackkerouac/aphrodite)](https://github.com/jackkerouac/aphrodite/releases)

</div>

---

<div align="center">

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example01.png)
![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example02.png)

</div>

---

## 🚨 **BREAKING CHANGE NOTICE - v4.0.0**

**Aphrodite v4.0.0 is a complete rewrite with breaking changes:**

- **New Docker-first architecture** - Simplified deployment
- **Modern web-based configuration** - No more YAML files to edit
- **Database migration required** - All settings need to be reconfigured
- **Improved performance** - 3x faster processing with async architecture

**Migration Required:**
- Older users must reconfigure all settings through the new web interface
- Poster processing history will not be migrated
- Badge configurations will need to be recreated (defaults provided)

---

## What is Aphrodite?

Aphrodite automatically enhances your media posters by adding intelligent badges for:

- **🔊 Audio Formats** (Atmos, DTS-X, Dolby Digital+)
- **📺 Resolution** (4K, 1080p, HDR, Dolby Vision)
- **🏆 Awards** (Oscars, Emmys, Golden Globes, Critic Scores)
- **⭐ Reviews** (IMDb, Rotten Tomatoes, Metacritic)

Perfect for **Jellyfin**, **Plex**, and other media servers!

## Quick Start with Docker

### Manual Setup (3 steps)

```bash
# 1. Download files
mkdir aphrodite && cd aphrodite
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml -o docker-compose.yml
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/.env.example -o .env

# 2. Edit .env (optional - secure defaults provided)
nano .env

# 3. Start services
docker-compose up -d
```

### That's it! 
Visit **http://localhost:8000** to configure your media server and start processing!

## Configuration

### Web-Based Setup (New!)
No more editing YAML files! Configure everything through the modern web interface:

1. **Media Server Connection**
   - Jellyfin URL and API key
   - Automatic media discovery

2. **External APIs** (Optional)
   - TMDB (movie metadata)
   - OMDB (ratings)
   - MDBList (additional data)

3. **Badge Customization**
   - Position, size, and styling
   - Enable/disable specific badges
   - Custom image mappings

### Environment Variables
Only basic settings needed in `.env`:

```env
# Security (change these!)
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_very_long_secret_key

# Ports (change if needed)
API_PORT=8000
FRONTEND_PORT=3000
```

## What's New in v4.0.0?

### Modern Architecture
- **Docker-first** - Single command deployment
- **Async FastAPI** - 3x faster processing
- **React frontend** - Modern, responsive UI
- **PostgreSQL** - Reliable data storage
- **Background workers** - Non-blocking processing

### Better Security
- Auto-generated secure passwords
- JWT-based authentication
- Input validation and sanitization
- Regular security updates

### Improved User Experience  
- **Web-based configuration** - No more YAML editing
- **Real-time progress** - Watch processing in real-time
- **Better error handling** - Clear, actionable error messages
- **Responsive design** - Works on desktop and mobile

### Enhanced Performance
- **Parallel processing** - Multiple posters at once
- **Smart caching** - Faster subsequent runs
- **Incremental updates** - Only process changed media
- **Optimized database** - Faster queries and operations

## Directory Structure

```
your-aphrodite/
├── docker-compose.yml          # Service configuration
├── .env                        # Your settings
├── posters/                    # 📤 Your enhanced posters
└── images/                     # 🎨 Badge images (customizable)
```

**Simple!** Only 2 directories to manage, everything else is handled internally.

## 🛠️ Management

### PowerShell (Windows)
```powershell
# Quick setup
.\scripts\setup.ps1

# Start services  
docker-compose up -d

# Test everything
.\scripts\test-docker.ps1

# Manage services
.\scripts\manage.ps1 status
.\scripts\manage.ps1 logs
```

### Bash (Linux/macOS)
```bash
# Quick setup
./scripts/setup.sh

# Start services
docker-compose up -d

# Test everything
./scripts/test-docker.sh

# Manage services
docker-compose logs -f
docker-compose restart
```

## 📊 Service Overview

| Service | Description | Access |
|---------|-------------|--------|
| **Web Interface** | Configure and monitor | http://localhost:8000 |
| **API** | REST API for automation | http://localhost:8000/docs |
| **Database** | PostgreSQL (managed) | Internal |
| **Cache** | Redis (managed) | Internal |
| **Worker** | Background processing | Internal |

## Advanced Usage

### API Integration
```bash
# Check system health
curl http://localhost:8000/health/live

# Start processing job
curl -X POST http://localhost:8000/api/v1/jobs/process \
  -H "Content-Type: application/json" \
  -d '{"library_id": "movies"}'

# Get job status
curl http://localhost:8000/api/v1/jobs/{job_id}
```

### Automation
```bash
# Update to latest version
docker-compose pull && docker-compose up -d

# Backup configuration
docker-compose exec postgresql pg_dump -U aphrodite aphrodite_v2 > backup.sql

# View detailed logs
docker-compose logs -f --tail=100
```

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Ensure ports are free
netstat -tlnp | grep :8000  # Linux
netstat -an | findstr :8000  # Windows
```

**Permission issues:**
```bash
# Fix directory permissions
sudo chown -R $(id -u):$(id -g) posters images

# Or set user IDs in .env
echo "PUID=$(id -u)" >> .env
echo "PGID=$(id -g)" >> .env
```

**Reset everything:**
```bash
# WARNING: Deletes all data
docker-compose down -v
docker-compose up -d
```

### Getting Help

1. **Health Check**: http://localhost:8000/health
2. **Logs**: `docker-compose logs -f`
3. **GitHub Issues**: Report bugs and feature requests

## Updates

```bash
# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d

# Clean up old images  
docker image prune -f
```

## Security

- **Change default passwords** in `.env`
- **Use strong SECRET_KEY** (64+ characters)
- **Keep Docker images updated**
- **Consider reverse proxy** for external access
- **Regular backups** of database

## Documentation

- **[Docker Setup Guide](DOCKER.md)** - Detailed Docker instructions
- **[Configuration Guide](docs/configuration.md)** - Advanced configuration
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup

## Credits

Built with love using:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [PostgreSQL](https://www.postgresql.org/) - Reliable database
- [Redis](https://redis.io/) - Fast caching
- [Docker](https://www.docker.com/) - Containerization

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.

---

<div align="center">

**⭐ Star this repo if Aphrodite enhanced your media collection! ⭐**

[Report Bug](https://github.com/jackkerouac/aphrodite/issues) • [Request Feature](https://github.com/jackkerouac/aphrodite/issues)

</div>
