#!/bin/bash
# Complete build script that rebuilds frontend before Docker image

echo "🏗️  Building Aphrodite with Fresh Frontend"
echo "========================================="

# Step 1: Rebuild the frontend
echo "1️⃣  Rebuilding Next.js frontend..."
cd frontend
npm run build:docker
cd ..

if [ ! -d "frontend/.next" ]; then
    echo "❌ Frontend build failed - .next directory not found"
    exit 1
fi

echo "✅ Frontend rebuilt successfully"

# Step 2: Build Docker image
echo ""
echo "2️⃣  Building Docker image..."
docker-compose build --no-cache

echo ""
echo "3️⃣  Starting services..."
docker-compose up -d

echo ""
echo "✅ Complete build finished!"
echo "🌐 Visit: http://localhost:8000"
