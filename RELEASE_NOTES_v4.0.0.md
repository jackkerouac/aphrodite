# Aphrodite v4.0.0 Release Notes

## 🚀 Major Frontend Integration Release

**Release Date**: June 20, 2025  
**Docker Image**: `jackkerouac/aphrodite:4.0.0`

### ✨ What's New

**Complete Frontend Integration**
- ✅ Next.js frontend fully integrated with FastAPI backend
- ✅ Beautiful, responsive UI with working Tailwind CSS v4
- ✅ Single Docker container deployment (no more separate frontend/backend)
- ✅ Frontend served directly from FastAPI at root path (`/`)

**Simplified Deployment**
- ✅ Single command deployment: `docker run -d -p 8000:8000 jackkerouac/aphrodite:4.0.0`
- ✅ Clean database on new deployments (no development data pollution)
- ✅ AMD64 optimized builds (faster, more reliable)
- ✅ Updated Docker Compose configuration

### 🔧 Technical Improvements

**Frontend**
- Next.js static export integration
- Tailwind CSS v4 with proper build process
- Responsive design for all screen sizes
- Modern React components and hooks

**Backend**
- FastAPI serves frontend static files
- API available at `/api/*` endpoints
- Improved error handling and logging
- Database migrations and clean startup

**Docker**
- Single-stage build for faster deployment
- AMD64 optimized (no ARM64 compilation issues)
- Reduced image size and startup time
- Better layer caching

### 📦 Deployment Options

**Quick Start**
```bash
docker run -d -p 8000:8000 jackkerouac/aphrodite:4.0.0
```

**Docker Compose**
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/jackkerouac/aphrodite/v4.0.0/docker-compose.yml
docker-compose up -d
```

### 🌐 Access Points

After deployment:
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### 🗃️ Database

- Clean PostgreSQL database on first run
- No development data included
- Ready for Jellyfin configuration
- Automatic schema migration

### ⚙️ Configuration

Copy `.env.example` to `.env` and configure:
- `JELLYFIN_API_KEY` - Your Jellyfin API key
- `JELLYFIN_BASE_URL` - Your Jellyfin server URL
- `DATABASE_URL` - PostgreSQL connection (auto-configured in Docker)

### 🐛 Bug Fixes

- Fixed Tailwind CSS compilation and styling issues
- Resolved frontend build and Docker integration
- Fixed database initialization and clean startup
- Eliminated ARM64 compilation failures

### 🔄 Migration from v3.x

**Database Migration**
- v4.0.0 starts with a clean database
- Export any important data from v3.x before upgrading
- Re-configure Jellyfin connection after upgrade

**Docker Images**
- New image location: `jackkerouac/aphrodite:4.0.0`
- Update docker-compose.yml to use new image
- Remove old volumes for clean startup

### 🛠️ Development

**Local Development**
```bash
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite
cp .env.example .env
docker-compose up -d
```

**Build from Source**
```bash
python build_amd64_only.py
```

### 📋 System Requirements

- Docker Engine 20.10+
- 2GB RAM minimum
- AMD64 architecture (Intel/AMD processors)
- PostgreSQL 13+ (included in Docker Compose)

### 🤝 Support

- **GitHub Issues**: https://github.com/jackkerouac/aphrodite/issues
- **Docker Hub**: https://hub.docker.com/r/jackkerouac/aphrodite
- **Documentation**: README.md in repository

### 🎯 Next Steps

1. Deploy v4.0.0
2. Configure Jellyfin connection
3. Start managing your movie posters!

---

**Full Changelog**: https://github.com/jackkerouac/aphrodite/compare/v3.0.0...v4.0.0
