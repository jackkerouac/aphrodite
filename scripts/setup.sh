#!/bin/bash

# Aphrodite v2 Docker Quick Setup Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${BLUE}🐋 $1${NC}"
    echo "=================================="
}

# Generate secure random password
generate_password() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
    else
        # Fallback for systems without openssl
        date +%s | sha256sum | base64 | head -c 25
    fi
}

# Generate secret key
generate_secret_key() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 64 | tr -d "=+/"
    else
        # Fallback
        date +%s | sha256sum | base64 | head -c 64
    fi
}

print_header "Aphrodite v2 Quick Setup"
echo ""
echo "This script will set up Aphrodite v2 with Docker in just a few steps!"
echo ""

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_step "Docker and Docker Compose are available"

# Create essential directories
print_info "Creating directories..."
mkdir -p posters images
print_step "Created posters and images directories"

# Generate .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Generating secure configuration..."
    
    POSTGRES_PASS=$(generate_password)
    REDIS_PASS=$(generate_password)
    SECRET_KEY=$(generate_secret_key)
    
    cat > .env << EOF
# Aphrodite v2 Configuration - Generated $(date)

# Database & Redis passwords (auto-generated)
POSTGRES_PASSWORD=$POSTGRES_PASS
REDIS_PASSWORD=$REDIS_PASS

# Application ports
API_PORT=8000
FRONTEND_PORT=3000

# Security key (auto-generated)
SECRET_KEY=$SECRET_KEY

# User permissions (adjust if needed)
PUID=$(id -u)
PGID=$(id -g)

# Logging
LOG_LEVEL=INFO
EOF
    
    print_step "Generated .env configuration with secure passwords"
else
    print_step ".env file already exists"
fi

# Set directory permissions
chmod 755 posters images
print_step "Set directory permissions"

echo ""
print_header "Ready to Start!"
echo ""
echo "🚀 Run these commands to start Aphrodite:"
echo ""
echo "   docker-compose up -d"
echo ""
echo "📱 Then visit: http://localhost:8000"
echo ""
echo "📋 What to do next:"
echo "   1. Wait for services to start (about 1-2 minutes)"
echo "   2. Open http://localhost:8000 in your browser"
echo "   3. Configure your Jellyfin server and API keys in the web interface"
echo "   4. Start processing your media!"
echo ""
echo "📁 Directory info:"
echo "   • ./posters/ - Your processed poster images will be saved here"
echo "   • ./images/  - Badge images and assets (customize as needed)"
echo ""
echo "🔧 Need help? Check the logs with: docker-compose logs -f"
