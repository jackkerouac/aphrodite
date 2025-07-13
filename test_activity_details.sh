#!/bin/bash

# Test script for Activity Type Breakdown enhancement

echo "🧪 Testing Activity Type Breakdown Enhancement"
echo "=============================================="

# Test 1: Check if backend endpoint exists
echo ""
echo "📡 Testing backend endpoint availability..."
echo "GET /api/v1/analytics/activity-details/badge_application"

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/api/v1/analytics/activity-details/badge_application

echo ""
echo "GET /api/v1/analytics/activity-details/poster_replacement"

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/api/v1/analytics/activity-details/poster_replacement

# Test 2: Check response format
echo ""
echo "📊 Testing response format for badge_application..."

response=$(curl -s http://localhost:8000/api/v1/analytics/activity-details/badge_application?limit=5)
echo "$response" | python3 -m json.tool | head -20

echo ""
echo "✅ Test script completed!"
echo ""
echo "🔄 Next steps:"
echo "1. Rebuild the Docker container"
echo "2. Test the frontend interface"
echo "3. Verify clicking on activity types opens the dialog"
echo "4. Check pagination and filtering work correctly"
