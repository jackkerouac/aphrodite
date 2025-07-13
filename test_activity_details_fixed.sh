#!/bin/bash

# Test script for Activity Type Breakdown enhancement

echo "🧪 Testing Activity Type Breakdown Enhancement"
echo "=============================================="

# Test 1: Check if backend endpoint exists
echo ""
echo "📡 Testing backend endpoint availability..."
echo "GET /api/v1/analytics/activity-details/badge_application"

response1=$(curl -s -w "HTTPSTATUS:%{http_code}" http://localhost:8000/api/v1/analytics/activity-details/badge_application)
http_code1=$(echo $response1 | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
body1=$(echo $response1 | sed -e 's/HTTPSTATUS:.*//')

echo "HTTP Status: $http_code1"
if [ "$http_code1" != "200" ]; then
    echo "❌ Error response:"
    echo "$body1" | python3 -c "import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2))" 2>/dev/null || echo "$body1"
else
    echo "✅ Success!"
fi

echo ""
echo "GET /api/v1/analytics/activity-details/poster_replacement"

response2=$(curl -s -w "HTTPSTATUS:%{http_code}" http://localhost:8000/api/v1/analytics/activity-details/poster_replacement)
http_code2=$(echo $response2 | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
body2=$(echo $response2 | sed -e 's/HTTPSTATUS:.*//')

echo "HTTP Status: $http_code2"
if [ "$http_code2" != "200" ]; then
    echo "❌ Error response:"
    echo "$body2" | python3 -c "import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2))" 2>/dev/null || echo "$body2"
else
    echo "✅ Success!"
fi

# Test 3: Check response format for successful requests
if [ "$http_code1" = "200" ]; then
    echo ""
    echo "📊 Testing response format for badge_application..."
    echo "$body1" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print('Activity Type:', data.get('activity_type')); print('Total Count:', data.get('total_count')); print('Activities:', len(data.get('activities', [])))"
fi

echo ""
echo "✅ Test script completed!"
echo ""
echo "🔄 Next steps:"
echo "1. If you see 500 errors, check the Docker logs: docker logs <container_name>"
echo "2. If successful, rebuild the Docker container"
echo "3. Test the frontend interface"
echo "4. Verify clicking on activity types opens the dialog"
echo "5. Check pagination and filtering work correctly"
