#!/bin/bash
# Script to build and push Docker images for Aphrodite

# Configuration
IMAGE_NAME="aphrodite"
VERSION=$(cat aphrodite.py | grep -oP "VERSION\s*=\s*['\"]v\K[^'\"]*" || echo "0.1.0")
GITHUB_REPO=""  # Add your GitHub username/repo here, e.g., "yourusername/aphrodite-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Aphrodite Docker image v${VERSION}${NC}"

# Build the image
echo -e "${YELLOW}Building Docker image: ${IMAGE_NAME}:${VERSION}${NC}"
docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully built Docker image: ${IMAGE_NAME}:${VERSION}${NC}"

# Ask if we should push to GitHub Container Registry
if [ -n "$GITHUB_REPO" ]; then
    read -p "Do you want to push to GitHub Container Registry? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Tag for GitHub Container Registry
        GITHUB_IMAGE="ghcr.io/${GITHUB_REPO}/${IMAGE_NAME}"
        echo -e "${YELLOW}Tagging for GitHub Container Registry: ${GITHUB_IMAGE}:${VERSION}${NC}"
        docker tag ${IMAGE_NAME}:${VERSION} ${GITHUB_IMAGE}:${VERSION}
        docker tag ${IMAGE_NAME}:${VERSION} ${GITHUB_IMAGE}:latest
        
        echo -e "${YELLOW}Pushing to GitHub Container Registry${NC}"
        docker push ${GITHUB_IMAGE}:${VERSION}
        docker push ${GITHUB_IMAGE}:latest
        
        echo -e "${GREEN}Successfully pushed to GitHub Container Registry${NC}"
    fi
else
    echo -e "${YELLOW}No GitHub repository configured. Skipping push.${NC}"
    echo -e "${YELLOW}To enable pushing to GitHub Container Registry, edit this script and add your GitHub username/repo.${NC}"
fi

echo -e "${GREEN}Docker image build complete: ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "${GREEN}You can now run it with: docker run -p 5000:5000 ${IMAGE_NAME}:latest${NC}"
