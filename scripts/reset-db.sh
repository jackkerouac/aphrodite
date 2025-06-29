#!/bin/bash
# Reset Development Database Script
# Completely resets the development database with fresh data

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

echo "🗄️ Resetting Aphrodite development database..."

# Confirm action
read -p "This will delete ALL data in the development database. Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Database reset cancelled."
    exit 0
fi

# Stop dependent services
print_status "Stopping API and worker services..."
docker-compose -f docker-compose.dev.yml stop api worker

# Stop and remove database container
print_status "Stopping and removing database container..."
docker-compose -f docker-compose.dev.yml stop postgres
docker-compose -f docker-compose.dev.yml rm -f postgres

# Remove database volume
print_status "Removing database volume..."
docker volume rm aphrodite_postgres_data 2>/dev/null || true

# Start database service
print_status "Starting fresh database..."
docker-compose -f docker-compose.dev.yml up -d postgres

# Wait for database to be ready
print_status "Waiting for database to initialize..."
sleep 15

# Check if database is ready
for i in {1..30}; do
    if docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite &> /dev/null; then
        break
    fi
    print_status "Waiting for database... ($i/30)"
    sleep 2
done

# Start API service
print_status "Starting API service..."
docker-compose -f docker-compose.dev.yml up -d api

# Wait for API to be ready
sleep 10

# Initialize database with default data
print_status "Initializing database with default settings..."
docker-compose -f docker-compose.dev.yml exec api python database_defaults_init.py

# Start worker service
print_status "Starting worker service..."
docker-compose -f docker-compose.dev.yml up -d worker

# Verify services are running
print_status "Verifying services..."
sleep 5

if docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite &> /dev/null; then
    print_success "Database is ready"
else
    print_error "Database failed to start properly"
    exit 1
fi

if curl -f http://localhost:8000/health/live &> /dev/null; then
    print_success "API is running"
else
    print_warning "API may still be starting up"
fi

echo ""
print_success "Database reset complete! 🎉"
echo ""
print_status "Next steps:"
echo "   1. Visit http://localhost:3000/settings to configure Jellyfin"
echo "   2. Import your anime library"
echo "   3. Set up user preferences"
echo ""
print_status "Database details:"
echo "   • Host: localhost:5433"
echo "   • Database: aphrodite"
echo "   • Username: aphrodite"
echo "   • Password: aphrodite123"