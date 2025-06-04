@echo off
echo ===================================
echo   Aphrodite Version Check
echo ===================================
echo.

echo Container Status:
docker ps --filter "name=aphrodite" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

echo.
echo Image Version (from container):
docker exec aphrodite cat /app/version.txt 2>nul || echo "Version file not found"

echo.
echo Image Info:
docker inspect aphrodite --format="{{.Config.Image}}" 2>nul || echo "Container not found"

echo.
echo Web Version Check:
echo Opening http://localhost:2125 to check web interface...
start http://localhost:2125

echo.
pause
