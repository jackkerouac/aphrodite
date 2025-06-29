#!/bin/bash
# Aphrodite Test Script
# Run all tests for the project

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🧪 Running Aphrodite test suite..."

# Check if development environment is running
if ! docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    print_status "Starting test environment..."
    docker-compose -f docker-compose.dev.yml up -d
    sleep 15
fi

# Backend Tests
print_status "Running backend tests..."
if docker-compose -f docker-compose.dev.yml exec -T api python -m pytest -v; then
    print_success "Backend tests passed"
else
    print_error "Backend tests failed"
    exit 1
fi

# Frontend Tests
print_status "Running frontend tests..."
if docker-compose -f docker-compose.dev.yml exec -T frontend npm test -- --watchAll=false; then
    print_success "Frontend tests passed"
else
    print_error "Frontend tests failed"
    exit 1
fi

# Integration Tests
print_status "Running integration tests..."

# Test API health
if curl -f http://localhost:8000/health/live &> /dev/null; then
    print_success "API health check passed"
else
    print_error "API health check failed"
    exit 1
fi

# Test Frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_success "Frontend health check passed"
else
    print_error "Frontend health check failed"
    exit 1
fi

# Test Database Connection
if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U aphrodite &> /dev/null; then
    print_success "Database connection test passed"
else
    print_error "Database connection test failed"
    exit 1
fi

# Test Redis Connection
if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis connection test passed"
else
    print_error "Redis connection test failed"
    exit 1
fi

echo ""
print_success "All tests passed! 🎉"