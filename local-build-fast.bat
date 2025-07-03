@echo off
REM local-build-fast.bat - Faster build script for Aphrodite local development
REM This version uses Docker cache for faster builds during development

echo 🚀 Building and running Aphrodite locally (fast mode)...

REM Step 1: Build the frontend
echo 📦 Building Next.js frontend...
REM cd frontend
REM call npm run build
REM cd ..

REM Step 2: Ensure all containers are stopped
echo 🛑 Stopping any running containers...
docker-compose -f docker-compose.local.yml down

REM Step 3: Build Docker images WITH cache (much faster)
echo 🐳 Building Docker images (using cache)...
docker-compose -f docker-compose.local.yml build

REM Step 4: Start the containers without rebuilding
echo 🔄 Starting containers...
docker-compose -f docker-compose.local.yml up -d --no-build

echo ✅ Done! Aphrodite should be running at http://localhost:8000
echo 👀 Watching logs (Ctrl+C to exit)...
docker-compose -f docker-compose.local.yml logs --follow aphrodite
