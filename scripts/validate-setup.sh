#!/bin/bash
# Validate Development Setup - Quick Test
# Tests that all development files are present and configured correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔍 Validating Aphrodite development setup..."

# Check required files exist
REQUIRED_FILES=(
    "CONTRIBUTING.md"
    "Dockerfile.dev"
    "docker-compose.dev.yml"
    "frontend/Dockerfile.dev"
    "docs/development/setup.md"
    "scripts/dev-setup.sh"
    "scripts/test.sh"
    "scripts/reset-db.sh"
    "scripts/build.sh"
    "scripts/clean.sh"
    "scripts/make-executable.sh"
)

print_status "Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file"
    else
        print_error "✗ $file (missing)"
        exit 1
    fi
done

# Check docker-compose.dev.yml syntax
print_status "Validating docker-compose.dev.yml syntax..."
if docker-compose -f docker-compose.dev.yml config >/dev/null 2>&1; then
    print_success "✓ docker-compose.dev.yml syntax valid"
else
    print_error "✗ docker-compose.dev.yml has syntax errors"
    exit 1
fi

# Check frontend package.json for Tailwind v4
print_status "Checking Tailwind v4 configuration..."
if grep -q '"tailwindcss": "\^4"' frontend/package.json; then
    print_success "✓ Tailwind v4 detected in frontend/package.json"
else
    print_error "✗ Tailwind v4 not found - this may cause build issues"
fi

# Check script permissions (will be set by make-executable.sh)
print_status "Checking script files..."
SCRIPT_FILES=(
    "scripts/dev-setup.sh"
    "scripts/test.sh"
    "scripts/reset-db.sh"
    "scripts/build.sh"
    "scripts/clean.sh"
)

for script in "${SCRIPT_FILES[@]}"; do
    if [ -f "$script" ]; then
        print_success "✓ $script exists"
    else
        print_error "✗ $script missing"
        exit 1
    fi
done

# Check environment files
print_status "Checking environment configuration..."
if [ -f ".env.development" ]; then
    print_success "✓ .env.development exists"
else
    print_error "✗ .env.development missing"
    exit 1
fi

# Check key directories
print_status "Checking directory structure..."
REQUIRED_DIRS=(
    "api"
    "frontend"
    "shared"
    "aphrodite_logging"
    "aphrodite_helpers"
    "docs/development"
    "scripts"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "✓ $dir/"
    else
        print_error "✗ $dir/ (missing directory)"
        exit 1
    fi
done

echo ""
print_success "🎉 Development setup validation complete!"
echo ""
print_status "Next steps:"
echo "   1. Make scripts executable: ./scripts/make-executable.sh"
echo "   2. Set up development environment: ./scripts/dev-setup.sh"
echo "   3. Start developing with hot reloading!"
echo ""
print_status "Services will be available at:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
print_status "All development files are in place and ready for contributors! 🚀"