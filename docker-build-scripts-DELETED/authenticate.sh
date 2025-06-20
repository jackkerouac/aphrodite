#!/bin/bash
# Docker Registry Authentication Script
# Created: 2025-06-20

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔐 Docker Registry Authentication${NC}"
echo ""

# Check if tokens are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GITHUB_TOKEN environment variable is not set${NC}"
    echo -e "${YELLOW}Please set your GitHub Personal Access Token:${NC}"
    echo -e "export GITHUB_TOKEN=your_github_token_here"
    exit 1
fi

if [ -z "$DOCKERHUB_TOKEN" ]; then
    echo -e "${RED}❌ DOCKERHUB_TOKEN environment variable is not set${NC}"
    echo -e "${YELLOW}Please set your Docker Hub Access Token:${NC}"
    echo -e "export DOCKERHUB_TOKEN=your_dockerhub_token_here"
    exit 1
fi

# Login to GitHub Container Registry
echo -e "${YELLOW}🔑 Logging into GitHub Container Registry...${NC}"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u jackkerouac --password-stdin

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully logged into ghcr.io${NC}"
else
    echo -e "${RED}❌ Failed to login to ghcr.io${NC}"
    exit 1
fi

# Login to Docker Hub
echo -e "${YELLOW}🔑 Logging into Docker Hub...${NC}"
echo "$DOCKERHUB_TOKEN" | docker login -u jackkerouac --password-stdin

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully logged into Docker Hub${NC}"
else
    echo -e "${RED}❌ Failed to login to Docker Hub${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All registries authenticated successfully!${NC}"
echo -e "${YELLOW}You can now run the build script: ./docker-build-scripts/build-multiplatform.sh${NC}"
