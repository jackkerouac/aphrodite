#!/usr/bin/env bash

echo "🧹 Nuclear clean - removing all build artifacts..."

# Remove Next.js build directory completely
rm -rf .next

# Remove all node_modules cache
rm -rf node_modules/.cache

# Remove any TypeScript build info files
find . -name "*.tsbuildinfo" -delete 2>/dev/null

# Clear npm cache (if any)
npm cache clean --force 2>/dev/null

echo "✅ Nuclear clean completed. Ready for fresh build."
