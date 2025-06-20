# Aphrodite v2 Docker Build - Manual Multi-Platform Build Script (PowerShell)
# Created: 2025-06-20

# Configuration
$REPO_OWNER = "jackkerouac"
$REPO_NAME = "aphrodite"
$VERSION = "v4.0.2"  # Next version after v4.0.1
$DOCKER_HUB_USER = "jackkerouac"

# Image tags
$GHCR_IMAGE = "ghcr.io/$REPO_OWNER/$REPO_NAME"
$DOCKER_HUB_IMAGE = "$DOCKER_HUB_USER/aphrodite"

Write-Host "🚀 Aphrodite Multi-Platform Docker Build" -ForegroundColor Green
Write-Host "Repository: $REPO_OWNER/$REPO_NAME" -ForegroundColor Green
Write-Host "Version: $VERSION" -ForegroundColor Green
Write-Host ""

# Step 1: Setup buildx
Write-Host "📦 Setting up Docker buildx..." -ForegroundColor Yellow
try {
    docker buildx create --name aphrodite-builder --use --bootstrap 2>$null
} catch {
    Write-Host "Using existing aphrodite-builder" -ForegroundColor Yellow
    docker buildx use aphrodite-builder
}

# Step 2: Build and push multi-platform images
Write-Host "🔨 Building and pushing multi-platform images..." -ForegroundColor Yellow
Write-Host "Platforms: linux/amd64, linux/arm64" -ForegroundColor Green
Write-Host "Registries: GitHub Container Registry, Docker Hub" -ForegroundColor Green
Write-Host ""

try {
    docker buildx build `
        --platform linux/amd64,linux/arm64 `
        -t "${GHCR_IMAGE}:${VERSION}" `
        -t "${GHCR_IMAGE}:latest" `
        -t "${DOCKER_HUB_IMAGE}:${VERSION}" `
        -t "${DOCKER_HUB_IMAGE}:latest" `
        --push `
        .

    Write-Host ""
    Write-Host "✅ Multi-platform build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Built images:" -ForegroundColor Yellow
    Write-Host "  ${GHCR_IMAGE}:${VERSION}"
    Write-Host "  ${GHCR_IMAGE}:latest"
    Write-Host "  ${DOCKER_HUB_IMAGE}:${VERSION}"
    Write-Host "  ${DOCKER_HUB_IMAGE}:latest"
    Write-Host ""
    Write-Host "🔍 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run verification script: .\docker-build-scripts\verify-images.ps1"
    Write-Host "  2. Create GitHub release: .\docker-build-scripts\create-release.ps1"
    Write-Host "  3. Test installation: .\docker-build-scripts\test-installation.ps1"
} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
