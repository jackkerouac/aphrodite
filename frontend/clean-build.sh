#!/usr/bin/env bash

# Clean build script to remove all cached artifacts and rebuild from scratch

echo "🧹 Cleaning all Next.js build artifacts..."

# Remove build directories
rm -rf .next
rm -rf node_modules/.cache
rm -rf out

# Remove TypeScript build info
find . -name "*.tsbuildinfo" -delete

# Clear Next.js cache
npx next clean

echo "✅ Clean completed. Run 'npm run build' to rebuild."
