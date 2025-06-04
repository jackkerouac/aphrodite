@echo off
echo ===================================
echo   Aphrodite Complete Fix Script
echo ===================================
echo.

echo Step 1: Stopping ALL containers...
docker compose down
docker compose -f docker-compose.dev.yml down 2>nul

echo.
echo Step 2: Complete cleanup (containers, images, cache)...
docker container prune -f
docker image prune -f
docker system prune -f
docker container rm aphrodite aphrodite-dev 2>nul
docker image rm ghcr.io/jackkerouac/aphrodite:latest 2>nul
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.0 2>nul
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.1 2>nul
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.2 2>nul

echo.
echo Step 3: Pulling fresh 2.2.2 image...
docker pull ghcr.io/jackkerouac/aphrodite:2.2.2

echo.
echo Step 4: Verify downloaded image...
docker images | findstr "ghcr.io/jackkerouac/aphrodite"

echo.
echo Step 5: Clear browser cache files...
echo - Clearing version cache...
if exist "version_cache.json" del "version_cache.json"
if exist "data\version_cache.json" del "data\version_cache.json"

echo.
echo Step 6: Starting with fresh 2.2.2 image...
docker compose up -d

echo.
echo Step 7: Waiting for startup...
timeout /t 10 /nobreak >nul

echo.
echo Step 8: Comprehensive version verification...
echo Docker image info:
docker inspect aphrodite --format="Image: {{.Config.Image}}" 2>nul || echo "Container not found"

echo.
echo Container version file:
docker exec aphrodite cat /app/version.yml 2>nul || echo "Version file not accessible"

echo.
echo API version check:
curl -s http://localhost:2125/api/version/current 2>nul || echo "API not accessible yet"

echo.
echo ===================================
echo   BROWSER CACHE CLEARING REQUIRED
echo ===================================
echo.
echo IMPORTANT: After this script completes, please:
echo 1. Open your browser
echo 2. Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
echo 3. Clear "Cached images and files" for at least 24 hours
echo 4. OR use Private/Incognito mode
echo.
echo This will ensure the web interface shows the correct version.
echo.
echo Opening Aphrodite now...
start http://localhost:2125
echo.
pause
