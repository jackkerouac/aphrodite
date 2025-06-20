# Setup script for Aphrodite Docker build scripts (PowerShell)
# Created: 2025-06-20

Write-Host "🔧 Setting up Aphrodite Docker Build Scripts" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed" -ForegroundColor Green
    Write-Host "   $dockerVersion" -ForegroundColor Gray
} catch {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop" -ForegroundColor Yellow
}

# Check Docker buildx
try {
    $buildxVersion = docker buildx version
    Write-Host "✅ Docker buildx is available" -ForegroundColor Green
    Write-Host "   $buildxVersion" -ForegroundColor Gray
} catch {
    Write-Host "❌ Docker buildx is not available" -ForegroundColor Red
    Write-Host "   Please update Docker to a version with buildx support" -ForegroundColor Yellow
}

# Check GitHub CLI
try {
    $ghVersion = (gh --version | Select-Object -First 1)
    Write-Host "✅ GitHub CLI is installed" -ForegroundColor Green
    Write-Host "   $ghVersion" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  GitHub CLI is not installed" -ForegroundColor Yellow
    Write-Host "   Install from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "   (Required for automated release creation)" -ForegroundColor Yellow
}

Write-Host ""

# Environment variables check
Write-Host "🔑 Environment Variables" -ForegroundColor Yellow
Write-Host "Set these before running the build:" -ForegroundColor Blue
Write-Host ""
Write-Host "`$env:GITHUB_TOKEN = 'your_github_personal_access_token'" -ForegroundColor Yellow
Write-Host "`$env:DOCKERHUB_TOKEN = 'your_dockerhub_access_token'" -ForegroundColor Yellow
Write-Host ""

if ($env:GITHUB_TOKEN) {
    Write-Host "✅ GITHUB_TOKEN is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  GITHUB_TOKEN is not set" -ForegroundColor Yellow
}

if ($env:DOCKERHUB_TOKEN) {
    Write-Host "✅ DOCKERHUB_TOKEN is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  DOCKERHUB_TOKEN is not set" -ForegroundColor Yellow
}

Write-Host ""

# Next steps
Write-Host "🚀 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Blue
Write-Host "1. Set environment variables (if not already set)"
Write-Host "2. Run the complete build process:"
Write-Host "   .\docker-build-scripts\master-build.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or run individual scripts as needed:"
Write-Host "   .\docker-build-scripts\authenticate.ps1" -ForegroundColor Yellow
Write-Host "   .\docker-build-scripts\build-multiplatform.ps1" -ForegroundColor Yellow
Write-Host "   .\docker-build-scripts\verify-images.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Blue
Write-Host "   Get-Content docker-build-scripts\README.md" -ForegroundColor Yellow
