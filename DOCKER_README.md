# Aphrodite v4.0.0 Docker Infrastructure

This directory contains the production-ready Docker infrastructure for Aphrodite v4.0.0, a modern media poster enhancement system with FastAPI backend and Next.js frontend.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Production Deployment (Recommended)

1. **Create environment file:**
   ```bash
   cp .env.docker.template .env
   # Edit .env with your secure passwords and configuration
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health/live
   - API docs: http://localhost:8000/docs (if enabled)

### Development Build

1. **Build and test locally:**
   ```bash
   python test_docker.py
   ```

2. **Or build manually:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

## 📋 Architecture

- **Frontend**: Next.js (built into the image)
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7 (optional)
- **Background Jobs**: Celery (optional)

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | Database password | `changeme` |
| `SECRET_KEY` | Application secret key | Required in production |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level | `info` |

### Services

- **aphrodite**: Main application (port 8000)
- **postgres**: Database (port 5432)
- **redis**: Cache and message broker (port 6379)
- **celery-worker**: Background tasks (optional, use `--profile worker`)

## 🔍 Monitoring

### Health Checks
- Application: `curl http://localhost:8000/health/live`
- Database: `docker-compose exec postgres pg_isready -U aphrodite`
- Redis: `docker-compose exec redis redis-cli ping`

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f aphrodite
```

## 💾 Data Persistence

Persistent data is stored in Docker volumes:
- `postgres_data`: Database files
- `redis_data`: Redis persistence
- `media_data`: Media files and uploads
- `logs_data`: Application logs
- `config_data`: Configuration files

## 🛠️ Troubleshooting

### Common Issues

1. **Application won't start:**
   ```bash
   # Check logs
   docker-compose logs aphrodite
   
   # Verify database connection
   docker-compose exec postgres pg_isready -U aphrodite
   ```

2. **Database connection errors:**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Port conflicts:**
   ```bash
   # Change ports in docker-compose.yml if needed
   # Default ports: 8000 (app), 5432 (postgres), 6379 (redis)
   ```

### Rebuilding

```bash
# Rebuild from scratch
docker-compose down -v
docker system prune -f
docker-compose -f docker-compose.dev.yml build --no-cache
```

## 🔄 Updates

### Updating to New Version

```bash
# Pull latest image
docker-compose pull

# Restart services
docker-compose up -d
```

### Building New Version

```bash
# Build new image
docker build -t ghcr.io/jackkerouac/aphrodite:v4.0.1 .

# Test locally
docker tag ghcr.io/jackkerouac/aphrodite:v4.0.1 ghcr.io/jackkerouac/aphrodite:latest
docker-compose up -d
```

## 🏗️ Multi-Platform Builds

```bash
# Setup buildx for multi-platform
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/jackkerouac/aphrodite:latest \
  --push .
```

## 📚 Files Reference

- `Dockerfile`: Multi-stage production build
- `docker-compose.yml`: Production deployment
- `docker-compose.dev.yml`: Development build
- `.dockerignore`: Build context exclusions
- `test_docker.py`: Build and test script
- `.env.docker.template`: Environment template

## 🎯 Production Checklist

- [ ] Set secure `POSTGRES_PASSWORD`
- [ ] Set secure `SECRET_KEY` (32+ characters)
- [ ] Configure proper `FRONTEND_URL`
- [ ] Review CORS origins
- [ ] Set up SSL/TLS proxy (nginx/traefik)
- [ ] Configure log rotation
- [ ] Set up monitoring (optional)
- [ ] Configure backups

## 🔐 Security Notes

1. **Never use default passwords in production**
2. **Use strong secret keys (32+ random characters)**
3. **Run behind a reverse proxy with SSL**
4. **Regularly update base images**
5. **Monitor security advisories**

## 📞 Support

For issues with the Docker infrastructure:
1. Check logs: `docker-compose logs`
2. Verify health checks
3. Review environment configuration
4. Run test script: `python test_docker.py`

For application-specific issues, refer to the main README.md.
