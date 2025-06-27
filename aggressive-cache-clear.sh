#!/bin/bash

# AGGRESSIVE FRONTEND CACHE CLEARING AND REBUILD
# This script clears ALL caches and rebuilds from scratch

set -e

echo "🧹 AGGRESSIVE CACHE CLEARING FOR APHRODITE FRONTEND"
echo "=================================================="
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "1️⃣ Removing ALL build artifacts..."
rm -rf .next
rm -rf out
rm -rf dist
echo "   ✅ Removed .next, out, dist"

echo ""
echo "2️⃣ Clearing Node.js caches..."
rm -rf node_modules/.cache
rm -rf .next/cache
rm -rf .npm
echo "   ✅ Cleared Node.js caches"

echo ""
echo "3️⃣ Clearing TypeScript cache..."
rm -rf .tsbuildinfo
rm -rf tsconfig.tsbuildinfo
echo "   ✅ Cleared TypeScript cache"

echo ""
echo "4️⃣ Verifying source code is correct..."
if grep -q "getApiBaseUrl" src/services/api.ts; then
    echo "   ✅ Source has getApiBaseUrl function"
else
    echo "   ❌ ERROR: Source missing getApiBaseUrl function!"
    exit 1
fi

if grep -q "window.location.origin" src/services/api.ts; then
    echo "   ✅ Source has window.location.origin logic"
else
    echo "   ❌ ERROR: Source missing window.location.origin!"
    exit 1
fi

echo ""
echo "5️⃣ Setting production environment..."
export NODE_ENV=production
export NEXT_PUBLIC_API_URL=""
echo "   NODE_ENV: $NODE_ENV"
echo "   NEXT_PUBLIC_API_URL: '$NEXT_PUBLIC_API_URL'"

echo ""
echo "6️⃣ Installing fresh dependencies..."
npm ci --cache .npm --prefer-offline=false
echo "   ✅ Fresh dependencies installed"

echo ""
echo "7️⃣ Building with production settings..."
npm run build

echo ""
echo "✅ REBUILD COMPLETE!"
echo ""
echo "🔍 VERIFICATION STEPS:"
echo "1. Run: node ../test-build-verification.js"
echo "2. Look for 'No hardcoded localhost:8000 found'"
echo "3. Look for 'Found window.location.origin references'"
echo ""
echo "If verification passes:"
echo "- Rebuild Docker container"
echo "- Test on remote machine"
echo "- Dashboard should show 'Online' status"
