#!/bin/bash
# Aphrodite v2 Master Build and Release Script
# Created: 2025-06-20

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
VERSION="v4.0.2"

echo -e "${BOLD}${GREEN}🚀 Aphrodite v2 Manual Multi-Platform Docker Build & Release${NC}"
echo -e "${GREEN}===============================================================${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo -e "${GREEN}Repository: jackkerouac/aphrodite${NC}"
echo -e "${GREEN}Platforms: linux/amd64, linux/arm64${NC}"
echo -e "${GREEN}Registries: GitHub Container Registry, Docker Hub${NC}"
echo ""

# Step 1: Pre-flight checks
echo -e "${BOLD}${BLUE}Step 1: Pre-flight Checks${NC}"
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Check Docker buildx
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}❌ Docker buildx is not available${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found. Please run this script from the aphrodite repository root.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Step 2: Authentication
echo -e "${BOLD}${BLUE}Step 2: Registry Authentication${NC}"
echo -e "${YELLOW}🔐 Please ensure you have set the following environment variables:${NC}"
echo -e "  export GITHUB_TOKEN=your_github_personal_access_token"
echo -e "  export DOCKERHUB_TOKEN=your_dockerhub_access_token"
echo ""

read -p "Press Enter to continue with authentication, or Ctrl+C to cancel..."
./docker-build-scripts/authenticate.sh

echo ""

# Step 3: Build and Push
echo -e "${BOLD}${BLUE}Step 3: Multi-Platform Build and Push${NC}"
read -p "Press Enter to start the build process, or Ctrl+C to cancel..."
./docker-build-scripts/build-multiplatform.sh

echo ""

# Step 4: Verification
echo -e "${BOLD}${BLUE}Step 4: Image Verification${NC}"
read -p "Press Enter to verify the built images, or Ctrl+C to cancel..."
./docker-build-scripts/verify-images.sh

echo ""

# Step 5: Release Creation
echo -e "${BOLD}${BLUE}Step 5: GitHub Release Creation${NC}"
echo -e "${YELLOW}⚠️  This will create a new GitHub release ${VERSION}${NC}"
read -p "Press Enter to create the release, or Ctrl+C to cancel..."
./docker-build-scripts/create-release.sh

echo ""

# Step 6: Asset Attachment
echo -e "${BOLD}${BLUE}Step 6: Release Asset Attachment${NC}"
read -p "Press Enter to attach docker-compose.yml and .env.example, or Ctrl+C to cancel..."
./docker-build-scripts/attach-assets.sh

echo ""

# Step 7: Installation Testing
echo -e "${BOLD}${BLUE}Step 7: Installation Testing${NC}"
read -p "Press Enter to run end-to-end installation tests, or Ctrl+C to cancel..."
./docker-build-scripts/test-installation.sh

echo ""

# Success summary
echo -e "${BOLD}${GREEN}🎉 COMPLETE: Aphrodite ${VERSION} Multi-Platform Release${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${YELLOW}📋 What was accomplished:${NC}"
echo -e "  ✅ Multi-platform Docker images built (linux/amd64, linux/arm64)"
echo -e "  ✅ Images pushed to GitHub Container Registry and Docker Hub"
echo -e "  ✅ Images verified for functionality and accessibility"
echo -e "  ✅ GitHub release ${VERSION} created with release notes"
echo -e "  ✅ docker-compose.yml and .env.example attached to release"
echo -e "  ✅ End-to-end installation testing completed"
echo ""
echo -e "${YELLOW}🐳 Available Images:${NC}"
echo -e "  • ghcr.io/jackkerouac/aphrodite:${VERSION}"
echo -e "  • ghcr.io/jackkerouac/aphrodite:latest"
echo -e "  • jackkerouac/aphrodite:${VERSION}"
echo -e "  • jackkerouac/aphrodite:latest"
echo ""
echo -e "${YELLOW}🔗 Release URL:${NC}"
echo -e "  https://github.com/jackkerouac/aphrodite/releases/tag/${VERSION}"
echo ""
echo -e "${GREEN}🚀 Users can now install Aphrodite using the published Docker images!${NC}"
