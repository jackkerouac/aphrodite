# Build script for Aphrodite frontend - PowerShell version
# Ensures frontend uses correct environment for production deployment

param(
    [switch]$Verbose
)

function Write-Status {
    param($Message, $Color = "Green")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Error-Status {
    param($Message)
    Write-Host $Message -ForegroundColor Red
}

function Write-Warning-Status {
    param($Message)
    Write-Host $Message -ForegroundColor Yellow
}

Write-Status "🔧 Building Aphrodite frontend for production deployment..."
Write-Status ("=" * 60)

# Get script directory and frontend path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $ScriptDir "frontend"

if (-not (Test-Path $FrontendDir)) {
    Write-Error-Status "❌ Error: Frontend directory not found at $FrontendDir"
    exit 1
}

Write-Status "📁 Working in: $FrontendDir"
Set-Location $FrontendDir

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Error-Status "❌ Error: package.json not found in frontend directory"
    exit 1
}

Write-Status "`n📦 Installing dependencies..."
try {
    & npm ci
    if ($LASTEXITCODE -ne 0) {
        Write-Warning-Status "⚠️ npm ci failed, trying npm install..."
        & npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Status "❌ Failed to install dependencies"
            exit 1
        }
    }
    Write-Status "✅ Dependencies installed successfully"
} catch {
    Write-Error-Status "❌ Error installing dependencies: $_"
    exit 1
}

Write-Status "`n🧹 Cleaning previous build..."
$NextDir = Join-Path $FrontendDir ".next"
if (Test-Path $NextDir) {
    try {
        Remove-Item $NextDir -Recurse -Force
        Write-Status "✅ Removed .next directory"
    } catch {
        Write-Warning-Status "⚠️ Could not remove .next directory: $_"
    }
}

Write-Status "`n🏗️ Building frontend with production environment..."

# Set environment variables for the build
$env:NODE_ENV = "production"

try {
    & npm run build:docker
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Status "❌ Build failed"
        exit 1
    }
    Write-Status "✅ Build completed successfully!"
} catch {
    Write-Error-Status "❌ Build failed: $_"
    exit 1
}

Write-Status "`n📋 Verifying build..."

# Check if .next directory was created
if (-not (Test-Path $NextDir)) {
    Write-Error-Status "❌ Error: .next directory not found after build"
    exit 1
}

# Check if static directory exists
$StaticDir = Join-Path $NextDir "static"
if (-not (Test-Path $StaticDir)) {
    Write-Error-Status "❌ Error: .next/static directory not found"
    exit 1
}

Write-Status "✅ Frontend build completed successfully!"
Write-Status "🚀 Ready for Docker deployment"

# Show build info
Write-Status "`n📊 Build info:"
try {
    # Count files in static directory
    $StaticFiles = Get-ChildItem -Path $StaticDir -Recurse -File
    $FileCount = $StaticFiles.Count
    Write-Status "   Static files: $FileCount files"
    
    # Get build size
    $BuildSize = (Get-ChildItem -Path $NextDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $BuildSizeMB = [math]::Round($BuildSize / 1MB, 1)
    Write-Status "   Build size: $BuildSizeMB MB"
} catch {
    Write-Warning-Status "   Could not calculate build stats: $_"
}

Write-Status "`n🔗 API URL configuration:"
Write-Status "   Development: http://localhost:8000"
Write-Status "   Production: Dynamic (uses window.location.origin)"

Write-Status "`n✅ The frontend will now work correctly on remote machines!"
Write-Status "`n🚀 Next steps:"
Write-Status "   1. Commit and push changes to GitHub"
Write-Status "   2. GitHub will build the Docker image"
Write-Status "   3. Deploy to remote machine (192.168.0.110)"
Write-Status "   4. Test that Dashboard shows 'Online' status"

# Return to original directory
Set-Location $ScriptDir
