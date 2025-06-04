@echo off
echo ===================================
echo   Aphrodite Version Verification
echo ===================================
echo.

echo [1/5] Docker Compose Configuration:
type docker-compose.yml | findstr "image:"

echo.
echo [2/5] Running Container Image:
docker inspect aphrodite --format="Image: {{.Config.Image}}" 2>nul || echo "❌ Container not found"

echo.
echo [3/5] Container Version File:
docker exec aphrodite cat /app/version.yml 2>nul || echo "❌ Version file not accessible"

echo.
echo [4/5] API Version Response:
curl -s "http://localhost:2125/api/version/current" 2>nul || echo "❌ API not accessible"

echo.
echo [5/5] Available Images:
echo Local Aphrodite images:
docker images | findstr "aphrodite" || echo "❌ No Aphrodite images found"

echo.
echo ===================================
echo   Quick Actions
echo ===================================
echo.
echo If versions don't match:
echo 1. Run: complete-fix.bat
echo 2. Clear browser cache (Ctrl+Shift+Delete)
echo 3. Hard refresh page (Ctrl+F5)
echo.
pause
