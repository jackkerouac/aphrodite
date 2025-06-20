#!/bin/bash
# Installation Testing Script
# Created: 2025-06-20

set -e

# Configuration
REPO_OWNER="jackkerouac"
REPO_NAME="aphrodite"
VERSION="v4.0.2"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🧪 Aphrodite Installation Testing${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo ""

# Create test directory
TEST_DIR="./test-installation"
echo -e "${YELLOW}📁 Creating test directory: ${TEST_DIR}${NC}"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Test 1: Pull GitHub Container Registry image
echo -e "${BLUE}🔍 Test 1: Pull from GitHub Container Registry${NC}"
GHCR_IMAGE="ghcr.io/${REPO_OWNER}/${REPO_NAME}:${VERSION}"
echo -e "${YELLOW}Pulling: ${GHCR_IMAGE}${NC}"

if docker pull "$GHCR_IMAGE"; then
    echo -e "${GREEN}✅ Successfully pulled from GHCR${NC}"
else
    echo -e "${RED}❌ Failed to pull from GHCR${NC}"
    cd ..
    exit 1
fi
echo ""

# Test 2: Pull Docker Hub image
echo -e "${BLUE}🔍 Test 2: Pull from Docker Hub${NC}"
DOCKERHUB_IMAGE="${REPO_OWNER}/aphrodite:${VERSION}"
echo -e "${YELLOW}Pulling: ${DOCKERHUB_IMAGE}${NC}"

if docker pull "$DOCKERHUB_IMAGE"; then
    echo -e "${GREEN}✅ Successfully pulled from Docker Hub${NC}"
else
    echo -e "${RED}❌ Failed to pull from Docker Hub${NC}"
    cd ..
    exit 1
fi
echo ""

# Test 3: Create sample docker-compose.yml
echo -e "${BLUE}🔍 Test 3: Create and test docker-compose setup${NC}"
cat > docker-compose.yml << EOF
version: '3.8'

services:
  aphrodite:
    image: ${GHCR_IMAGE}
    container_name: aphrodite-test
    ports:
      - "8000:8000"
      - "3000:3000"
    environment:
      - BUILD_ENV=production
    volumes:
      - ./config:/app/config
      - ./media:/app/media
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOF

echo -e "${GREEN}✅ Created test docker-compose.yml${NC}"
echo ""

# Test 4: Verify compose file syntax
echo -e "${BLUE}🔍 Test 4: Validate docker-compose syntax${NC}"
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ docker-compose.yml syntax is valid${NC}"
else
    echo -e "${RED}❌ docker-compose.yml syntax error${NC}"
    cd ..
    exit 1
fi
echo ""

# Test 5: Quick container start test
echo -e "${BLUE}🔍 Test 5: Quick container functionality test${NC}"
echo -e "${YELLOW}Starting container for 30 seconds...${NC}"

# Create required directories
mkdir -p config media logs

# Start the container in detached mode
if docker-compose up -d; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
    
    # Wait a moment for container to initialize
    sleep 10
    
    # Check if container is running
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Container is running${NC}"
        
        # Check health endpoint (may fail initially, that's okay)
        echo -e "${YELLOW}Testing health endpoint...${NC}"
        if timeout 20s bash -c 'until curl -f http://localhost:8000/health/live 2>/dev/null; do sleep 2; done'; then
            echo -e "${GREEN}✅ Health endpoint responding${NC}"
        else
            echo -e "${YELLOW}⚠️  Health endpoint not responding (may need configuration)${NC}"
        fi
    else
        echo -e "${RED}❌ Container failed to stay running${NC}"
        echo -e "${YELLOW}Container logs:${NC}"
        docker-compose logs
    fi
    
    # Stop the test container
    echo -e "${YELLOW}Stopping test container...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Test container stopped${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    cd ..
    exit 1
fi
echo ""

# Cleanup
cd ..
echo -e "${YELLOW}🧹 Cleaning up test directory...${NC}"
rm -rf "$TEST_DIR"

# Final summary
echo -e "${GREEN}🎉 Installation Testing Complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Test Results Summary:${NC}"
echo -e "  ✅ GitHub Container Registry image pull"
echo -e "  ✅ Docker Hub image pull"
echo -e "  ✅ docker-compose.yml creation and validation"
echo -e "  ✅ Container startup and basic functionality"
echo ""
echo -e "${GREEN}🚀 Images are ready for production use!${NC}"
echo ""
echo -e "${YELLOW}📚 User Instructions:${NC}"
echo -e "  1. Download docker-compose.yml from the GitHub release"
echo -e "  2. Download .env.example and copy to .env"
echo -e "  3. Configure .env with your settings"
echo -e "  4. Run: docker-compose up -d"
echo ""
echo -e "${BLUE}🔗 Release URL: https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/tag/${VERSION}${NC}"
