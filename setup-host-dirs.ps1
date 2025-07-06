# Host Directory Setup Script for Aphrodite (PowerShell)
# This script creates the necessary directory structure when using host mounts

Write-Host "🚀 Setting up Aphrodite host directories..." -ForegroundColor Green

# Base directory - CHANGE THIS TO YOUR DESIRED PATH
$BaseDir = "C:\docker\aphrodite-testing"

# Create all necessary directories
$directories = @(
    "$BaseDir\data",
    "$BaseDir\data\cache",
    "$BaseDir\data\config",
    "$BaseDir\logs",
    "$BaseDir\media",
    "$BaseDir\media\temp",
    "$BaseDir\media\preview",
    "$BaseDir\media\processed",
    "$BaseDir\static"
)

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    try {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to create: $dir" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Directory setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Directory structure:" -ForegroundColor Cyan
Write-Host "├── $BaseDir\"
Write-Host "│   ├── data\            # Application data"
Write-Host "│   │   ├── cache\       # Cache files"
Write-Host "│   │   └── config\      # Configuration files"
Write-Host "│   ├── logs\            # Application logs"
Write-Host "│   ├── media\           # Media files"
Write-Host "│   │   ├── temp\        # Temporary files"
Write-Host "│   │   ├── preview\     # Preview images"
Write-Host "│   │   └── processed\   # Processed posters"
Write-Host "│   └── static\          # Original static files"
Write-Host ""
Write-Host "🐳 You can now run:" -ForegroundColor Yellow
Write-Host "   docker-compose down"
Write-Host "   docker-compose up -d"
Write-Host ""
Write-Host "🌐 The preview files should now be accessible at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/api/v1/static/preview/"
