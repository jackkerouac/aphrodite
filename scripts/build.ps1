# Aphrodite Production Build Script (PowerShell)
# Builds the complete application for production deployment

param(
    [switch]$NativeNode,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Aphrodite Production Build Script

USAGE:
    .\build.ps1 [OPTIONS]

OPTIONS:
    -NativeNode   Use local Node.js instead of Docker for frontend build
    -Help         Show this help message

DESCRIPTION:
    Builds the complete application for production deployment.
    IMPORTANT: Builds frontend with Tailwind v4 for GitHub Actions compatibility.

REQUIREMENTS:
    - Docker and Docker Compose
    - Node.js 18+ (optional, for -NativeNode)

EXAMPLES:
    .\build.ps1                # Use Docker for frontend build
    .\build.ps1 -NativeNode    # Use local Node.js for frontend build
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🏗️ Building Aphrodite for production..." -ForegroundColor Cyan

# Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required for building"
    exit 1
}

$useDockerBuild = $true
if ($NativeNode) {
    if (Get-Command node -ErrorAction SilentlyContinue) {
        $useDockerBuild = $false
        Write-Status "Using local Node.js for frontend build"
    } else {
        Write-Warning "Node.js not found - falling back to Docker build"
    }
} else {
    Write-Status "Using Docker for frontend build"
}

# Get version
$version = "dev"
if (Test-Path "VERSION") {
    $version = Get-Content "VERSION" -Raw | Trim
}
Write-Status "Building version: $version"

# Clean previous builds
Write-Status "Cleaning previous builds..."
try {
    docker system prune -f --filter "label=aphrodite-build" 2>$null
} catch {
    # Ignore if no builds to clean
}

# Build frontend (REQUIRED for Tailwind v4)
Write-Status "Building frontend with Tailwind v4..."

if ($useDockerBuild) {
    Write-Status "Using Docker to build frontend..."
    
    # Create temporary build container
    $frontendPath = Join-Path $PWD "frontend"
    docker run --rm `
        -v "${frontendPath}:/app" `
        -w /app `
        node:18-alpine `
        sh -c "npm ci && npm run build"
} else {
    Write-Status "Building frontend natively..."
    Push-Location frontend
    
    try {
        # Install dependencies
        npm ci
        
        # Build with Tailwind v4
        npm run build
        
        Write-Success "Frontend build completed"
    } catch {
        Write-Error "Frontend build failed"
        Pop-Location
        exit 1
    } finally {
        Pop-Location
    }
}

# Verify frontend build
if (-not (Test-Path "frontend\.next")) {
    Write-Error "Frontend build failed - .next directory not found"
    Write-Error "This is required for Tailwind v4 and production deployment"
    exit 1
}

Write-Success "Frontend build completed with Tailwind v4"

# Build production Docker image
Write-Status "Building production Docker image..."

try {
    docker build `
        --label "aphrodite-build" `
        --tag "aphrodite:$version" `
        --tag "aphrodite:latest" `
        --file Dockerfile `
        .
    
    Write-Success "Production image built successfully"
} catch {
    Write-Error "Docker build failed"
    exit 1
}

# Test the built image
Write-Status "Testing built image..."

# Generate random container name
$testContainer = "aphrodite-test-$(Get-Random)"

try {
    # Start test container
    docker run -d `
        --name $testContainer `
        --env DATABASE_URL="sqlite:///test.db" `
        --env ENVIRONMENT="test" `
        --publish 18000:8000 `
        "aphrodite:$version" | Out-Null

    # Wait for container to start
    Start-Sleep -Seconds 10

    # Test health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:18000/health/live" -TimeoutSec 10 -ErrorAction Stop
        Write-Success "Production image health check passed"
    } catch {
        Write-Error "Production image health check failed"
        docker logs $testContainer
        throw
    }
} catch {
    Write-Error "Production image test failed"
    exit 1
} finally {
    # Clean up test container
    try {
        docker rm -f $testContainer 2>$null
    } catch {
        # Ignore cleanup errors
    }
}

# Show image info
Write-Status "Built image details:"
docker images aphrodite:$version --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

Write-Host ""
Write-Success "Production build complete! 🎉"
Write-Host ""
Write-Status "Built images:"
Write-Host "   • aphrodite:$version"
Write-Host "   • aphrodite:latest"
Write-Host ""
Write-Status "Next steps:"
Write-Host "   • Test locally: docker run -p 8000:8000 aphrodite:$version"
Write-Host "   • Push to registry: docker push aphrodite:$version"
Write-Host "   • Deploy with: docker-compose up -d"
Write-Host ""
Write-Warning "Remember: Frontend was built with Tailwind v4 for GitHub Actions compatibility"