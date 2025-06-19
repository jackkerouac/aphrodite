#!/bin/bash

# Aphrodite v2 One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main/install.sh | bash

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🐋 Aphrodite v2 Quick Installer${NC}"
echo "=================================="
echo ""

# Check prerequisites
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is required but not installed."
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose is required but not installed."
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create directory
INSTALL_DIR="aphrodite-v2"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory $INSTALL_DIR already exists.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo -e "${GREEN}✅ Created directory $INSTALL_DIR${NC}"

# Download files
echo "📥 Downloading configuration files..."

BASE_URL="https://raw.githubusercontent.com/YOUR_USERNAME/aphrodite/main"

curl -fsSL "$BASE_URL/docker-compose.yml" -o docker-compose.yml
curl -fsSL "$BASE_URL/.env.example" -o .env.example
curl -fsSL "$BASE_URL/scripts/setup.sh" -o setup.sh

chmod +x setup.sh

echo -e "${GREEN}✅ Downloaded configuration files${NC}"

# Run setup
echo "🔧 Running setup..."
./setup.sh

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo "🚀 Start Aphrodite with:"
echo "   docker-compose up -d"
echo ""
echo "📱 Then visit: http://localhost:8000"
echo ""
echo "📁 You're now in the $INSTALL_DIR directory"
echo "   All your poster files will be saved to ./posters/"
echo ""
