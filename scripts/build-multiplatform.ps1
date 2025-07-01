# Aphrodite Multi-Platform Build Script (PowerShell)
# Builds for both AMD64 and ARM64 architectures

param(
    [string]$Version = $null
)

# Color functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🏗️ Building Aphrodite for multiple platforms (AMD64 + ARM64)..." -ForegroundColor Cyan

# Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required for building"
    exit 1
}

try {
    docker buildx version | Out-Null
} catch {
    Write-Error "Docker Buildx is required for multi-platform builds"
    Write-Error "Please install Docker Desktop or enable buildx in your Docker installation"
    exit 1
}

# Get version
if (-not $Version) {
    if (Test-Path "VERSION") {
        $Version = Get-Content "VERSION" -Raw | Trim
    } else {
        $Version = "dev"
    }
}
Write-Status "Building version: $Version"

# Setup buildx builder
Write-Status "Setting up multi-platform builder..."
try {
    docker buildx use aphrodite-multiplatform 2>$null
} catch {
    try {
        docker buildx create --name aphrodite-multiplatform --use 2>$null
    } catch {
        Write-Status "Creating new multi-platform builder..."
        docker buildx create --name aphrodite-multiplatform --driver docker-container --use
    }
}

# Inspect builder capabilities
Write-Status "Builder capabilities:"
docker buildx inspect --bootstrap

# Check if frontend is built
if (-not (Test-Path "frontend\.next")) {
    Write-Error "Frontend not pre-built!"
    Write-Error "Please run './scripts/build.ps1' first to build the frontend"
    exit 1
}

Write-Success "Using pre-built frontend"

# Build for multiple platforms
Write-Status "Building for AMD64 and ARM64 platforms..."
Write-Warning "This may take significantly longer than single-platform builds"

try {
    docker buildx build `
        --label "aphrodite-build" `
        --tag "aphrodite:$Version-multiplatform" `
        --tag "aphrodite:latest-multiplatform" `
        --platform linux/amd64,linux/arm64 `
        --file Dockerfile `
        --load `
        .
    
    Write-Success "Multi-platform build completed successfully!"
} catch {
    Write-Error "Multi-platform build failed"
    Write-Status "Falling back to current platform build..."
    docker buildx build `
        --label "aphrodite-build" `
        --tag "aphrodite:$Version" `
        --tag "aphrodite:latest" `
        --file Dockerfile `
        --load `
        .
    return
}

# Show built images
Write-Status "Built images:"
docker images aphrodite --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

Write-Host ""
Write-Success "Multi-platform build complete! 🎉"
Write-Host ""
Write-Status "Built for platforms: linux/amd64, linux/arm64"
Write-Host "   • aphrodite:$Version-multiplatform"
Write-Host "   • aphrodite:latest-multiplatform"
Write-Host ""
Write-Status "To push to a registry with multi-platform support:"
Write-Host "   docker buildx build --platform linux/amd64,linux/arm64 --push -t your-registry/aphrodite:$Version ."
Write-Host ""
Write-Warning "Note: Multi-platform images require a registry that supports manifests"
Write-Warning "Local Docker daemon can only load one platform at a time"
