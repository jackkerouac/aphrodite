#!/bin/bash
# Setup script for Aphrodite Docker build scripts
# Created: 2025-06-20

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🔧 Setting up Aphrodite Docker Build Scripts${NC}"
echo ""

# Make all scripts executable
echo -e "${YELLOW}📝 Making scripts executable...${NC}"
chmod +x docker-build-scripts/*.sh

echo -e "${GREEN}✅ All scripts are now executable${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
    DOCKER_VERSION=$(docker --version)
    echo -e "   ${DOCKER_VERSION}"
else
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}   Please install Docker Desktop${NC}"
fi

# Check Docker buildx
if docker buildx version &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker buildx is available${NC}"
    BUILDX_VERSION=$(docker buildx version)
    echo -e "   ${BUILDX_VERSION}"
else
    echo -e "${RED}❌ Docker buildx is not available${NC}"
    echo -e "${YELLOW}   Please update Docker to a version with buildx support${NC}"
fi

# Check GitHub CLI
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✅ GitHub CLI is installed${NC}"
    GH_VERSION=$(gh --version | head -n 1)
    echo -e "   ${GH_VERSION}"
else
    echo -e "${YELLOW}⚠️  GitHub CLI is not installed${NC}"
    echo -e "${YELLOW}   Install from: https://cli.github.com/${NC}"
    echo -e "${YELLOW}   (Required for automated release creation)${NC}"
fi

echo ""

# Environment variables check
echo -e "${YELLOW}🔑 Environment Variables${NC}"
echo -e "${BLUE}Set these before running the build:${NC}"
echo ""
echo -e "${YELLOW}export GITHUB_TOKEN=your_github_personal_access_token${NC}"
echo -e "${YELLOW}export DOCKERHUB_TOKEN=your_dockerhub_access_token${NC}"
echo ""

if [ -n "$GITHUB_TOKEN" ]; then
    echo -e "${GREEN}✅ GITHUB_TOKEN is set${NC}"
else
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN is not set${NC}"
fi

if [ -n "$DOCKERHUB_TOKEN" ]; then
    echo -e "${GREEN}✅ DOCKERHUB_TOKEN is set${NC}"
else
    echo -e "${YELLOW}⚠️  DOCKERHUB_TOKEN is not set${NC}"
fi

echo ""

# Next steps
echo -e "${GREEN}🚀 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Set environment variables (if not already set)"
echo -e "2. Run the complete build process:"
echo -e "   ${YELLOW}./docker-build-scripts/master-build.sh${NC}"
echo ""
echo -e "Or run individual scripts as needed:"
echo -e "   ${YELLOW}./docker-build-scripts/authenticate.sh${NC}"
echo -e "   ${YELLOW}./docker-build-scripts/build-multiplatform.sh${NC}"
echo -e "   ${YELLOW}./docker-build-scripts/verify-images.sh${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   ${YELLOW}cat docker-build-scripts/README.md${NC}"
