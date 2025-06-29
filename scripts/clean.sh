#!/bin/bash
# Aphrodite Clean Development Environment Script
# Removes all development containers, volumes, and build artifacts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🧹 Cleaning Aphrodite development environment..."

# Confirm action
read -p "This will remove all containers, volumes, and build artifacts. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Clean operation cancelled."
    exit 0
fi

# Stop and remove all development services
print_status "Stopping development services..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Remove development volumes
print_status "Removing development volumes..."
docker volume rm -f aphrodite_postgres_data 2>/dev/null || true
docker volume rm -f aphrodite_redis_data 2>/dev/null || true
docker volume rm -f aphrodite_aphrodite_data 2>/dev/null || true
docker volume rm -f aphrodite_aphrodite_logs 2>/dev/null || true
docker volume rm -f aphrodite_aphrodite_media 2>/dev/null || true
docker volume rm -f aphrodite_aphrodite_static 2>/dev/null || true
docker volume rm -f aphrodite_frontend_node_modules 2>/dev/null || true

# Remove development images
print_status "Removing development images..."
docker image rm -f aphrodite_api 2>/dev/null || true
docker image rm -f aphrodite_frontend 2>/dev/null || true
docker image rm -f aphrodite_worker 2>/dev/null || true

# Clean frontend build artifacts
print_status "Cleaning frontend build artifacts..."
if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    print_status "Removed frontend/.next"
fi

if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    print_status "Removed frontend/node_modules"
fi

# Clean backend artifacts
print_status "Cleaning backend artifacts..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Clean logs
print_status "Cleaning logs..."
if [ -d "logs" ]; then
    rm -rf logs/*
    print_status "Cleared logs directory"
fi

if [ -d "api/logs" ]; then
    rm -rf api/logs/*
    print_status "Cleared api/logs directory"
fi

# Clean temporary files
print_status "Cleaning temporary files..."
rm -rf temp/* tmp/* 2>/dev/null || true

# Clean Docker system (careful - only remove development artifacts)
print_status "Cleaning Docker system..."
docker system prune -f --filter "label=aphrodite-dev" 2>/dev/null || true

# Clean unused Docker resources
print_status "Cleaning unused Docker resources..."
docker image prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

# Show remaining Docker resources
print_status "Remaining Docker resources:"
echo "Images:"
docker images --filter "reference=*aphrodite*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" || true
echo ""
echo "Volumes:"
docker volume ls --filter "name=aphrodite" --format "table {{.Name}}\t{{.Driver}}" || true

echo ""
print_success "Development environment cleaned! 🧹"
echo ""
print_status "To restart development:"
echo "   ./scripts/dev-setup.sh"
echo ""
print_status "Files preserved:"
echo "   • Source code"
echo "   • Configuration files (.env.*)"
echo "   • Documentation"
echo "   • Git history"