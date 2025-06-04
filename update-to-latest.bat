@echo off
echo ===================================
echo   Future-Proof Aphrodite Updater
echo ===================================
echo.

set COMPOSE_FILE=docker-compose.yml

echo Step 1: Checking current configuration...
echo Current image in %COMPOSE_FILE%:
type %COMPOSE_FILE% | findstr "image:" | findstr "aphrodite"

echo.
echo Step 2: Stopping current containers...
docker compose down 2>nul

echo.
echo Step 3: Cleaning up old images and cache...
echo Removing old containers...
docker container prune -f 2>nul

echo Removing unused images...
docker image prune -f 2>nul

echo.
echo Step 4: Pulling latest image specified in compose file...
docker compose pull

echo.
echo Step 5: Starting with updated image...
docker compose up -d

echo.
echo Step 6: Waiting for startup...
timeout /t 10 /nobreak >nul

echo.
echo Step 7: Version verification...
echo Container image:
docker inspect aphrodite --format="{{.Config.Image}}" 2>nul || echo "❌ Container not found"

echo.
echo Container internal version:
docker exec aphrodite cat /app/version.yml 2>nul || echo "❌ Version file not accessible"

echo.
echo API version:
curl -s "http://localhost:2125/api/version/current" 2>nul || echo "❌ API not ready yet"

echo.
echo ===================================
echo   Update Complete!
echo ===================================
echo.
echo IMPORTANT: Clear your browser cache for version display:
echo 1. Press Ctrl+Shift+Delete
echo 2. Clear "Cached images and files"
echo 3. Or use Private/Incognito mode
echo.
echo Opening Aphrodite...
start http://localhost:2125
echo.
pause
