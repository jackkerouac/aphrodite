#!/bin/bash

# Host Directory Setup Script for Aphrodite
# This script creates the necessary directory structure when using host mounts

echo "🚀 Setting up Aphrodite host directories..."

# Base directory
BASE_DIR="/home/nas/docker/aphrodite-testing"

# Create all necessary directories
directories=(
    "$BASE_DIR/data"
    "$BASE_DIR/data/cache"
    "$BASE_DIR/data/config"
    "$BASE_DIR/logs"
    "$BASE_DIR/media"
    "$BASE_DIR/media/temp"
    "$BASE_DIR/media/preview"
    "$BASE_DIR/media/processed"
    "$BASE_DIR/static"
)

echo "📁 Creating directory structure..."
for dir in "${directories[@]}"; do
    if mkdir -p "$dir"; then
        echo "✅ Created: $dir"
    else
        echo "❌ Failed to create: $dir"
    fi
done

# Set proper permissions (optional, uncomment if needed)
# echo "🔐 Setting permissions..."
# chmod -R 755 "$BASE_DIR"

echo ""
echo "🎉 Directory setup complete!"
echo ""
echo "📋 Directory structure:"
echo "├── $BASE_DIR/"
echo "│   ├── data/            # Application data"
echo "│   │   ├── cache/       # Cache files"
echo "│   │   └── config/      # Configuration files"
echo "│   ├── logs/            # Application logs"
echo "│   ├── media/           # Media files"
echo "│   │   ├── temp/        # Temporary files"
echo "│   │   ├── preview/     # Preview images"
echo "│   │   └── processed/   # Processed posters"
echo "│   └── static/          # Original static files"
echo ""
echo "🐳 You can now run:"
echo "   docker-compose down"
echo "   docker-compose up -d"
echo ""
echo "🌐 The preview files should now be accessible at:"
echo "   http://your-server:8000/api/v1/static/preview/"
