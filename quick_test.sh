#!/bin/bash
# Quick test script for Aphrodite Docker infrastructure
# Run this to verify everything works before pushing to production

set -e  # Exit on any error

echo "🚀 Aphrodite v4.0.0 Docker Quick Test"
echo "===================================="

# Check prerequisites
echo "📋 Checking prerequisites..."
docker --version || { echo "❌ Docker not found"; exit 1; }
docker compose version || { echo "❌ Docker Compose not found"; exit 1; }
echo "✅ Docker and Docker Compose available"

# Build the image
echo ""
echo "🏗️  Building Docker image..."
docker build -t aphrodite:test .
echo "✅ Image built successfully"

# Test basic functionality
echo ""
echo "🧪 Testing basic functionality..."
docker run --rm aphrodite:test python -c "import api.main; print('✅ FastAPI imports work')"
docker run --rm aphrodite:test python -c "from api.app.routes.health import router; print('✅ Health routes available')"

# Quick smoke test with compose
echo ""
echo "🐳 Quick smoke test with Docker Compose..."
cp .env.docker.template .env
echo "POSTGRES_PASSWORD=test123" >> .env
echo "SECRET_KEY=test-secret-key-for-docker-testing-only" >> .env

# Start just the databases first
docker compose -f docker-compose.dev.yml up -d postgres redis

# Wait a bit for databases to start
echo "⏳ Waiting for databases to start..."
sleep 10

# Check database health
echo "🔍 Checking database health..."
docker compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite || {
    echo "❌ PostgreSQL not ready"
    docker compose -f docker-compose.dev.yml logs postgres
    exit 1
}

docker compose -f docker-compose.dev.yml exec redis redis-cli ping || {
    echo "❌ Redis not ready" 
    docker compose -f docker-compose.dev.yml logs redis
    exit 1
}

echo "✅ Databases are healthy"

# Start the application
echo "🚀 Starting Aphrodite application..."
docker compose -f docker-compose.dev.yml up -d aphrodite

# Wait for app to start
echo "⏳ Waiting for application to start..."
sleep 15

# Test health endpoint
echo "🏥 Testing health endpoint..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health/live > /dev/null 2>&1; then
        echo "✅ Application is healthy and responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Application failed to start"
        docker compose -f docker-compose.dev.yml logs aphrodite
        exit 1
    fi
    sleep 1
done

# Test API root
echo "🌐 Testing API root endpoint..."
curl -s http://localhost:8000/ | head -100

echo ""
echo "🧹 Cleaning up..."
docker compose -f docker-compose.dev.yml down -v

echo ""
echo "🎉 All tests passed! Docker infrastructure is ready."
echo ""
echo "📋 Next steps:"
echo "1. Tag for registry: docker tag aphrodite:test ghcr.io/jackkerouac/aphrodite:latest"
echo "2. Build multi-platform: python build_multiplatform.py --setup-buildx --push"
echo "3. Deploy production: docker-compose up -d"
