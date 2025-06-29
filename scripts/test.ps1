# Aphrodite Test Script (PowerShell)
# Run all tests for the project

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Integration,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Aphrodite Test Script

USAGE:
    .\test.ps1 [OPTIONS]

OPTIONS:
    -Backend      Run only backend tests
    -Frontend     Run only frontend tests  
    -Integration  Run only integration tests
    -Help         Show this help message

DESCRIPTION:
    Runs the complete test suite for Aphrodite including backend, frontend,
    and integration tests. Requires development environment to be running.

EXAMPLES:
    .\test.ps1                # Run all tests
    .\test.ps1 -Backend       # Run only backend tests
    .\test.ps1 -Frontend      # Run only frontend tests
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🧪 Running Aphrodite test suite..." -ForegroundColor Cyan

# Check if development environment is running
$runningServices = docker-compose -f docker-compose.dev.yml ps --services --filter "status=running"
if (-not $runningServices) {
    Write-Status "Starting test environment..."
    docker-compose -f docker-compose.dev.yml up -d
    Start-Sleep -Seconds 15
}

$allTestsPassed = $true

# Backend Tests
if (-not $Frontend -and -not $Integration) {
    Write-Status "Running backend tests..."
    try {
        docker-compose -f docker-compose.dev.yml exec -T api python -m pytest -v
        Write-Success "Backend tests passed"
    } catch {
        Write-Error "Backend tests failed"
        $allTestsPassed = $false
        if ($Backend) { exit 1 }
    }
}

# Frontend Tests  
if (-not $Backend -and -not $Integration) {
    Write-Status "Running frontend tests..."
    try {
        docker-compose -f docker-compose.dev.yml exec -T frontend npm test -- --watchAll=false
        Write-Success "Frontend tests passed"
    } catch {
        Write-Error "Frontend tests failed"
        $allTestsPassed = $false
        if ($Frontend) { exit 1 }
    }
}

# Integration Tests
if (-not $Backend -and -not $Frontend) {
    Write-Status "Running integration tests..."

    # Test API health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/live" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "API health check passed"
    } catch {
        Write-Error "API health check failed"
        $allTestsPassed = $false
        if ($Integration) { exit 1 }
    }

    # Test Frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "Frontend health check passed"
    } catch {
        Write-Error "Frontend health check failed"
        $allTestsPassed = $false
        if ($Integration) { exit 1 }
    }

    # Test Database Connection
    try {
        docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U aphrodite | Out-Null
        Write-Success "Database connection test passed"
    } catch {
        Write-Error "Database connection test failed"
        $allTestsPassed = $false
        if ($Integration) { exit 1 }
    }

    # Test Redis Connection
    try {
        $redisTest = docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping
        if ($redisTest -match "PONG") {
            Write-Success "Redis connection test passed"
        } else {
            throw "Redis ping failed"
        }
    } catch {
        Write-Error "Redis connection test failed"
        $allTestsPassed = $false
        if ($Integration) { exit 1 }
    }
}

Write-Host ""
if ($allTestsPassed) {
    Write-Success "All tests passed! 🎉"
} else {
    Write-Error "Some tests failed! Please check the output above."
    exit 1
}