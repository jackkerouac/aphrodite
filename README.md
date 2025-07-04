# Aphrodite v4.X.X - Modern Media Poster Enhancement System

## Please note, I am aware of the batch processing issue. I am working on it, I promise!

<div align="center">

🎬 **Transform your movie and TV show posters with intelligent badge overlays** 🎭

[![License](https://img.shields.io/github/license/jackkerouac/aphrodite)](LICENSE.md)
[![GitHub Release](https://img.shields.io/github/v/release/jackkerouac/aphrodite)](https://github.com/jackkerouac/aphrodite/releases)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/jackkerouac/aphrodite/releases/tag/v4.0.0)

</div>

---

<div align="center">

![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example01.png)
![Example Image](https://github.com/jackkerouac/aphrodite/blob/main/example02.png)

</div>

---

## 🚀 **PRODUCTION READY - v4.0.0**

**Aphrodite v4.0.0 is now production-ready with:**

- **🐳 Docker-first architecture** - Single command deployment
- **🎨 Modern web interface** - Real-time configuration and monitoring
- **⚡ High-performance processing** - 3x faster with async architecture
- **🔐 Enterprise security** - Secure defaults and best practices
- **📊 Advanced analytics** - Comprehensive system monitoring

**First-time users:** Everything works out of the box with secure defaults!

**Upgrading from v3.x:** Database migration required - see migration guide below.

---

## What is Aphrodite?

Aphrodite automatically enhances your media posters by adding intelligent badges for:

- **🔊 Audio Formats** (Atmos, DTS-X, Dolby Digital+)
- **📺 Resolution** (4K, 1080p, HDR, Dolby Vision)
- **🏆 Awards** (Oscars, Emmys, Golden Globes, Critic Scores)
- **⭐ Reviews** (IMDb, Rotten Tomatoes, Metacritic)

Perfect for **Jellyfin**, **Plex**, and other media servers!

## Quick Start with Docker

### Multi-Platform Support 🏗️

Aphrodite supports both **AMD64** (Intel/AMD) and **ARM64** (Apple Silicon, Raspberry Pi 4+, AWS Graviton) architectures out of the box!

- **Apple Silicon Macs**: Native ARM64 performance
- **Raspberry Pi 4+**: Full support with 64-bit OS
- **AWS Graviton**: Optimized for ARM-based cloud instances
- **Standard x86_64**: Works on all traditional systems

### Production Setup (Recommended)

```bash
# 1. Download production files
mkdir aphrodite && cd aphrodite

# Using wget (Linux/macOS with wget)
wget https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml
wget https://github.com/jackkerouac/aphrodite/releases/latest/download/.env.example

# OR using curl (macOS/Linux/Windows with curl)
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml -o docker-compose.yml
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/.env.example -o .env.example

# Setup environment file
mv .env.example .env

# 2. Configure for production (important!)
nano .env  # Update passwords and security settings

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps
```

### Quick Development Setup

```bash
# For testing/development only
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml -o docker-compose.yml
curl -L https://github.com/jackkerouac/aphrodite/releases/latest/download/.env.example -o .env
docker-compose up -d
```

### That's it! 
Visit **http://localhost:8000** to configure your media server and start processing!

### 💾 **Migration from v3.x**

Upgrading from Aphrodite v3.x requires reconfiguration:

1. **Export your v3.x settings** (if desired)
2. **Install v4.0.0** using the setup above
3. **Reconfigure through web interface** at http://localhost:8000
4. **Import your media libraries** - automatic discovery available
5. **Customize badge settings** - improved defaults provided

**Note:** v3.x poster processing history will not be migrated, but all media will be rediscovered automatically.

---

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
Critical settings to customize in `.env`:

```env
# SECURITY - CHANGE THESE FOR PRODUCTION!
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here
SECRET_KEY=your_very_long_secret_key_64_characters_minimum_for_security

# Network (change if ports conflict)
API_PORT=8000
FRONTEND_PORT=3000

# Optional: Custom user IDs (Linux/macOS)
# PUID=1000
# PGID=1000
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
| **Dashboard** | Main control interface | http://localhost:8000 |
| **API** | REST API + documentation | http://localhost:8000/api/docs |
| **Database** | PostgreSQL (auto-managed) | Internal only |
| **Cache** | Redis (auto-managed) | Internal only |
| **Workers** | Background processing | Internal only |

## Advanced Usage

### Health & Status
```bash
# Check system health
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/health/detailed

# Start processing job (requires authentication)
curl -X POST http://localhost:8000/api/v1/workflow/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Manual Processing", "user_id": "admin"}'

# Monitor job progress
curl http://localhost:8000/api/v1/workflow/jobs/{job_id}
```

### Production Maintenance
```bash
# Update to latest version
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U aphrodite aphrodite_v2 > backup-$(date +%Y%m%d).sql

# View logs
docker-compose logs -f --tail=100

# Restart specific service
docker-compose restart api
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

**Database connection issues:**
```bash
# Check all services
docker-compose ps

# Restart database
docker-compose restart postgres redis

# Check database logs
docker-compose logs postgres
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats

# Check system health
curl http://localhost:8000/health/detailed

# Scale workers (if needed)
docker-compose up -d --scale worker=3
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

## Production Deployment

### Reverse Proxy Setup
For production, use a reverse proxy:

```nginx
# Nginx example
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Checklist
- ✅ Changed default passwords in `.env`
- ✅ Generated strong SECRET_KEY (64+ characters)
- ✅ Configured firewall rules
- ✅ Set up reverse proxy with SSL
- ✅ Regular backups scheduled
- ✅ Log monitoring configured

## Links & Resources

- **[Production Setup Guide](docs/production.md)** - Complete production deployment
- **[ARM Support Guide](docs/ARM_SUPPORT.md)** - Multi-platform builds and deployment
- **[API Documentation](http://localhost:8000/api/docs)** - Interactive API explorer
- **[Migration Guide](docs/migration.md)** - Upgrading from v3.x
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Contributing Guide](CONTRIBUTING.md)** - Development and contributions

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
