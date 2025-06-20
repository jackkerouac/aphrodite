# Docker Registry Authentication Script (PowerShell)
# Created: 2025-06-20

Write-Host "🔐 Docker Registry Authentication" -ForegroundColor Green
Write-Host ""

# Check if tokens are set
if (-not $env:GITHUB_TOKEN) {
    Write-Host "❌ GITHUB_TOKEN environment variable is not set" -ForegroundColor Red
    Write-Host "Please set your GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "`$env:GITHUB_TOKEN = 'your_github_token_here'" -ForegroundColor Yellow
    exit 1
}

if (-not $env:DOCKERHUB_TOKEN) {
    Write-Host "❌ DOCKERHUB_TOKEN environment variable is not set" -ForegroundColor Red
    Write-Host "Please set your Docker Hub Access Token:" -ForegroundColor Yellow
    Write-Host "`$env:DOCKERHUB_TOKEN = 'your_dockerhub_token_here'" -ForegroundColor Yellow
    exit 1
}

# Login to GitHub Container Registry
Write-Host "🔑 Logging into GitHub Container Registry..." -ForegroundColor Yellow
try {
    $env:GITHUB_TOKEN | docker login ghcr.io -u jackkerouac --password-stdin
    Write-Host "✅ Successfully logged into ghcr.io" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to login to ghcr.io" -ForegroundColor Red
    exit 1
}

# Login to Docker Hub
Write-Host "🔑 Logging into Docker Hub..." -ForegroundColor Yellow
try {
    $env:DOCKERHUB_TOKEN | docker login -u jackkerouac --password-stdin
    Write-Host "✅ Successfully logged into Docker Hub" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to login to Docker Hub" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 All registries authenticated successfully!" -ForegroundColor Green
Write-Host "You can now run the build script: .\docker-build-scripts\build-multiplatform.ps1" -ForegroundColor Yellow
