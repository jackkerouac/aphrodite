#!/bin/bash

# Simple test for emergency fix

echo "🔧 Testing Emergency Fix for Activity Details"
echo "============================================"

echo "Testing simple endpoint..."
curl -s "http://localhost:8000/api/v1/analytics/activity-details/badge_application?limit=3" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    print('✅ Success!')
    print('Activity Type:', data.get('activity_type'))
    print('Total Count:', data.get('total_count'))
    print('Activities Found:', len(data.get('activities', [])))
    
    # Show first activity if available
    activities = data.get('activities', [])
    if activities:
        first = activities[0]
        print('\\nFirst Activity:')
        print('  ID:', first.get('id'))
        print('  Name:', first.get('name'))
        print('  Status:', first.get('status'))
        print('  Posters:', first.get('total_posters'))
except Exception as e:
    print('❌ Error:', e)
    print('Raw response:', sys.stdin.read())
"

echo ""
echo "If this works, rebuild Docker and test the frontend!"
