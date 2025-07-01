#!/bin/bash
# Aphrodite Production Build Script
# Builds the complete application for production deployment

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

echo "🏗️ Building Aphrodite for production..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    print_error "Docker is required for building"
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_warning "Node.js not found - will use Docker for frontend build"
    USE_DOCKER_BUILD=true
else
    USE_DOCKER_BUILD=false
fi

# Get version
VERSION=$(cat VERSION 2>/dev/null || echo "dev")
print_status "Building version: $VERSION"

# Clean previous builds
print_status "Cleaning previous builds..."
docker system prune -f --filter "label=aphrodite-build" 2>/dev/null || true

# Build frontend (REQUIRED for Tailwind v4)
print_status "Building frontend with Tailwind v4..."

if [ "$USE_DOCKER_BUILD" = true ]; then
    print_status "Using Docker to build frontend..."
    
    # Create temporary build container
    docker run --rm \
        -v "$(pwd)/frontend:/app" \
        -w /app \
        node:18-alpine \
        sh -c "npm ci && npm run build"
else
    print_status "Building frontend natively..."
    cd frontend
    
    # Install dependencies
    npm ci
    
    # Build with Tailwind v4
    npm run build
    
    cd ..
fi

# Verify frontend build
if [ ! -d "frontend/.next" ]; then
    print_error "Frontend build failed - .next directory not found"
    print_error "This is required for Tailwind v4 and production deployment"
    exit 1
fi

print_success "Frontend build completed with Tailwind v4"

# Build production Docker image
print_status "Building production Docker image..."

# Check if buildx is available for multi-platform builds
if docker buildx version &> /dev/null; then
    print_status "Using Docker Buildx for multi-platform support..."
    
    # Create and use multi-platform builder if not exists
    docker buildx create --name aphrodite-builder --use 2>/dev/null || docker buildx use aphrodite-builder 2>/dev/null || true
    
    # Build for multiple platforms
    docker buildx build \
        --label "aphrodite-build" \
        --tag "aphrodite:$VERSION" \
        --tag "aphrodite:latest" \
        --platform linux/amd64,linux/arm64 \
        --file Dockerfile \
        --progress=plain \
        --load \
        . || {
        print_error "Multi-platform build failed, trying with build args..."
        docker buildx build \
            --label "aphrodite-build" \
            --tag "aphrodite:$VERSION" \
            --tag "aphrodite:latest" \
            --platform linux/amd64,linux/arm64 \
            --file Dockerfile \
            --build-arg BUILDPLATFORM=linux/amd64 \
            --progress=plain \
            --load \
            .
    }
else
    print_warning "Docker Buildx not available, building for current platform only"
    docker build \
        --label "aphrodite-build" \
        --tag "aphrodite:$VERSION" \
        --tag "aphrodite:latest" \
        --file Dockerfile \
        .
fi

print_success "Production image built successfully"

# Test the built image
print_status "Testing built image..."

# Start test container
TEST_CONTAINER=$(docker run -d \
    --name "aphrodite-test-$RANDOM" \
    --env DATABASE_URL="sqlite:///test.db" \
    --env ENVIRONMENT="test" \
    --publish 18000:8000 \
    "aphrodite:$VERSION")

# Wait for container to start
sleep 10

# Test health endpoint
if curl -f http://localhost:18000/health/live &> /dev/null; then
    print_success "Production image health check passed"
else
    print_error "Production image health check failed"
    docker logs "$TEST_CONTAINER"
    docker rm -f "$TEST_CONTAINER"
    exit 1
fi

# Clean up test container
docker rm -f "$TEST_CONTAINER"

# Show image info
print_status "Built image details:"
docker images aphrodite:$VERSION --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
print_success "Production build complete! 🎉"
echo ""
print_status "Built images:"
echo "   • aphrodite:$VERSION"
echo "   • aphrodite:latest"
echo ""
print_status "Next steps:"
echo "   • Test locally: docker run -p 8000:8000 aphrodite:$VERSION"
echo "   • Push to registry: docker push aphrodite:$VERSION"
echo "   • Deploy with: docker-compose up -d"
echo ""
print_warning "Remember: Frontend was built with Tailwind v4 for GitHub Actions compatibility"