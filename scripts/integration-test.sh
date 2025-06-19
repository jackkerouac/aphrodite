#!/bin/bash

# Aphrodite v2 Docker Integration Test
# This script performs a complete end-to-end test of the Docker setup

set -e

echo "🧪 Aphrodite v2 Docker Integration Test"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "PASS") echo -e "${GREEN}✅ PASS${NC}: $message" ;;
        "FAIL") echo -e "${RED}❌ FAIL${NC}: $message" ;;
        "INFO") echo -e "${BLUE}ℹ️  INFO${NC}: $message" ;;
        "WARN") echo -e "${YELLOW}⚠️  WARN${NC}: $message" ;;
    esac
}

# Clean up function
cleanup() {
    print_status "INFO" "Cleaning up test environment..."
    docker-compose down -v >/dev/null 2>&1 || true
    rm -rf test-aphrodite >/dev/null 2>&1 || true
}

# Set up trap for cleanup
trap cleanup EXIT

# Test 1: Download and setup
print_status "INFO" "Testing download and setup process..."

mkdir -p test-aphrodite
cd test-aphrodite

# Download files
curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/docker-compose.yml" -o docker-compose.yml 2>/dev/null || {
    # Fallback to local files if remote not available
    cp ../docker-compose.yml .
}

curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/.env.example" -o .env.example 2>/dev/null || {
    cp ../.env.example .
}

curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/scripts/setup.sh" -o setup.sh 2>/dev/null || {
    cp ../scripts/setup.sh .
}

chmod +x setup.sh

print_status "PASS" "Downloaded configuration files"

# Test 2: Run setup script
print_status "INFO" "Running setup script..."
./setup.sh >/dev/null 2>&1

if [ -f ".env" ] && [ -d "posters" ] && [ -d "images" ]; then
    print_status "PASS" "Setup script completed successfully"
else
    print_status "FAIL" "Setup script did not create required files/directories"
    exit 1
fi

# Test 3: Start services
print_status "INFO" "Starting Docker services..."
docker-compose up -d

# Wait for services to be healthy
print_status "INFO" "Waiting for services to be healthy..."
timeout=120
count=0

while [ $count -lt $timeout ]; do
    if docker-compose ps | grep -q "healthy"; then
        sleep 5  # Wait a bit more for full initialization
        break
    fi
    sleep 1
    ((count++))
done

if [ $count -ge $timeout ]; then
    print_status "FAIL" "Services did not become healthy within timeout"
    docker-compose logs
    exit 1
fi

print_status "PASS" "Services started and are healthy"

# Test 4: Database connectivity
print_status "INFO" "Testing database connectivity..."
if docker-compose exec -T postgresql pg_isready -U aphrodite -d aphrodite_v2 >/dev/null 2>&1; then
    print_status "PASS" "Database is accessible"
else
    print_status "FAIL" "Database connectivity test failed"
    exit 1
fi

# Test 5: Redis connectivity
print_status "INFO" "Testing Redis connectivity..."
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_status "PASS" "Redis is responding"
else
    print_status "FAIL" "Redis connectivity test failed"
    exit 1
fi

# Test 6: API endpoints
print_status "INFO" "Testing API endpoints..."

# Health check
if curl -f http://localhost:8000/health/live >/dev/null 2>&1; then
    print_status "PASS" "API health endpoint is accessible"
else
    print_status "FAIL" "API health endpoint is not accessible"
    exit 1
fi

# Root endpoint
if curl -f http://localhost:8000/ >/dev/null 2>&1; then
    print_status "PASS" "API root endpoint is accessible"
else
    print_status "FAIL" "API root endpoint is not accessible"
    exit 1
fi

# Test 7: Database schema
print_status "INFO" "Testing database schema..."
table_count=$(docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' \n')

if [ "$table_count" -ge "8" ]; then
    print_status "PASS" "Database schema is properly initialized ($table_count tables)"
else
    print_status "FAIL" "Database schema initialization failed (only $table_count tables found)"
    exit 1
fi

# Test 8: Default configuration data
print_status "INFO" "Testing default configuration data..."
config_count=$(docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -t -c "SELECT COUNT(*) FROM system_config;" | tr -d ' \n')

if [ "$config_count" -ge "4" ]; then
    print_status "PASS" "Default configuration data is present ($config_count configs)"
else
    print_status "FAIL" "Default configuration data is missing (only $config_count configs found)"
    exit 1
fi

# Test 9: File permissions
print_status "INFO" "Testing file permissions..."
if docker-compose exec -T aphrodite touch /app/media/test.log >/dev/null 2>&1; then
    docker-compose exec -T aphrodite rm -f /app/media/test.log >/dev/null 2>&1
    print_status "PASS" "File permissions are correct"
else
    print_status "FAIL" "File permission test failed"
    exit 1
fi

# Test 10: Worker service
print_status "INFO" "Testing worker service..."
if docker-compose ps aphrodite-worker | grep -q "Up"; then
    print_status "PASS" "Worker service is running"
else
    print_status "FAIL" "Worker service is not running"
    exit 1
fi

echo ""
print_status "INFO" "All tests completed successfully! 🎉"
echo ""
echo "📊 Test Summary:"
echo "✅ Configuration download and setup"
echo "✅ Docker service startup"
echo "✅ Database connectivity and schema"
echo "✅ Redis connectivity"
echo "✅ API endpoint accessibility"
echo "✅ Default configuration data"
echo "✅ File permissions"
echo "✅ Background worker service"
echo ""
echo "🚀 Aphrodite v2 Docker setup is working perfectly!"
echo "   Visit http://localhost:8000 to start using it."
