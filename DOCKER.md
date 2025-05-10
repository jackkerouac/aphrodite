# Docker Deployment Guide for Aphrodite

This guide covers how to deploy Aphrodite using Docker containers.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose 2.0 or later (Compose V2)
- At least 2GB of available RAM
- 1GB of available disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone [repository-url]
cd aphrodite
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Required variables
PG_USER=aphrodite
PG_PASSWORD=your_secure_password  # Change this!
PG_DATABASE=aphrodite
FRONTEND_URL=http://localhost:5000

# Optional - defaults are usually fine
PORT=5000
PG_HOST=db
PG_PORT=5432
```

### 3. Development Environment

For development with hot-reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

This will start:
- Frontend development server at http://localhost:5173
- Backend API at http://localhost:5000
- PostgreSQL database at localhost:5432

### 4. Production Deployment

For production deployment:

```bash
# Build and start the containers
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop the application
docker-compose -f docker-compose.prod.yml down
```

## Architecture

The application uses a multi-stage Docker build:

1. **Frontend Build Stage**: Compiles the React application using Vite
2. **Production Stage**: Runs the Node.js backend with the compiled frontend

## Volumes

The following volumes are used for data persistence:

- `aphrodite_postgres_data`: PostgreSQL database files
- `aphrodite_data`: Application data (badges, processed images)
- `logs`: Application logs (mounted from host)

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PG_USER` | PostgreSQL username | - | Yes |
| `PG_PASSWORD` | PostgreSQL password | - | Yes |
| `PG_DATABASE` | PostgreSQL database name | - | Yes |
| `PG_HOST` | PostgreSQL host | `db` | No |
| `PG_PORT` | PostgreSQL port | `5432` | No |
| `PORT` | Backend server port | `5000` | No |
| `FRONTEND_URL` | Frontend URL for CORS | - | Yes |
| `NODE_ENV` | Node environment | `production` | No |

## Health Checks

The application includes health check endpoints:

- Backend API: `http://localhost:5000/api/health`
- PostgreSQL: Built-in Docker health check

## Updating the Application

To update to a new version:

```bash
# Pull the latest code
git pull

# Rebuild the containers
docker-compose -f docker-compose.prod.yml build --no-cache

# Restart the application
docker-compose -f docker-compose.prod.yml up -d
```

## Backup and Restore

### Database Backup

```bash
# Create a backup
docker exec aphrodite-db pg_dump -U aphrodite aphrodite > backup.sql

# Restore from backup
docker exec -i aphrodite-db psql -U aphrodite aphrodite < backup.sql
```

### Application Data Backup

```bash
# Backup application data
docker run --rm -v aphrodite_data:/data -v $(pwd):/backup alpine tar czf /backup/aphrodite-data.tar.gz -C /data .

# Restore application data
docker run --rm -v aphrodite_data:/data -v $(pwd):/backup alpine tar xzf /backup/aphrodite-data.tar.gz -C /data
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Ensure the database container is running: `docker-compose ps`
   - Check database logs: `docker logs aphrodite-db`
   - Verify environment variables in `.env`

2. **Permission Issues**
   - Ensure proper ownership of volumes
   - Run with appropriate user permissions

3. **Port Conflicts**
   - Check if ports 5000 or 5432 are already in use
   - Modify port mappings in docker-compose files if needed

### Debugging

```bash
# Access application container
docker exec -it aphrodite-app sh

# View application logs
docker logs aphrodite-app

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Restart a specific service
docker-compose -f docker-compose.prod.yml restart app
```

## Security Considerations

1. Always change default passwords in production
2. Use secrets management for sensitive data
3. Enable SSL/TLS for production deployments
4. Regularly update base images for security patches
5. Limit exposed ports to only what's necessary

## Multi-Architecture Support

The Dockerfile supports both AMD64 and ARM64 architectures. Images will be built for the host architecture automatically.

## Performance Tuning

For better performance in production:

1. Adjust PostgreSQL configuration based on available resources
2. Set appropriate Node.js memory limits
3. Use a reverse proxy (nginx) for static file serving
4. Enable gzip compression
5. Implement caching strategies

## CI/CD Integration

The Docker setup can be integrated with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker image
        run: |
          docker build -t aphrodite:latest .
          # Add deployment steps here
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)
