#!/bin/bash
# Quick diagnostic script to check what's happening with API calls in the running container

echo "🔍 Debugging Aphrodite API issues in running container..."
echo "Container: aphrodite-aphrodite-1"

echo ""
echo "1. 📱 Checking frontend JavaScript files for our API fix..."
docker exec aphrodite-aphrodite-1 find /app/frontend/.next -name "*.js" -exec grep -l "buildApiUrl\|getApiBaseUrl" {} \; 2>/dev/null | head -5

echo ""
echo "2. 🌐 Testing API endpoints directly from inside container..."
echo "Health endpoint:"
docker exec aphrodite-aphrodite-1 curl -s http://localhost:8000/health/detailed | head -100

echo ""
echo "3. 🔧 Testing system info endpoint:"
docker exec aphrodite-aphrodite-1 curl -s http://localhost:8000/api/v1/system/info | head -100

echo ""
echo "4. 🎯 Testing from the HOST machine (192.168.0.110)..."
echo "Health endpoint from host:"
curl -s http://192.168.0.110:8000/health/detailed | head -100

echo ""
echo "5. 📋 Testing API endpoint from host:"
curl -s http://192.168.0.110:8000/api/v1/system/info | head -100

echo ""
echo "6. 🧪 Testing frontend static file for our fix..."
echo "Looking for API URL logic in main app bundle:"
curl -s http://192.168.0.110:8000/_next/static/chunks/app/page-*.js 2>/dev/null | grep -o "buildApiUrl\|getApiBaseUrl\|window\.location\.origin" | head -5

echo ""
echo "7. 🔎 Browser console simulation - what URL would be used?"
echo "Simulating window.location.origin on 192.168.0.110:8000..."
echo "Expected API base URL: http://192.168.0.110:8000"
echo "Expected health URL: http://192.168.0.110:8000/health/detailed"

echo ""
echo "8. 📊 Final test - can we access dashboard data API?"
curl -s http://192.168.0.110:8000/api/v1/analytics/overview | head -100
