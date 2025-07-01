#!/bin/bash
# local-build.sh - Script to build and run Aphrodite locally

# Exit on error
set -e

echo "Building and running Aphrodite locally..."

# Step 1: Build the frontend
echo "Building Next.js frontend..."
cd frontend
npm run build
cd ..

# Step 2: Ensure all containers are stopped
echo "Stopping any running containers..."
docker-compose -f docker-compose.local.yml down

# Step 3: Build Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.local.yml build

# Step 4: Start the containers without rebuilding
echo "Starting containers..."
docker-compose -f docker-compose.local.yml up -d --no-build

echo "Done! Aphrodite should be running at http://localhost:8000"
