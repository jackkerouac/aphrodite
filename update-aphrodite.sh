#!/bin/bash

echo "==================================="
echo "   Aphrodite Version Update Script"
echo "==================================="
echo

echo "Step 1: Stopping current containers..."
docker compose down
docker compose -f docker-compose.dev.yml down 2>/dev/null

echo
echo "Step 2: Removing old containers and images..."
docker container rm aphrodite aphrodite-dev 2>/dev/null
docker image rm ghcr.io/jackkerouac/aphrodite:latest 2>/dev/null
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.0 2>/dev/null
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.1 2>/dev/null

echo
echo "Step 3: Clearing Docker cache..."
docker system prune -f

echo
echo "Step 4: Pulling fresh image..."
docker pull ghcr.io/jackkerouac/aphrodite:2.2.2

echo
echo "Step 5: Starting Aphrodite with latest version..."
docker compose up -d

echo
echo "Step 6: Waiting for startup..."
sleep 5

echo
echo "Step 7: Checking version..."
docker exec aphrodite cat /app/version.txt 2>/dev/null || echo "Version file not found"

echo
echo "==================================="
echo "   Update Complete!"
echo "   Access: http://localhost:2125"
echo "==================================="
