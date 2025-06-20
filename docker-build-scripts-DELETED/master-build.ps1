# Aphrodite v2 Master Build and Release Script (PowerShell)
# Created: 2025-06-20

# Configuration
$VERSION = "v4.0.2"

Write-Host "🚀 Aphrodite v2 Manual Multi-Platform Docker Build & Release" -ForegroundColor Green -BackgroundColor Black
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "Version: $VERSION" -ForegroundColor Green
Write-Host "Repository: jackkerouac/aphrodite" -ForegroundColor Green
Write-Host "Platforms: linux/amd64, linux/arm64" -ForegroundColor Green
Write-Host "Registries: GitHub Container Registry, Docker Hub" -ForegroundColor Green
Write-Host ""

# Step 1: Pre-flight checks
Write-Host "Step 1: Pre-flight Checks" -ForegroundColor Blue -BackgroundColor Black
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $null = docker --version
} catch {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}

# Check Docker buildx
try {
    $null = docker buildx version
} catch {
    Write-Host "❌ Docker buildx is not available" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Dockerfile not found. Please run this script from the aphrodite repository root." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites met" -ForegroundColor Green
Write-Host ""

# Step 2: Authentication
Write-Host "Step 2: Registry Authentication" -ForegroundColor Blue -BackgroundColor Black
Write-Host "🔐 Please ensure you have set the following environment variables:" -ForegroundColor Yellow
Write-Host "  `$env:GITHUB_TOKEN = 'your_github_personal_access_token'"
Write-Host "  `$env:DOCKERHUB_TOKEN = 'your_dockerhub_access_token'"
Write-Host ""

Read-Host "Press Enter to continue with authentication, or Ctrl+C to cancel"
& ".\docker-build-scripts\authenticate.ps1"

Write-Host ""

# Step 3: Build and Push
Write-Host "Step 3: Multi-Platform Build and Push" -ForegroundColor Blue -BackgroundColor Black
Read-Host "Press Enter to start the build process, or Ctrl+C to cancel"
& ".\docker-build-scripts\build-multiplatform.ps1"

Write-Host ""

# Step 4: Verification
Write-Host "Step 4: Image Verification" -ForegroundColor Blue -BackgroundColor Black
Read-Host "Press Enter to verify the built images, or Ctrl+C to cancel"
& ".\docker-build-scripts\verify-images.ps1"

Write-Host ""

# Success summary
Write-Host "🎉 DOCKER BUILD COMPLETE: Aphrodite $VERSION Multi-Platform Images" -ForegroundColor Green -BackgroundColor Black
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 What was accomplished:" -ForegroundColor Yellow
Write-Host "  ✅ Multi-platform Docker images built (linux/amd64, linux/arm64)"
Write-Host "  ✅ Images pushed to GitHub Container Registry and Docker Hub"
Write-Host "  ✅ Images verified for functionality and accessibility"
Write-Host ""
Write-Host "🐳 Available Images:" -ForegroundColor Yellow
Write-Host "  • ghcr.io/jackkerouac/aphrodite:$VERSION"
Write-Host "  • ghcr.io/jackkerouac/aphrodite:latest"
Write-Host "  • jackkerouac/aphrodite:$VERSION"
Write-Host "  • jackkerouac/aphrodite:latest"
Write-Host ""
Write-Host "🚀 Multi-platform Docker images are ready for use!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps (Optional):" -ForegroundColor Blue
Write-Host "  1. Create GitHub release manually at:"
Write-Host "     https://github.com/jackkerouac/aphrodite/releases/new"
Write-Host "  2. Tag: $VERSION"
Write-Host "  3. Attach docker-compose.yml and .env.example files"
