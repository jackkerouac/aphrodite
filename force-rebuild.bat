@echo off
REM Force complete frontend rebuild with cache clearing

echo 🧹 Force Rebuilding Frontend (with cache clear)
echo ==============================================

cd frontend

REM Clear all caches and builds
echo Clearing Next.js cache...
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache
if exist .cache rmdir /s /q .cache

REM Clear npm cache
echo Clearing npm cache...
npm cache clean --force

REM Reinstall dependencies
echo Reinstalling dependencies...
if exist node_modules rmdir /s /q node_modules
call npm install

REM Build frontend
echo Building frontend...
call npm run build:docker

cd ..

if not exist "frontend\.next" (
    echo ❌ Frontend build failed
    pause
    exit /b 1
)

echo ✅ Frontend force rebuild complete
echo.
echo 🐳 Building Docker container...
docker-compose build --no-cache

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ✅ Complete rebuild finished!
pause
