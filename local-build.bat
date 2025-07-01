@echo off
REM local-build.bat - Fast build script for Aphrodite local development
REM Uses Docker cache for faster builds. Use local-build-clean.bat for a fresh build.

echo 🚀 Building and running Aphrodite locally...

REM Step 1: Build the frontend
echo 📦 Building Next.js frontend...
cd frontend
call npm run build
cd ..

REM Step 2: Ensure all containers are stopped
echo 🛑 Stopping any running containers...
docker-compose -f docker-compose.local.yml down

REM Step 3: Build Docker images WITH cache (much faster)
echo 🐳 Building Docker images (using cache for speed)...
docker-compose -f docker-compose.local.yml build

REM Step 4: Start the containers without rebuilding
echo 🔄 Starting containers...
docker-compose -f docker-compose.local.yml up -d --no-build

echo ✅ Done! Aphrodite should be running at http://localhost:8000
echo 💡 Tip: Use local-build-clean.bat if you need a completely fresh build
echo 👀 Watching logs (Ctrl+C to exit)...
docker-compose -f docker-compose.local.yml logs --follow aphrodite
