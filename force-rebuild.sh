#!/bin/bash
# Force complete frontend rebuild with cache clearing

echo "🧹 Force Rebuilding Frontend (with cache clear)"
echo "=============================================="

cd frontend

# Clear all caches and builds
echo "Clearing Next.js cache..."
rm -rf .next
rm -rf node_modules/.cache
rm -rf .cache

# Clear npm cache
echo "Clearing npm cache..."
npm cache clean --force

# Reinstall dependencies
echo "Reinstalling dependencies..."
rm -rf node_modules
npm install

# Build frontend
echo "Building frontend..."
npm run build:docker

cd ..

if [ ! -d "frontend/.next" ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

echo "✅ Frontend force rebuild complete"
echo ""
echo "🐳 Building Docker container..."
docker-compose build --no-cache

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Complete rebuild finished!"
