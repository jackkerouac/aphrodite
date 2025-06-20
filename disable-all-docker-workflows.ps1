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

# Disable all Docker-related workflows
$workflowFiles = @(
    "docker-build.yml",
    "docker-publish.yml",
    "build.yml",
    "ci.yml"
)

foreach ($file in $workflowFiles) {
    $filePath = ".github/workflows/$file"
    if (Test-Path $filePath) {
        Write-Host "🔄 Disabling $file..." -ForegroundColor Yellow
        Move-Item $filePath "$filePath.disabled"
        Write-Host "✅ Moved $file to $file.disabled" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  $file not found or already disabled" -ForegroundColor Blue
    }
}

# Create a README explaining the change
$readmeContent = @"
# GitHub Actions Workflows - DISABLED

## 🚫 All Docker Build Workflows Disabled

All Docker-related workflows have been disabled to start fresh with a new Docker build infrastructure.

## 📅 Disabled Date

$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") - Cleaned slate for new Docker build implementation.

## 🔄 Re-enabling Workflows

To re-enable these workflows in the future:
1. Remove the ``.disabled`` extension from the files
2. Commit the changes
3. The workflows will run on the next trigger

## 🏗️ Next Steps

A new Docker build infrastructure will be implemented from scratch.
"@

Write-Host "📝 Creating documentation..." -ForegroundColor Yellow
$readmeContent | Out-File -FilePath ".github/workflows/README-DISABLED.md" -Encoding UTF8

Write-Host ""
Write-Host "✅ GitHub Actions Docker workflows have been disabled!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Yellow
Write-Host "  • All Docker workflow files moved to .disabled"
Write-Host "  • Created README-DISABLED.md with explanation"
Write-Host ""
Write-Host "🔍 Next Steps:" -ForegroundColor Blue
Write-Host "  1. Commit these changes to your repository"
Write-Host "  2. Start fresh with new Docker infrastructure"
Write-Host ""
