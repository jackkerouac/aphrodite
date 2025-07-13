# Test Performance Metrics Endpoint
# Run this in PowerShell:

Write-Host "Testing Performance Metrics API..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/performance-metrics" -Method Get
    Write-Host "✅ Performance metrics endpoint works!" -ForegroundColor Green
    Write-Host "Total Jobs: $($response.total_jobs_processed)" -ForegroundColor White
    Write-Host "Success Rate: $($response.success_rate_percentage)%" -ForegroundColor White
    Write-Host "Avg Duration: $($response.avg_job_duration_seconds)s" -ForegroundColor White
    Write-Host "Jobs/Hour: $($response.jobs_per_hour_24h)" -ForegroundColor White
} catch {
    Write-Host "❌ Performance metrics failed: $($_.Exception.Message)" -ForegroundColor Red
}
