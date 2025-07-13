#!/bin/bash

# Enhanced test script for Activity Type Breakdown enhancement

echo "🧪 Testing Activity Type Breakdown Enhancement"
echo "=============================================="

# Test 0: Check workflow models availability
echo ""
echo "🔍 Checking workflow models availability..."
echo "GET /api/v1/debug/workflow-models"

debug_response=$(curl -s -w "HTTPSTATUS:%{http_code}" http://localhost:8000/api/v1/debug/workflow-models)
debug_http_code=$(echo $debug_response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
debug_body=$(echo $debug_response | sed -e 's/HTTPSTATUS:.*//')

echo "HTTP Status: $debug_http_code"
if [ "$debug_http_code" = "200" ]; then
    echo "✅ Debug endpoint accessible"
    echo "$debug_body" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print('BatchJobModel Available:', data.get('batch_job_model')); print('Table Exists:', data.get('batch_job_table_exists')); print('Job Count:', data.get('batch_job_count')); error=data.get('error'); print('Error:', error) if error else None"
else
    echo "❌ Debug endpoint failed"
fi

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

# Test 4: Test filtering
echo ""
echo "🔍 Testing filtering functionality..."
echo "GET /api/v1/analytics/activity-details/badge_application?limit=2&days=30"

filter_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "http://localhost:8000/api/v1/analytics/activity-details/badge_application?limit=2&days=30")
filter_http_code=$(echo $filter_response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
filter_body=$(echo $filter_response | sed -e 's/HTTPSTATUS:.*//')

echo "HTTP Status: $filter_http_code"
if [ "$filter_http_code" = "200" ]; then
    echo "✅ Filtering works!"
    echo "$filter_body" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); pagination=data.get('pagination', {}); print('Page:', pagination.get('page')); print('Limit:', pagination.get('limit')); print('Total Pages:', pagination.get('total_pages'))"
else
    echo "❌ Filtering failed"
fi

echo ""
echo "✅ Test script completed!"
echo ""
echo "🔄 Next steps:"
echo "1. If you see 500 errors, check the Docker logs: docker logs <container_name>"
echo "2. If workflow models are not available, the database may need migration"
echo "3. If successful, test the frontend interface"
echo "4. Verify clicking on activity types opens the dialog"
echo "5. Check pagination and filtering work correctly"

# Summary
echo ""
echo "📋 Test Summary:"
echo "Debug endpoint: $debug_http_code"
echo "Badge application endpoint: $http_code1"
echo "Poster replacement endpoint: $http_code2"
echo "Filtering test: $filter_http_code"

if [ "$http_code1" = "200" ] && [ "$http_code2" = "200" ]; then
    echo "🎉 All main endpoints working!"
else
    echo "⚠️ Some endpoints failed - check the errors above"
fi
