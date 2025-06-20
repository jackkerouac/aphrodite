#!/bin/bash
# Aphrodite v2 Manual Multi-Platform Docker Build Script
# Created: 2025-06-20

set -e

# Configuration
REPO_OWNER="jackkerouac"
REPO_NAME="aphrodite"
VERSION="v4.0.2"  # Next version after v4.0.1
DOCKER_HUB_USER="jackkerouac"

# Image tags
GHCR_IMAGE="ghcr.io/${REPO_OWNER}/${REPO_NAME}"
DOCKER_HUB_IMAGE="${DOCKER_HUB_USER}/aphrodite"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Aphrodite Multi-Platform Docker Build${NC}"
echo -e "${GREEN}Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo ""

# Step 1: Setup buildx
echo -e "${YELLOW}📦 Setting up Docker buildx...${NC}"
docker buildx create --name aphrodite-builder --use --bootstrap 2>/dev/null || {
    echo -e "${YELLOW}Using existing aphrodite-builder${NC}"
    docker buildx use aphrodite-builder
}

# Step 2: Build and push multi-platform images
echo -e "${YELLOW}🔨 Building and pushing multi-platform images...${NC}"
echo -e "${GREEN}Platforms: linux/amd64, linux/arm64${NC}"
echo -e "${GREEN}Registries: GitHub Container Registry, Docker Hub${NC}"
echo ""

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t "${GHCR_IMAGE}:${VERSION}" \
    -t "${GHCR_IMAGE}:latest" \
    -t "${DOCKER_HUB_IMAGE}:${VERSION}" \
    -t "${DOCKER_HUB_IMAGE}:latest" \
    --push \
    .

echo ""
echo -e "${GREEN}✅ Multi-platform build completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 Built images:${NC}"
echo -e "  ${GHCR_IMAGE}:${VERSION}"
echo -e "  ${GHCR_IMAGE}:latest"
echo -e "  ${DOCKER_HUB_IMAGE}:${VERSION}"
echo -e "  ${DOCKER_HUB_IMAGE}:latest"
echo ""
echo -e "${YELLOW}🔍 Next steps:${NC}"
echo -e "  1. Run verification script: ./docker-build-scripts/verify-images.sh"
echo -e "  2. Create GitHub release: ./docker-build-scripts/create-release.sh"
echo -e "  3. Test installation: ./docker-build-scripts/test-installation.sh"
