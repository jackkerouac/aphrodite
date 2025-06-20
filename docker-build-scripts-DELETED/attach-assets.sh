#!/bin/bash
# Release Assets Attachment Script
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

echo -e "${GREEN}📎 Attaching Release Assets${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo -e "${YELLOW}Please attach assets manually on GitHub${NC}"
    exit 1
fi

# Check if files exist
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
    exit 1
fi

if [ ! -f ".env.example" ]; then
    echo -e "${RED}❌ .env.example not found${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Attaching the following assets:${NC}"
echo -e "  • docker-compose.yml"
echo -e "  • .env.example"
echo ""

# Attach docker-compose.yml
echo -e "${YELLOW}📎 Attaching docker-compose.yml...${NC}"
gh release upload "$VERSION" docker-compose.yml \
    --repo "${REPO_OWNER}/${REPO_NAME}" \
    --clobber

# Attach .env.example
echo -e "${YELLOW}📎 Attaching .env.example...${NC}"
gh release upload "$VERSION" .env.example \
    --repo "${REPO_OWNER}/${REPO_NAME}" \
    --clobber

echo ""
echo -e "${GREEN}✅ Successfully attached all release assets!${NC}"
echo ""
echo -e "${YELLOW}🔗 Release URL:${NC}"
echo -e "https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/tag/${VERSION}"
echo ""
echo -e "${YELLOW}📋 Assets attached:${NC}"
echo -e "  ✅ docker-compose.yml - Ready-to-use deployment configuration"
echo -e "  ✅ .env.example - Environment configuration template"
echo ""
echo -e "${GREEN}🎉 Release ${VERSION} is now complete and ready for users!${NC}"
