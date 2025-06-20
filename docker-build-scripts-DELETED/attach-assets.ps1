# Release Assets Attachment Script (PowerShell)
# Created: 2025-06-20

# Configuration
$REPO_OWNER = "jackkerouac"
$REPO_NAME = "aphrodite"
$VERSION = "v4.0.2"

Write-Host "📎 Attaching Release Assets" -ForegroundColor Green
Write-Host "Version: $VERSION" -ForegroundColor Green
Write-Host ""

# Check if gh CLI is available
try {
    $null = Get-Command gh -ErrorAction Stop
} catch {
    Write-Host "❌ GitHub CLI (gh) is not installed" -ForegroundColor Red
    Write-Host "Please attach assets manually on GitHub" -ForegroundColor Yellow
    exit 1
}

# Check if files exist
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env.example")) {
    Write-Host "❌ .env.example not found" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Attaching the following assets:" -ForegroundColor Yellow
Write-Host "  • docker-compose.yml"
Write-Host "  • .env.example"
Write-Host ""

try {
    # Attach docker-compose.yml
    Write-Host "📎 Attaching docker-compose.yml..." -ForegroundColor Yellow
    gh release upload $VERSION docker-compose.yml `
        --repo "$REPO_OWNER/$REPO_NAME" `
        --clobber

    # Attach .env.example
    Write-Host "📎 Attaching .env.example..." -ForegroundColor Yellow
    gh release upload $VERSION .env.example `
        --repo "$REPO_OWNER/$REPO_NAME" `
        --clobber

    Write-Host ""
    Write-Host "✅ Successfully attached all release assets!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Release URL:" -ForegroundColor Yellow
    Write-Host "https://github.com/$REPO_OWNER/$REPO_NAME/releases/tag/$VERSION"
    Write-Host ""
    Write-Host "📋 Assets attached:" -ForegroundColor Yellow
    Write-Host "  ✅ docker-compose.yml - Ready-to-use deployment configuration"
    Write-Host "  ✅ .env.example - Environment configuration template"
    Write-Host ""
    Write-Host "🎉 Release $VERSION is now complete and ready for users!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to attach assets: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
