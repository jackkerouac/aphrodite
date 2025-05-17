#!/bin/bash
# Simple script to debug Vue build

echo "=== Debugging Vue Build ==="
echo "Current directory: $(pwd)"

# Check if frontend directory exists
if [ -d "aphrodite-web/frontend" ]; then
  echo "Frontend directory exists"
else
  echo "ERROR: Frontend directory not found"
  exit 1
fi

# Check for package.json
if [ -f "aphrodite-web/frontend/package.json" ]; then
  echo "package.json found"
else
  echo "ERROR: package.json not found"
  exit 1
fi

# Change to frontend directory
cd aphrodite-web/frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Build
echo "Building frontend..."
npm run build

# Check build output
if [ -d "dist" ]; then
  echo "Build successful!"
  echo "dist directory contents:"
  ls -la dist/
else
  echo "ERROR: Build failed, no dist directory"
  exit 1
fi

echo "=== Debug complete ==="
