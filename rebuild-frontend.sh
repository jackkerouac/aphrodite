#!/bin/bash

# Frontend Production Build Script
# This script rebuilds the frontend with production settings to fix localhost hardcoding

set -e

echo "🔧 Rebuilding Aphrodite Frontend for Production..."
echo "   This will fix any hardcoded localhost URLs"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "📋 Current build environment:"
echo "   NODE_ENV: ${NODE_ENV:-development}"
echo "   NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-(not set)}"
echo ""

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf .next
rm -rf out
echo "   ✅ Cleaned .next and out directories"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
    echo "   ✅ Dependencies installed"
fi

# Build for production with correct environment
echo "🏗️ Building frontend for production..."
echo "   Using .env.production file with NEXT_PUBLIC_API_URL="

# Explicitly set production environment
export NODE_ENV=production
export NEXT_PUBLIC_API_URL=""

# Build the application
npm run build

echo ""
echo "✅ Frontend build complete!"
echo ""
echo "🔍 Next steps:"
echo "   1. Run verification: node ../test-build-verification.js"
echo "   2. If verification passes, rebuild Docker container"
echo "   3. Test on remote machine"
