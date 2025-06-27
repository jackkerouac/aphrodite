# Aphrodite v4.0.0 Production Deployment Checklist

## Pre-Deployment Checklist ✅

### 1. **Docker Configuration**
- [x] ✅ Fixed docker-compose.yml database port (5432 internal, 5433 external)
- [x] ✅ Updated .env.docker.template with correct DATABASE_URL
- [x] ✅ Dockerfile follows production best practices (non-root user, health checks)
- [x] ✅ Added production startup script with database initialization
- [x] ✅ Updated .dockerignore to exclude test/development files

### 2. **Path Configuration**  
- [x] ✅ All font paths use Docker-compatible `/app/assets/fonts/` 
- [x] ✅ All image paths use Docker-compatible `/app/assets/images/`
- [x] ✅ Created symlinks for backward compatibility
- [x] ✅ No hardcoded localhost or development paths found

### 3. **Database Initialization**
- [x] ✅ Created production initialization script (`init-badge-settings-production.py`)
- [x] ✅ Badge settings match your local configuration but with Docker paths
- [x] ✅ Placeholder API settings (users configure via web interface)
- [x] ✅ Database connection recovery mechanisms in place

### 4. **GitHub Actions**
- [x] ✅ GitHub Action correctly checks for pre-built frontend (Tailwind v4 compatible)
- [x] ✅ Builds on release publication 
- [x] ✅ Pushes to GitHub Container Registry

### 5. **Environment Variables**
- [x] ✅ All critical environment variables defined in .env.docker.template
- [x] ✅ Database URL uses service names for Docker internal communication
- [x] ✅ Redis configuration for Docker networking
- [x] ✅ Removed insecure defaults from docker-compose.yml

## Deployment Process

### Step 1: Pre-Build Frontend Locally
```bash
# Build the frontend with Tailwind v4
cd frontend
npm run build
cd ..
```

### Step 2: Test Production Configuration
```bash
# Run the production readiness test
python test-production-readiness.py
```

### Step 3: Create Release
1. Commit all changes
2. Create a git tag: `git tag v4.0.0-production`
3. Push tag: `git push origin v4.0.0-production`
4. Create GitHub release - this will trigger the Docker build

### Step 4: Deploy
```bash
# Copy the template and customize
cp .env.docker.template .env

# Edit .env with your settings:
# - Change POSTGRES_PASSWORD 
# - Change SECRET_KEY
# - Set your external ports
# - Configure any API keys (or do via web interface)

# Deploy
docker-compose up -d
```

### Step 5: Post-Deployment Verification
```bash
# Check all services are running
docker-compose ps

# Check logs
docker-compose logs aphrodite

# Test API health
curl http://localhost:8000/health/live

# Access web interface
# Go to http://localhost:8000
```

## Production Notes

### Database Initialization
- ✅ The container automatically initializes database tables on first run
- ✅ Default badge settings are inserted with Docker-compatible paths
- ✅ API keys can be configured via the web interface after startup

### Font and Image Assets
- ✅ All fonts are copied to `/app/assets/fonts/`
- ✅ All images are copied to `/app/assets/images/`
- ✅ Symlinks created for backward compatibility (`/app/fonts` -> `/app/assets/fonts`)

### Networking
- ✅ Internal services communicate via Docker service names
- ✅ External ports are configurable via environment variables
- ✅ No hardcoded localhost references

### Security
- ✅ Runs as non-root user (`aphrodite`)
- ✅ Uses proper environment variable handling
- ✅ Database passwords must be changed from defaults
- ✅ Secret key must be changed from default

### Monitoring
- ✅ Health checks configured for all services
- ✅ Proper logging configuration
- ✅ Container restart policies set to `unless-stopped`

## Fixes Applied

1. **Fixed database connection**: Changed `postgres:5433` to `postgres:5432` in docker-compose.yml
2. **Updated template**: Fixed DATABASE_URL in .env.docker.template  
3. **Font paths**: All badge settings now use `/app/assets/fonts/` paths
4. **Image paths**: All badge settings now use `/app/assets/images/` paths
5. **Production script**: Created startup script with database initialization
6. **Configuration**: Badge settings match your local config but with Docker paths

## Ready for Release! 🚀

The application is now production-ready with:
- Proper Docker networking
- Production-compatible paths
- Automatic database initialization
- Your current badge configurations
- Security best practices
- GitHub Actions for automated builds
