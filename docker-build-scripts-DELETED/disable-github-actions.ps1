# Disable GitHub Actions Docker Workflows Script (PowerShell)
# Created: 2025-06-20

Write-Host "🔧 Disabling GitHub Actions Docker Workflows" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path ".github/workflows")) {
    Write-Host "❌ .github/workflows directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the repository root directory" -ForegroundColor Yellow
    exit 1
}

# Disable docker-build.yml
if (Test-Path ".github/workflows/docker-build.yml") {
    Write-Host "🔄 Disabling docker-build.yml..." -ForegroundColor Yellow
    Move-Item ".github/workflows/docker-build.yml" ".github/workflows/docker-build.yml.disabled"
    Write-Host "✅ Moved docker-build.yml to docker-build.yml.disabled" -ForegroundColor Green
} else {
    Write-Host "ℹ️  docker-build.yml not found or already disabled" -ForegroundColor Blue
}

# Disable docker-publish.yml
if (Test-Path ".github/workflows/docker-publish.yml") {
    Write-Host "🔄 Disabling docker-publish.yml..." -ForegroundColor Yellow
    Move-Item ".github/workflows/docker-publish.yml" ".github/workflows/docker-publish.yml.disabled"
    Write-Host "✅ Moved docker-publish.yml to docker-publish.yml.disabled" -ForegroundColor Green
} else {
    Write-Host "ℹ️  docker-publish.yml not found or already disabled" -ForegroundColor Blue
}

# Create a README explaining the change
$readmeContent = @"
# GitHub Actions Workflows - DISABLED

## 🚫 Docker Build Workflows Disabled

The following workflows have been disabled in favor of manual multi-platform Docker builds:

- ``docker-build.yml.disabled`` (was: docker-build.yml)
- ``docker-publish.yml.disabled`` (was: docker-publish.yml)

## ❓ Why Disabled?

GitHub Actions Docker builds were experiencing persistent layer caching issues causing failed builds. The manual build process using the scripts in ``docker-build-scripts/`` directory works reliably and produces the same multi-platform images.

## 🔄 Manual Build Process

Use the PowerShell scripts in the ``docker-build-scripts/`` directory:

``````powershell
# Complete build process
.\docker-build-scripts\master-build.ps1

# Or individual steps
.\docker-build-scripts\authenticate.ps1
.\docker-build-scripts\build-multiplatform.ps1
.\docker-build-scripts\verify-images.ps1
``````

## 🔙 Re-enabling Workflows

To re-enable these workflows in the future:

1. Remove the ``.disabled`` extension from the files
2. Commit the changes
3. The workflows will run on the next release or manual trigger

## 📅 Disabled Date

$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") - Switched to manual build process due to GitHub Actions Docker layer caching issues.
"@

Write-Host "📝 Creating documentation..." -ForegroundColor Yellow
$readmeContent | Out-File -FilePath ".github/workflows/README.md" -Encoding UTF8

Write-Host ""
Write-Host "✅ GitHub Actions Docker workflows have been disabled!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Yellow
Write-Host "  • docker-build.yml → docker-build.yml.disabled"
Write-Host "  • docker-publish.yml → docker-publish.yml.disabled"
Write-Host "  • Created .github/workflows/README.md with explanation"
Write-Host ""
Write-Host "🔍 Next Steps:" -ForegroundColor Blue
Write-Host "  1. Commit these changes to your repository"
Write-Host "  2. Use manual build scripts for Docker releases"
Write-Host "  3. No more failed GitHub Actions Docker builds!"
Write-Host ""
Write-Host "💡 Note: GitHub Actions workflows are now disabled for releases." -ForegroundColor Cyan
Write-Host "Use the manual build scripts in docker-build-scripts/ instead." -ForegroundColor Cyan
