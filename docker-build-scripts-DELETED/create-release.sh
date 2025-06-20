#!/bin/bash
# GitHub Release Creation Script
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
NC='\033[0m'

echo -e "${GREEN}📦 Creating GitHub Release${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo -e "${YELLOW}Please install GitHub CLI: https://cli.github.com/${NC}"
    echo -e "${YELLOW}Alternative: Create the release manually on GitHub${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
    echo -e "${YELLOW}Run: gh auth login${NC}"
    exit 1
fi

# Create release notes
RELEASE_NOTES="## 🚀 Aphrodite ${VERSION} - Multi-Platform Docker Release

### ✨ What's New
- **Multi-platform Docker images** now available for both AMD64 and ARM64 architectures
- **Improved Docker build process** with enhanced reliability
- **Enhanced frontend build** with proper dependency management
- **Container registry support** for both GitHub Container Registry and Docker Hub

### 🐳 Docker Images
**GitHub Container Registry:**
\`\`\`bash
docker pull ghcr.io/${REPO_OWNER}/${REPO_NAME}:${VERSION}
docker pull ghcr.io/${REPO_OWNER}/${REPO_NAME}:latest
\`\`\`

**Docker Hub:**
\`\`\`bash
docker pull ${REPO_OWNER}/aphrodite:${VERSION}
docker pull ${REPO_OWNER}/aphrodite:latest
\`\`\`

### 🏗️ Supported Platforms
- **linux/amd64** - Standard x86_64 systems
- **linux/arm64** - ARM-based systems (Apple Silicon, Raspberry Pi 4+, etc.)

### 📋 Installation
1. Download the \`docker-compose.yml\` and \`.env.example\` files from this release
2. Copy \`.env.example\` to \`.env\` and configure your settings
3. Run: \`docker-compose up -d\`

### 🔧 What's Fixed
- Docker build layer caching issues resolved
- Frontend build process optimized
- ESLint configuration conflicts eliminated
- Multi-platform compatibility ensured

### 📚 Documentation
See the attached \`docker-compose.yml\` for easy deployment setup.

---
**Full Changelog**: https://github.com/${REPO_OWNER}/${REPO_NAME}/compare/v4.0.1...${VERSION}"

echo -e "${YELLOW}📝 Creating release with the following details:${NC}"
echo -e "Repository: ${REPO_OWNER}/${REPO_NAME}"
echo -e "Tag: ${VERSION}"
echo -e "Title: Aphrodite ${VERSION} - Multi-Platform Docker Release"
echo ""

# Create the release
echo -e "${YELLOW}🚀 Creating GitHub release...${NC}"

gh release create "$VERSION" \
    --repo "${REPO_OWNER}/${REPO_NAME}" \
    --title "Aphrodite ${VERSION} - Multi-Platform Docker Release" \
    --notes "$RELEASE_NOTES" \
    --latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully created GitHub release ${VERSION}${NC}"
    echo ""
    echo -e "${YELLOW}📎 Next: Attach release assets${NC}"
    echo -e "Run: ./docker-build-scripts/attach-assets.sh"
else
    echo -e "${RED}❌ Failed to create GitHub release${NC}"
    exit 1
fi
