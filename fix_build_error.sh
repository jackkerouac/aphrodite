#!/bin/bash

echo "🔧 Next.js Build Error Fix"
echo "=========================="

echo "Cleaning Next.js build cache and temporary files..."

# Navigate to frontend directory if not already there
cd frontend 2>/dev/null || cd ./frontend 2>/dev/null || echo "Run this from the aphrodite root directory"

echo "1. Removing .next directory..."
rm -rf .next

echo "2. Removing node_modules/.cache..."
rm -rf node_modules/.cache

echo "3. Clearing npm cache..."
npm cache clean --force

echo "4. Reinstalling dependencies..."
npm install

echo "5. Attempting build again..."
npm run build

echo ""
echo "If this still fails, try:"
echo "- Run as Administrator (Windows)"
echo "- Check disk space"
echo "- Close any file explorers/editors that might have files open"
echo "- Restart your terminal/IDE"
