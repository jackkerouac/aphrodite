# Development Setup Guide

This guide covers everything you need to know to set up Aphrodite for local development.

## Quick Start

The fastest way to get started:

```bash
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite
./scripts/dev-setup.sh
```

This will set up a complete development environment with hot reloading in under 5 minutes.

## Prerequisites

### Required Software

- **Docker Desktop** (latest stable version)
- **Docker Compose** (included with Docker Desktop)
- **Git** (for cloning the repository)

### Optional (for native development)

- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)
- **PostgreSQL** (if running database natively)
- **Redis** (if running cache natively)

## Development Modes

### Mode 1: Full Docker Development (Recommended)

Everything runs in containers with hot reloading:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Services:**
- Frontend: http://localhost:3000 (Next.js + Tailwind v4)
- Backend: http://localhost:8000 (FastAPI)
- Database: PostgreSQL on port 5433
- Cache: Redis on port 6379

**Benefits:**
- Consistent environment across all platforms
- No need to install Node.js/Python locally
- Easy to reset and clean up
- Matches production environment closely

### Mode 2: Hybrid Development

Database in Docker, frontend/backend native:

```bash
# Start databases
docker-compose -f docker-compose.dev.yml up postgres redis -d

# Backend (terminal 1)
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend (terminal 2)  
cd frontend
npm install
npm run dev
```

**Benefits:**
- Faster startup times
- Better debugging experience
- IDE integration works better
- Can use your preferred Python/Node versions

## Important: Tailwind v4 Requirements

⚠️ **Critical for Contributors**: This project uses **Tailwind CSS v4**, which requires special handling:

1. **Frontend must be built locally** before creating production Docker images
2. This is **required for GitHub Actions** to work properly
3. Always run `npm run build` in the frontend directory before production deployment

```bash
cd frontend
npm run build  # This creates .next directory needed for production
```

## Environment Configuration

### Development Environment Variables

Copy the development environment file:

```bash
cp .env.development .env.local
# Edit .env.local with your specific settings
```

**Key Variables:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://aphrodite:aphrodite123@localhost:5433/aphrodite

# Cache
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=true
LOG_LEVEL=debug
ENVIRONMENT=development

# Jellyfin (configure via web interface)
JELLYFIN_URL=http://your-jellyfin-server:8096
JELLYFIN_API_KEY=your-api-key
JELLYFIN_USER_ID=your-user-id
```

### Database Configuration

**Development Database:**
- Host: `localhost:5433`
- Database: `aphrodite`
- Username: `aphrodite`
- Password: `aphrodite123`

**Connecting with external tools:**
```bash
# Using psql
psql -h localhost -p 5433 -U aphrodite -d aphrodite

# Using pgAdmin or other GUI tools
Host: localhost
Port: 5433
Database: aphrodite
Username: aphrodite
Password: aphrodite123
```

## Development Workflow

### Making Changes

1. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Make your changes:**
   - Backend: Edit files in `api/`, changes auto-reload
   - Frontend: Edit files in `frontend/src/`, changes auto-reload
   - Shared: Edit files in `shared/`, both services restart

3. **View changes:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Hot Reloading

**Backend (FastAPI):**
- Uvicorn watches for file changes in `/app`
- Auto-reloads on Python file modifications
- Logs show reload messages

**Frontend (Next.js):**
- Webpack dev server provides hot module replacement
- Changes appear instantly in browser
- Build errors show in browser overlay

### Common Development Tasks

**View logs:**
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f api
docker-compose -f docker-compose.dev.yml logs -f frontend
```

**Restart services:**
```bash
# Restart specific service
docker-compose -f docker-compose.dev.yml restart api

# Restart all services
docker-compose -f docker-compose.dev.yml restart
```

**Rebuild after dependency changes:**
```bash
# Rebuild and restart
docker-compose -f docker-compose.dev.yml up --build

# Rebuild specific service
docker-compose -f docker-compose.dev.yml build api
docker-compose -f docker-compose.dev.yml up -d api
```

**Reset database:**
```bash
./scripts/reset-db.sh
```

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# View database logs
docker-compose -f docker-compose.dev.yml logs postgres

# Reset database
./scripts/reset-db.sh
```

**Frontend not loading:**
```bash
# Check if frontend is running
curl http://localhost:3000

# Check frontend logs
docker-compose -f docker-compose.dev.yml logs frontend

# Restart frontend
docker-compose -f docker-compose.dev.yml restart frontend
```

**API not responding:**
```bash
# Check API health
curl http://localhost:8000/health/live

# Check API logs
docker-compose -f docker-compose.dev.yml logs api

# Restart API
docker-compose -f docker-compose.dev.yml restart api
```

**Hot reloading not working:**
```bash
# For file system issues on Windows/macOS
# Edit docker-compose.dev.yml and add:
# volumes:
#   - ./api:/app/api:cached    # macOS
#   - ./api:/app/api:delegated # Windows
```

**Tailwind v4 build issues:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Performance Issues

**Slow startup:**
- Use hybrid development mode (databases in Docker, apps native)
- Increase Docker Desktop memory allocation
- Use volume mount optimization for your platform

**High CPU usage:**
- Reduce file watching scope in development
- Use `docker-compose logs` to identify resource-heavy containers
- Consider running fewer services simultaneously

### Port Conflicts

If ports are already in use:

```bash
# Change ports in docker-compose.dev.yml
services:
  frontend:
    ports:
      - "3001:3000"  # Change frontend port
  api:
    ports:
      - "8001:8000"  # Change API port
  postgres:
    ports:
      - "5434:5432"  # Change database port
```

## Development Scripts

All development scripts are in the `scripts/` directory:

```bash
# Make scripts executable (if needed)
chmod +x scripts/*.sh

# Available scripts
./scripts/dev-setup.sh    # Complete environment setup
./scripts/test.sh         # Run all tests
./scripts/reset-db.sh     # Reset development database
./scripts/build.sh        # Build for production
./scripts/clean.sh        # Clean development environment
```

## Next Steps

Once your development environment is running:

1. **Configure Jellyfin**: Visit http://localhost:3000/settings
2. **Import library**: Connect to your Jellyfin server and import anime
3. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
4. **Start developing**: Make changes and see them reflected immediately

For more detailed guides, see:
- [Backend Development](backend.md)
- [Frontend Development](frontend.md)
- [Database Development](database.md)
- [Testing Guide](testing.md)
