# GitHub Release Creation Script (PowerShell)
# Created: 2025-06-20

# Configuration
$REPO_OWNER = "jackkerouac"
$REPO_NAME = "aphrodite"
$VERSION = "v4.0.2"

Write-Host "📦 Creating GitHub Release" -ForegroundColor Green
Write-Host "Version: $VERSION" -ForegroundColor Green
Write-Host ""

# Check if gh CLI is available
try {
    $null = Get-Command gh -ErrorAction Stop
} catch {
    Write-Host "❌ GitHub CLI (gh) is not installed" -ForegroundColor Red
    Write-Host "Please install GitHub CLI: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "Alternative: Create the release manually on GitHub" -ForegroundColor Yellow
    exit 1
}

# Check if user is authenticated
try {
    $null = gh auth status 2>$null
} catch {
    Write-Host "❌ Not authenticated with GitHub CLI" -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Create release notes
$RELEASE_NOTES = @"
## 🚀 Aphrodite $VERSION - Multi-Platform Docker Release

### ✨ What's New
- **Multi-platform Docker images** now available for both AMD64 and ARM64 architectures
- **Fixed Docker build process** with proper ARM64 compilation support
- **Enhanced psutil compatibility** for ARM-based systems
- **Container registry support** for both GitHub Container Registry and Docker Hub

### 🐳 Docker Images
**GitHub Container Registry:**
``````bash
docker pull ghcr.io/$REPO_OWNER/$REPO_NAME`:$VERSION
docker pull ghcr.io/$REPO_OWNER/$REPO_NAME`:latest
``````

**Docker Hub:**
``````bash
docker pull $REPO_OWNER/aphrodite`:$VERSION
docker pull $REPO_OWNER/aphrodite`:latest
``````

### 🏗️ Supported Platforms
- **linux/amd64** - Standard x86_64 systems
- **linux/arm64** - ARM-based systems (Apple Silicon, Raspberry Pi 4+, etc.)

### 📋 Installation
1. Download the ``docker-compose.yml`` and ``.env.example`` files from this release
2. Copy ``.env.example`` to ``.env`` and configure your settings
3. Run: ``docker-compose up -d``

### 🔧 What's Fixed
- ARM64 compilation issues with psutil resolved
- Added missing build dependencies (python3-dev, build-essential)
- Multi-platform Docker build now works reliably
- Manual build process replaces problematic GitHub Actions

### 📚 Documentation
See the attached ``docker-compose.yml`` for easy deployment setup.

---
**Full Changelog**: https://github.com/$REPO_OWNER/$REPO_NAME/compare/v4.0.1...$VERSION
"@

Write-Host "📝 Creating release with the following details:" -ForegroundColor Yellow
Write-Host "Repository: $REPO_OWNER/$REPO_NAME"
Write-Host "Tag: $VERSION"
Write-Host "Title: Aphrodite $VERSION - Multi-Platform Docker Release"
Write-Host ""

# Create the release
Write-Host "🚀 Creating GitHub release..." -ForegroundColor Yellow

try {
    gh release create $VERSION `
        --repo "$REPO_OWNER/$REPO_NAME" `
        --title "Aphrodite $VERSION - Multi-Platform Docker Release" `
        --notes $RELEASE_NOTES `
        --latest

    Write-Host "✅ Successfully created GitHub release $VERSION" -ForegroundColor Green
    Write-Host ""
    Write-Host "📎 Next: Attach release assets" -ForegroundColor Yellow
    Write-Host "Run: .\docker-build-scripts\attach-assets.ps1"
} catch {
    Write-Host "❌ Failed to create GitHub release: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
