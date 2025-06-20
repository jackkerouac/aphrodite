# 🐋 Aphrodite v2 Docker Setup

Get Aphrodite v2 running with Docker in under 5 minutes!

## 🚀 Quick Start

### 1. Get the Files
```bash
# Create directory and download files
mkdir aphrodite && cd aphrodite

# Download docker-compose.yml
curl -L https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/docker-compose.yml -o docker-compose.yml

# Download setup script (optional but recommended)
curl -L https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/scripts/setup.sh -o setup.sh
chmod +x setup.sh
```

### 2. Quick Setup (Recommended)
```bash
# Run the setup script - it handles everything!
./setup.sh

# Start Aphrodite
docker-compose up -d
```

### 3. Manual Setup (Alternative)
```bash
# Create directories
mkdir posters images

# Create .env file
cp .env.example .env
# Edit .env with your preferred passwords

# Start services
docker-compose up -d
```

### 4. Access Aphrodite
Visit **http://localhost:8000** in your browser!

## 📋 What You Get

| Service | Description | Access |
|---------|-------------|--------|
| **Web Interface** | Configure and manage Aphrodite | http://localhost:8000 |
| **API** | REST API for automation | http://localhost:8000/docs |
| **Database** | PostgreSQL (auto-configured) | Internal only |
| **Cache** | Redis (auto-configured) | Internal only |
| **Worker** | Background processing | Internal only |

## 📁 Directory Structure

Only these directories are exposed to your host system:

```
aphrodite/
├── docker-compose.yml          # Service configuration
├── .env                        # Your settings
├── posters/                    # 📤 Processed poster images
└── images/                     # 🎨 Badge images and assets
```

All other data (logs, cache, config) is stored in Docker volumes for better performance.

## ⚙️ Configuration

### Initial Setup (Web Interface)
After starting, visit http://localhost:8000 to configure:

1. **Jellyfin Connection**
   - Server URL (e.g., http://your-jellyfin:8096)
   - API Key
   - User ID

2. **External APIs** (Optional)
   - TMDB (The Movie Database)
   - OMDB (Open Movie Database)
   - MDBList
   - AniDB (for anime)

3. **Badge Settings**
   - Audio badges (top-right)
   - Resolution badges (top-left) 
   - Awards badges (bottom-right)
   - Review badges (bottom-left)

### Environment Variables (.env)

```env
# Security (CHANGE THESE!)
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_very_long_secret_key

# Ports (change if needed)
API_PORT=8000
FRONTEND_PORT=3000

# User permissions
PUID=1000  # Your user ID (run: id -u)
PGID=1000  # Your group ID (run: id -g)
```

## 🛠️ Management

### Service Control
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Update to latest version
docker-compose pull && docker-compose up -d
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Test API health
curl http://localhost:8000/health/live

# Run comprehensive tests
curl -L https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/scripts/test-docker.sh | bash
```

## 🔧 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Ensure ports aren't in use
netstat -tlnp | grep :8000
```

**Permission issues with posters/images:**
```bash
# Fix ownership
sudo chown -R $(id -u):$(id -g) posters images

# Or set PUID/PGID in .env to match your user
echo "PUID=$(id -u)" >> .env
echo "PGID=$(id -g)" >> .env
docker-compose restart
```

**Database connection issues:**
```bash
# Check PostgreSQL health
docker-compose exec postgresql pg_isready -U aphrodite -d aphrodite_v2

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

## 🔄 Updates

```bash
# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d

# Clean up old images
docker image prune -f
```

## 🎯 What's Different from v1?

- **Simpler Setup**: Only 2 directories to manage (`posters/` and `images/`)
- **Web Configuration**: All API keys configured through the web interface
- **Better Security**: Auto-generated passwords and secure defaults
- **Improved Performance**: Internal volumes for cache and logs
- **Health Checks**: Built-in monitoring and auto-restart
- **Multi-arch**: Supports both AMD64 and ARM64 (Raspberry Pi, Apple Silicon)

## 🆘 Getting Help

1. **Check Health**: http://localhost:8000/health
2. **View Logs**: `docker-compose logs -f`
3. **GitHub Issues**: Report bugs and ask questions
4. **Community**: Join our Discord/community for support

## 🔒 Security Notes

- Always change default passwords in `.env`
- Use strong `SECRET_KEY` (generate with `openssl rand -base64 64`)
- Keep Docker images updated
- Consider running behind a reverse proxy for external access

---

**Need the old v1 setup?** Check the `v1` branch for the legacy Docker configuration.
