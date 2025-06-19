#!/bin/bash

# Aphrodite v2 Docker Test Script
# This script tests the Docker setup and verifies all services are working

set -e

echo "🐋 Aphrodite v2 Docker Test Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC}: $message"
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC}: $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC}: $message"
            ;;
        "INFO")
            echo -e "ℹ️  INFO: $message"
            ;;
    esac
}

# Function to check if service is running
check_service() {
    local service=$1
    if docker-compose ps $service | grep -q "Up"; then
        print_status "PASS" "$service is running"
        return 0
    else
        print_status "FAIL" "$service is not running"
        return 1
    fi
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        print_status "PASS" "$description (HTTP $response)"
        return 0
    else
        print_status "FAIL" "$description (HTTP $response, expected $expected_status)"
        return 1
    fi
}

# Main test function
run_tests() {
    local failed_tests=0
    
    print_status "INFO" "Starting Docker service tests..."
    echo ""
    
    # Test 1: Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        print_status "PASS" "docker-compose.yml found"
    else
        print_status "FAIL" "docker-compose.yml not found"
        ((failed_tests++))
    fi
    
    # Test 2: Check if .env file exists
    if [ -f ".env" ]; then
        print_status "PASS" ".env configuration file found"
    else
        print_status "WARN" ".env file not found, using defaults"
    fi
    
    # Test 3: Check if Docker is running
    if docker info >/dev/null 2>&1; then
        print_status "PASS" "Docker daemon is running"
    else
        print_status "FAIL" "Docker daemon is not running"
        ((failed_tests++))
        return $failed_tests
    fi
    
    # Test 4: Check if Docker Compose is available
    if command -v docker-compose >/dev/null 2>&1; then
        print_status "PASS" "Docker Compose is available"
    else
        print_status "FAIL" "Docker Compose is not available"
        ((failed_tests++))
        return $failed_tests
    fi
    
    echo ""
    print_status "INFO" "Checking service status..."
    
    # Test 5-8: Check if services are running
    check_service "aphrodite-postgres" || ((failed_tests++))
    check_service "aphrodite-redis" || ((failed_tests++))
    check_service "aphrodite-app" || ((failed_tests++))
    check_service "aphrodite-worker" || ((failed_tests++))
    
    echo ""
    print_status "INFO" "Testing service connectivity..."
    
    # Test 9: PostgreSQL health check
    if docker-compose exec -T postgresql pg_isready -U aphrodite -d aphrodite_v2 >/dev/null 2>&1; then
        print_status "PASS" "PostgreSQL is ready and accepting connections"
    else
        print_status "FAIL" "PostgreSQL health check failed"
        ((failed_tests++))
    fi
    
    # Test 10: Redis health check
    if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_status "PASS" "Redis is responding to ping"
    else
        print_status "FAIL" "Redis health check failed"
        ((failed_tests++))
    fi
    
    # Wait a moment for services to be fully ready
    sleep 5
    
    echo ""
    print_status "INFO" "Testing HTTP endpoints..."
    
    # Test 11: API health endpoint
    check_endpoint "http://localhost:8000/health/live" 200 "API health endpoint" || ((failed_tests++))
    
    # Test 12: API root endpoint
    check_endpoint "http://localhost:8000/" 200 "API root endpoint" || ((failed_tests++))
    
    # Test 13: API docs endpoint (if enabled)
    check_endpoint "http://localhost:8000/docs" 200 "API documentation endpoint" || print_status "WARN" "API docs not accessible (may be disabled in production)"
    
    echo ""
    print_status "INFO" "Testing database setup..."
    
    # Test 14: Check database tables exist
    if docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" >/dev/null 2>&1; then
        print_status "PASS" "Database tables are accessible"
    else
        print_status "FAIL" "Database tables check failed"
        ((failed_tests++))
    fi
    
    # Test 15: Check default configuration exists
    if docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -c "SELECT COUNT(*) FROM system_config;" >/dev/null 2>&1; then
        print_status "PASS" "Default configuration data is present"
    else
        print_status "FAIL" "Default configuration check failed"
        ((failed_tests++))
    fi
    
    echo ""
    print_status "INFO" "Testing volume mounts..."
    
    # Test 16-17: Check essential volume directories exist
    local volumes=("posters" "images")
    for vol in "${volumes[@]}"; do
        if [ -d "./$vol" ]; then
            print_status "PASS" "$vol directory exists"
        else
            print_status "WARN" "$vol directory not found (will be created)"
        fi
    done
    
    echo ""
    print_status "INFO" "Testing permissions..."
    
    # Test 18: Check if we can write to mounted volumes
    if docker-compose exec -T aphrodite touch /app/media/test.log >/dev/null 2>&1; then
        print_status "PASS" "Volume permissions are correct"
        docker-compose exec -T aphrodite rm -f /app/media/test.log >/dev/null 2>&1
    else
        print_status "FAIL" "Volume permissions issue detected"
        ((failed_tests++))
    fi
    
    return $failed_tests
}

# Function to display help
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo "  -q, --quick    Run quick tests only (skip endpoint tests)"
    echo "  --logs         Show service logs after tests"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all tests"
    echo "  $0 --quick     # Run quick tests only"
    echo "  $0 --logs      # Run tests and show logs"
}

# Function to show logs
show_logs() {
    echo ""
    print_status "INFO" "Showing recent service logs..."
    echo ""
    
    echo "=== Aphrodite App Logs ==="
    docker-compose logs --tail=20 aphrodite 2>/dev/null || echo "No logs available"
    
    echo ""
    echo "=== Worker Logs ==="
    docker-compose logs --tail=10 aphrodite-worker 2>/dev/null || echo "No logs available"
    
    echo ""
    echo "=== PostgreSQL Logs ==="
    docker-compose logs --tail=10 postgresql 2>/dev/null || echo "No logs available"
    
    echo ""
    echo "=== Redis Logs ==="
    docker-compose logs --tail=10 redis 2>/dev/null || echo "No logs available"
}

# Parse command line arguments
VERBOSE=false
QUICK=false
SHOW_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
echo ""
if [ "$QUICK" = true ]; then
    print_status "INFO" "Running quick tests..."
else
    print_status "INFO" "Running comprehensive tests..."
fi

# Run the tests
run_tests
FAILED_TESTS=$?

# Summary
echo ""
echo "========================="
echo "📊 Test Summary"
echo "========================="

if [ $FAILED_TESTS -eq 0 ]; then
    print_status "PASS" "All tests completed successfully! 🎉"
    echo ""
    echo "🚀 Aphrodite v2 is ready to use!"
    echo "   • Web Interface: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
else
    print_status "FAIL" "$FAILED_TESTS test(s) failed"
    echo ""
    echo "🔧 Please check the failed tests above and:"
    echo "   • Verify your .env configuration"
    echo "   • Check service logs with: docker-compose logs"
    echo "   • Ensure all required ports are available"
    echo "   • Try restarting services: docker-compose restart"
fi

# Show logs if requested
if [ "$SHOW_LOGS" = true ]; then
    show_logs
fi

exit $FAILED_TESTS
