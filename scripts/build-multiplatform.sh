#!/bin/bash
# Aphrodite Multi-Platform Build Script
# Builds for both AMD64 and ARM64 architectures

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

echo "🏗️ Building Aphrodite for multiple platforms (AMD64 + ARM64)..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    print_error "Docker is required for building"
    exit 1
fi

if ! docker buildx version &> /dev/null; then
    print_error "Docker Buildx is required for multi-platform builds"
    print_error "Please install Docker Desktop or enable buildx in your Docker installation"
    exit 1
fi

# Get version
VERSION=$(cat VERSION 2>/dev/null || echo "dev")
print_status "Building version: $VERSION"

# Setup buildx builder
print_status "Setting up multi-platform builder..."
docker buildx create --name aphrodite-multiplatform --use 2>/dev/null || \
docker buildx use aphrodite-multiplatform 2>/dev/null || \
{
    print_status "Creating new multi-platform builder..."
    docker buildx create --name aphrodite-multiplatform --driver docker-container --use
}

# Inspect builder capabilities
print_status "Builder capabilities:"
docker buildx inspect --bootstrap

# Check if frontend is built
if [ ! -d "frontend/.next" ]; then
    print_error "Frontend not pre-built!"
    print_error "Please run './scripts/build.sh' first to build the frontend"
    exit 1
fi

print_success "Using pre-built frontend"

# Build for multiple platforms
print_status "Building for AMD64 and ARM64 platforms..."
print_warning "This may take significantly longer than single-platform builds"

docker buildx build \
    --label "aphrodite-build" \
    --tag "aphrodite:$VERSION-multiplatform" \
    --tag "aphrodite:latest-multiplatform" \
    --platform linux/amd64,linux/arm64 \
    --file Dockerfile \
    --push=false \
    --load \
    . || {
    print_error "Multi-platform build failed"
    print_status "Falling back to current platform build..."
    docker buildx build \
        --label "aphrodite-build" \
        --tag "aphrodite:$VERSION" \
        --tag "aphrodite:latest" \
        --file Dockerfile \
        --load \
        .
    exit 0
}

print_success "Multi-platform build completed successfully!"

# Show built images
print_status "Built images:"
docker images aphrodite --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | head -5

echo ""
print_success "Multi-platform build complete! 🎉"
echo ""
print_status "Built for platforms: linux/amd64, linux/arm64"
echo "   • aphrodite:$VERSION-multiplatform"
echo "   • aphrodite:latest-multiplatform"
echo ""
print_status "To push to a registry with multi-platform support:"
echo "   docker buildx build --platform linux/amd64,linux/arm64 --push -t your-registry/aphrodite:$VERSION ."
echo ""
print_warning "Note: Multi-platform images require a registry that supports manifests"
print_warning "Local Docker daemon can only load one platform at a time"
