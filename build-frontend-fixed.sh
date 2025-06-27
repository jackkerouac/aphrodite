#!/bin/bash
# Build script to ensure frontend uses correct environment for production

set -e

echo "🔧 Building Aphrodite frontend for production deployment..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "📦 Installing dependencies..."
npm ci --production=false

echo "🧹 Cleaning previous build..."
rm -rf .next

echo "🏗️ Building frontend with production environment..."
# Set NODE_ENV to production for the build
NODE_ENV=production npm run build:docker

echo "📋 Verifying build..."
if [ ! -d ".next" ]; then
    echo "❌ Error: .next directory not found after build"
    exit 1
fi

if [ ! -d ".next/static" ]; then
    echo "❌ Error: .next/static directory not found"
    exit 1
fi

echo "✅ Frontend build completed successfully!"
echo "🚀 Ready for Docker deployment"

# Show some build info
echo ""
echo "📊 Build info:"
echo "   Static files: $(find .next/static -type f | wc -l) files"
echo "   Build size: $(du -sh .next | cut -f1)"
echo ""
echo "🔗 API URL configuration:"
echo "   Development: http://localhost:8000"
echo "   Production: Dynamic (uses window.location.origin)"
echo ""
echo "✅ The frontend will now work correctly on remote machines!"
