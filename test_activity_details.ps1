# PowerShell test script for Activity Details endpoint
# Run this in PowerShell with: .\test_activity_details.ps1

Write-Host "🧪 Testing Activity Type Breakdown Enhancement" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Test the debug endpoint first
Write-Host "`n🔍 Checking workflow models..." -ForegroundColor Yellow
try {
    $debugResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/debug/workflow-models" -Method Get
    Write-Host "✅ Debug endpoint accessible" -ForegroundColor Green
    Write-Host "BatchJobModel Available: $($debugResponse.batch_job_model)" -ForegroundColor White
    Write-Host "Table Exists: $($debugResponse.batch_job_table_exists)" -ForegroundColor White
    Write-Host "Job Count: $($debugResponse.batch_job_count)" -ForegroundColor White
    if ($debugResponse.error) {
        Write-Host "Error: $($debugResponse.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Debug endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test the main endpoints
Write-Host "`n📡 Testing main endpoints..." -ForegroundColor Yellow

# Badge Application
Write-Host "`nTesting badge_application endpoint..." -ForegroundColor White
try {
    $badgeResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/activity-details/badge_application?limit=5" -Method Get
    Write-Host "✅ Badge Application endpoint works!" -ForegroundColor Green
    Write-Host "Activity Type: $($badgeResponse.activity_type)" -ForegroundColor White
    Write-Host "Total Count: $($badgeResponse.total_count)" -ForegroundColor White
    Write-Host "Activities Returned: $($badgeResponse.activities.Count)" -ForegroundColor White
    
    if ($badgeResponse.activities.Count -gt 0) {
        $first = $badgeResponse.activities[0]
        Write-Host "`nFirst Activity:" -ForegroundColor Cyan
        Write-Host "  ID: $($first.id)" -ForegroundColor White
        Write-Host "  Name: $($first.name)" -ForegroundColor White
        Write-Host "  Status: $($first.status)" -ForegroundColor White
        Write-Host "  Total Posters: $($first.total_posters)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Badge Application failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "Error Details: $errorBody" -ForegroundColor Red
    }
}

# Poster Replacement
Write-Host "`nTesting poster_replacement endpoint..." -ForegroundColor White
try {
    $posterResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/activity-details/poster_replacement?limit=5" -Method Get
    Write-Host "✅ Poster Replacement endpoint works!" -ForegroundColor Green
    Write-Host "Activity Type: $($posterResponse.activity_type)" -ForegroundColor White
    Write-Host "Total Count: $($posterResponse.total_count)" -ForegroundColor White
    Write-Host "Activities Returned: $($posterResponse.activities.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Poster Replacement failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ PowerShell test completed!" -ForegroundColor Green
Write-Host "`nIf both endpoints work, you can test the frontend by clicking on activity types in the Analytics Overview." -ForegroundColor Yellow
