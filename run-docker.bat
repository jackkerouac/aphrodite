@echo off
echo === Building Aphrodite Docker Image ===
docker-compose -f docker-compose.improved.yml build

echo === Starting Aphrodite Container ===
docker-compose -f docker-compose.improved.yml up -d

echo === Container Status ===
docker-compose -f docker-compose.improved.yml ps

echo.
echo Aphrodite is now running at http://localhost:5000
echo.
echo If you encounter any issues with the Jellyfin connection check:
echo 1. Make sure your Jellyfin server is accessible from the Docker container
echo 2. Check the container logs with: docker-compose -f docker-compose.improved.yml logs
echo 3. Verify your Jellyfin API settings in the web interface
echo.
