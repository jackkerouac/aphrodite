#!/bin/bash
# Frontend build script with Tailwind CSS v4 compatibility
set -e

echo "🏗️  Building frontend with Tailwind CSS v4 support..."

# Ensure we have the right platform-specific dependencies
echo "📦 Installing platform-specific dependencies..."
npm ci --include=dev

# Clean any existing build
echo "🧹 Cleaning previous build..."
rm -rf .next

# Check if LightningCSS is available
echo "🔍 Checking LightningCSS availability..."
if node -e "require('lightningcss')" 2>/dev/null; then
    echo "✅ LightningCSS is available"
else
    echo "⚠️  LightningCSS not available, but continuing..."
fi

# Build with environment variables set
echo "🚀 Starting Next.js build..."
export NODE_ENV=production
export SKIP_ENV_VALIDATION=1
export NEXT_TELEMETRY_DISABLED=1

# Try the build
if npm run build:docker; then
    echo "✅ Frontend build successful!"
else
    echo "❌ Build failed with docker script, trying regular build..."
    if npm run build; then
        echo "✅ Frontend build successful with fallback!"
    else
        echo "❌ All build attempts failed"
        exit 1
    fi
fi

echo "📋 Build output:"
ls -la .next/

echo "🎉 Frontend build completed successfully!"
