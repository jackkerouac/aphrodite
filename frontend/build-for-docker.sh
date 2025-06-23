#!/bin/bash
# Unix Frontend Build Script for Docker
# Handles permission issues and provides fallback options

set -e

echo "[INFO] Starting Unix-compatible frontend build..."

cd "$(dirname "$0")"

echo "[INFO] Current directory: $(pwd)"

# Clean node_modules if it exists
if [ -d "node_modules" ]; then
    echo "[INFO] Removing existing node_modules..."
    rm -rf "node_modules" || {
        echo "[WARNING] Could not remove node_modules, trying with sudo..."
        sudo rm -rf "node_modules" 2>/dev/null || echo "[WARNING] Could not clean node_modules"
    }
fi

# Clean package-lock.json to force fresh install
if [ -f "package-lock.json" ]; then
    echo "[INFO] Removing package-lock.json for fresh install..."
    rm -f "package-lock.json"
fi

# Clean .next directory for fresh build
if [ -d ".next" ]; then
    echo "[INFO] Cleaning existing build..."
    rm -rf ".next"
fi

echo "[INFO] Installing dependencies with npm install..."
npm install --no-package-lock --legacy-peer-deps

echo "[INFO] Building frontend for Docker..."
npm run build:docker

echo "[SUCCESS] Frontend build completed successfully!"

# Verify build output
if [ -d ".next" ]; then
    echo "[SUCCESS] Build directory .next exists"
else
    echo "[ERROR] Build directory .next not found"
    exit 1
fi

echo "[INFO] Frontend is ready for Docker deployment"
