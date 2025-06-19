# Aphrodite v2 Docker Test Script - PowerShell Version
# Run this in PowerShell to test your Docker setup

param(
    [switch]$Quick,
    [switch]$Logs,
    [switch]$Help
)

if ($Help) {
    Write-Host "Aphrodite v2 Docker Test Script" -ForegroundColor Blue
    Write-Host "Usage: .\test-docker.ps1 [-Quick] [-Logs] [-Help]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Quick    Run quick tests only (skip endpoint tests)"
    Write-Host "  -Logs     Show service logs after tests"
    Write-Host "  -Help     Show this help message"
    exit 0
}

function Write-Status {
    param(
        [string]$Status,
        [string]$Message
    )
    
    switch ($Status) {
        "PASS" { Write-Host "✅ PASS: $Message" -ForegroundColor Green }
        "FAIL" { Write-Host "❌ FAIL: $Message" -ForegroundColor Red }
        "WARN" { Write-Host "⚠️  WARN: $Message" -ForegroundColor Yellow }
        "INFO" { Write-Host "ℹ️  INFO: $Message" -ForegroundColor Blue }
    }
}

function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

function Test-Endpoint {
    param(
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [string]$Description
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Status "PASS" "$Description (HTTP $($response.StatusCode))"
            return $true
        } else {
            Write-Status "FAIL" "$Description (HTTP $($response.StatusCode), expected $ExpectedStatus)"
            return $false
        }
    }
    catch {
        Write-Status "FAIL" "$Description (Connection failed)"
        return $false
    }
}

function Test-ServiceRunning {
    param([string]$ServiceName)
    
    try {
        $result = docker-compose ps $ServiceName 2>$null
        if ($result -match "Up") {
            Write-Status "PASS" "$ServiceName is running"
            return $true
        } else {
            Write-Status "FAIL" "$ServiceName is not running"
            return $false
        }
    }
    catch {
        Write-Status "FAIL" "$ServiceName status check failed"
        return $false
    }
}

# Main test function
$FailedTests = 0

Write-Host ""
Write-Host "🐋 Aphrodite v2 Docker Test Script" -ForegroundColor Blue
Write-Host "==================================="
Write-Host ""

Write-Status "INFO" "Starting Docker service tests..."
Write-Host ""

# Test 1: Check if docker-compose.yml exists
if (Test-Path "docker-compose.yml") {
    Write-Status "PASS" "docker-compose.yml found"
} else {
    Write-Status "FAIL" "docker-compose.yml not found"
    $FailedTests++
}

# Test 2: Check if .env file exists
if (Test-Path ".env") {
    Write-Status "PASS" ".env configuration file found"
} else {
    Write-Status "WARN" ".env file not found, using defaults"
}

# Test 3: Check if Docker is running
try {
    $dockerInfo = docker info 2>$null
    if ($dockerInfo) {
        Write-Status "PASS" "Docker daemon is running"
    } else {
        Write-Status "FAIL" "Docker daemon is not running"
        $FailedTests++
        exit $FailedTests
    }
}
catch {
    Write-Status "FAIL" "Docker daemon is not running"
    $FailedTests++
    exit $FailedTests
}

# Test 4: Check if Docker Compose is available
if (Test-Command "docker-compose") {
    Write-Status "PASS" "Docker Compose is available"
} else {
    Write-Status "FAIL" "Docker Compose is not available"
    $FailedTests++
    exit $FailedTests
}

Write-Host ""
Write-Status "INFO" "Checking service status..."

# Test 5-8: Check if services are running
if (!(Test-ServiceRunning "aphrodite-postgres")) { $FailedTests++ }
if (!(Test-ServiceRunning "aphrodite-redis")) { $FailedTests++ }
if (!(Test-ServiceRunning "aphrodite-app")) { $FailedTests++ }
if (!(Test-ServiceRunning "aphrodite-worker")) { $FailedTests++ }

Write-Host ""
Write-Status "INFO" "Testing service connectivity..."

# Test 9: PostgreSQL health check
try {
    $pgResult = docker-compose exec -T postgresql pg_isready -U aphrodite -d aphrodite_v2 2>$null
    if ($pgResult -match "accepting connections") {
        Write-Status "PASS" "PostgreSQL is ready and accepting connections"
    } else {
        Write-Status "FAIL" "PostgreSQL health check failed"
        $FailedTests++
    }
}
catch {
    Write-Status "FAIL" "PostgreSQL health check failed"
    $FailedTests++
}

# Test 10: Redis health check
try {
    $redisResult = docker-compose exec -T redis redis-cli ping 2>$null
    if ($redisResult -match "PONG") {
        Write-Status "PASS" "Redis is responding to ping"
    } else {
        Write-Status "FAIL" "Redis health check failed"
        $FailedTests++
    }
}
catch {
    Write-Status "FAIL" "Redis health check failed"
    $FailedTests++
}

