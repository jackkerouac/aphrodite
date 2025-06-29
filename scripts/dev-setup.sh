#!/bin/bash
# Aphrodite Development Setup Script
# Automated setup for new contributors

set -e

echo "🚀 Setting up Aphrodite development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git."
    exit 1
fi

print_success "All prerequisites found!"

# Create .env.development if it doesn't exist
if [ ! -f .env.development ]; then
    print_status "Creating .env.development..."
    cp .env.development .env.development
    print_success ".env.development created"
else
    print_status ".env.development already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data media api/static/originals api/static/preview api/static/processed
mkdir -p api/static/awards/black api/static/awards/white
print_success "Directories created"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Pull base images
print_status "Pulling base Docker images..."
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull postgres:15-alpine
docker pull redis:7-alpine

# Build development images
print_status "Building development images..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Start database services first
print_status "Starting database services..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Check database health
if ! docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite &> /dev/null; then
    print_warning "Database not ready yet, waiting longer..."
    sleep 10
fi

# Initialize database
print_status "Initializing database..."
docker-compose -f docker-compose.dev.yml up -d api
sleep 5

# Run database initialization if needed
docker-compose -f docker-compose.dev.yml exec api python database_defaults_init.py || true

# Start all services
print_status "Starting all development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 15

# Check service health
print_status "Checking service health..."

# Check API
if curl -f http://localhost:8000/health/live &> /dev/null; then
    print_success "Backend API is running"
else
    print_warning "Backend API may still be starting up"
fi

# Check Frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_success "Frontend is running"
else
    print_warning "Frontend may still be starting up"
fi

# Show service status
print_status "Service status:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📍 Access your services:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo "   • Database:  localhost:5433 (user: aphrodite, password: aphrodite123)"
echo "   • Redis:     localhost:6379"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs:        docker-compose -f docker-compose.dev.yml logs -f"
echo "   • Stop services:    docker-compose -f docker-compose.dev.yml down"
echo "   • Restart service:  docker-compose -f docker-compose.dev.yml restart <service>"
echo "   • Rebuild:          docker-compose -f docker-compose.dev.yml up --build"
echo ""
echo "📚 Next steps:"
echo "   1. Configure Jellyfin connection at http://localhost:3000/settings"
echo "   2. Import your anime library"
echo "   3. Start developing! Code changes will auto-reload."
echo ""
echo "❓ Need help? Check CONTRIBUTING.md or open a GitHub Discussion."
