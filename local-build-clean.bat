@echo off
REM local-build-clean.bat - Clean build script for Aphrodite local development
REM Use this when you need a completely fresh build (slower but more reliable)

echo 🚀 Building and running Aphrodite locally (clean mode)...

REM Step 1: Build the frontend
echo 📦 Building Next.js frontend...
cd frontend
call npm run build
cd ..

REM Step 2: Ensure all containers are stopped
echo 🛑 Stopping any running containers...
docker-compose -f docker-compose.local.yml down

REM Step 3: Clean Docker environment (removes unused images, containers, networks)
echo 🧹 Cleaning Docker environment...
docker system prune -f

REM Step 4: Build Docker images WITHOUT cache (slow but clean)
echo 🐳 Building Docker images (no cache - slow but fresh)...
docker-compose -f docker-compose.local.yml build --no-cache

REM Step 5: Start the containers without rebuilding
echo 🔄 Starting containers...
docker-compose -f docker-compose.local.yml up -d --no-build

echo ✅ Done! Aphrodite should be running at http://localhost:8000
echo 👀 Watching logs (Ctrl+C to exit)...
docker-compose -f docker-compose.local.yml logs --follow aphrodite