if (!$Quick) {
    # Wait a moment for services to be fully ready
    Start-Sleep -Seconds 5
    
    Write-Host ""
    Write-Status "INFO" "Testing HTTP endpoints..."
    
    # Test 11: API health endpoint
    if (!(Test-Endpoint "http://localhost:8000/health/live" 200 "API health endpoint")) {
        $FailedTests++
    }
    
    # Test 12: API root endpoint
    if (!(Test-Endpoint "http://localhost:8000/" 200 "API root endpoint")) {
        $FailedTests++
    }
    
    # Test 13: API docs endpoint (optional)
    Test-Endpoint "http://localhost:8000/docs" 200 "API documentation endpoint" | Out-Null
}

Write-Host ""
Write-Status "INFO" "Testing database setup..."

# Test 14: Check database tables exist
try {
    $tableCount = docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>$null
    $tableCount = $tableCount.Trim()
    if ([int]$tableCount -ge 8) {
        Write-Status "PASS" "Database tables are accessible ($tableCount tables)"
    } else {
        Write-Status "FAIL" "Database tables check failed (only $tableCount tables)"
        $FailedTests++
    }
}
catch {
    Write-Status "FAIL" "Database tables check failed"
    $FailedTests++
}

# Test 15: Check default configuration exists
try {
    $configCount = docker-compose exec -T postgresql psql -U aphrodite -d aphrodite_v2 -t -c "SELECT COUNT(*) FROM system_config;" 2>$null
    $configCount = $configCount.Trim()
    if ([int]$configCount -ge 4) {
        Write-Status "PASS" "Default configuration data is present ($configCount configs)"
    } else {
        Write-Status "FAIL" "Default configuration check failed (only $configCount configs)"
        $FailedTests++
    }
}
catch {
    Write-Status "FAIL" "Default configuration check failed"
    $FailedTests++
}

Write-Host ""
Write-Status "INFO" "Testing volume mounts..."

# Test 16-17: Check essential volume directories exist
$volumes = @("posters", "images")
foreach ($vol in $volumes) {
    if (Test-Path $vol) {
        Write-Status "PASS" "$vol directory exists"
    } else {
        Write-Status "WARN" "$vol directory not found (will be created)"
    }
}

Write-Host ""
Write-Status "INFO" "Testing permissions..."

# Test 18: Check if we can write to mounted volumes
try {
    docker-compose exec -T aphrodite touch /app/media/test.log 2>$null
    docker-compose exec -T aphrodite rm -f /app/media/test.log 2>$null
    Write-Status "PASS" "Volume permissions are correct"
}
catch {
    Write-Status "FAIL" "Volume permissions issue detected"
    $FailedTests++
}

# Summary
Write-Host ""
Write-Host "=========================" -ForegroundColor Blue
Write-Host "📊 Test Summary" -ForegroundColor Blue
Write-Host "=========================" -ForegroundColor Blue

if ($FailedTests -eq 0) {
    Write-Status "PASS" "All tests completed successfully! 🎉"
    Write-Host ""
    Write-Host "🚀 Aphrodite v2 is ready to use!" -ForegroundColor Green
    Write-Host "   • Web Interface: http://localhost:8000" -ForegroundColor White
    Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Status "FAIL" "$FailedTests test(s) failed"
    Write-Host ""
    Write-Host "🔧 Please check the failed tests above and:" -ForegroundColor Yellow
    Write-Host "   • Verify your .env configuration" -ForegroundColor White
    Write-Host "   • Check service logs with: docker-compose logs" -ForegroundColor White
    Write-Host "   • Ensure all required ports are available" -ForegroundColor White
    Write-Host "   • Try restarting services: docker-compose restart" -ForegroundColor White
}

# Show logs if requested
if ($Logs) {
    Write-Host ""
    Write-Status "INFO" "Showing recent service logs..."
    Write-Host ""
    
    Write-Host "=== Aphrodite App Logs ===" -ForegroundColor Yellow
    docker-compose logs --tail=20 aphrodite
    
    Write-Host ""
    Write-Host "=== Worker Logs ===" -ForegroundColor Yellow
    docker-compose logs --tail=10 aphrodite-worker
    
    Write-Host ""
    Write-Host "=== PostgreSQL Logs ===" -ForegroundColor Yellow
    docker-compose logs --tail=10 postgresql
    
    Write-Host ""
    Write-Host "=== Redis Logs ===" -ForegroundColor Yellow
    docker-compose logs --tail=10 redis
}

exit $FailedTests
