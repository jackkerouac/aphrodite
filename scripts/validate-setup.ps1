# Validate Development Setup - Quick Test (PowerShell)
# Tests that all development files are present and configured correctly

param(
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Validate Development Setup Script

USAGE:
    .\validate-setup.ps1

DESCRIPTION:
    Validates that all required development files are present and properly
    configured for Aphrodite development environment.

CHECKS:
    - Required files exist
    - Docker Compose syntax is valid
    - Tailwind v4 configuration
    - Directory structure
    - Environment files

EXAMPLE:
    .\validate-setup.ps1
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🔍 Validating Aphrodite development setup..." -ForegroundColor Cyan

# Check required files exist
$requiredFiles = @(
    "CONTRIBUTING.md",
    "Dockerfile.dev",
    "docker-compose.dev.yml",
    "frontend\Dockerfile.dev",
    "docs\development\setup.md",
    "scripts\dev-setup.ps1",
    "scripts\test.ps1",
    "scripts\reset-db.ps1",
    "scripts\build.ps1",
    "scripts\clean.ps1",
    "scripts\validate-setup.ps1"
)

Write-Status "Checking required files..."
$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "✓ $file"
    } else {
        Write-Error "✗ $file (missing)"
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    exit 1
}

# Check docker-compose.dev.yml syntax
Write-Status "Validating docker-compose.dev.yml syntax..."
try {
    docker-compose -f docker-compose.dev.yml config | Out-Null
    Write-Success "✓ docker-compose.dev.yml syntax valid"
} catch {
    Write-Error "✗ docker-compose.dev.yml has syntax errors"
    exit 1
}

# Check frontend package.json for Tailwind v4
Write-Status "Checking Tailwind v4 configuration..."
if (Test-Path "frontend\package.json") {
    $packageJson = Get-Content "frontend\package.json" -Raw
    if ($packageJson -match '"tailwindcss": "\^4"') {
        Write-Success "✓ Tailwind v4 detected in frontend\package.json"
    } else {
        Write-Warning "✗ Tailwind v4 not found - this may cause build issues"
    }
} else {
    Write-Error "✗ frontend\package.json not found"
    exit 1
}

# Check PowerShell script files
Write-Status "Checking PowerShell script files..."
$scriptFiles = @(
    "scripts\dev-setup.ps1",
    "scripts\test.ps1",
    "scripts\reset-db.ps1",
    "scripts\build.ps1",
    "scripts\clean.ps1"
)

foreach ($script in $scriptFiles) {
    if (Test-Path $script) {
        Write-Success "✓ $script exists"
    } else {
        Write-Error "✗ $script missing"
        exit 1
    }
}

# Check environment files
Write-Status "Checking environment configuration..."
if (Test-Path ".env.development") {
    Write-Success "✓ .env.development exists"
} else {
    Write-Error "✗ .env.development missing"
    exit 1
}

# Check key directories
Write-Status "Checking directory structure..."
$requiredDirs = @(
    "api",
    "frontend",
    "shared",
    "aphrodite_logging",
    "aphrodite_helpers",
    "docs\development",
    "scripts"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir -PathType Container) {
        Write-Success "✓ $dir\"
    } else {
        Write-Error "✗ $dir\ (missing directory)"
        exit 1
    }
}

Write-Host ""
Write-Success "🎉 Development setup validation complete!"
Write-Host ""
Write-Status "Next steps:"
Write-Host "   1. Set up development environment: .\scripts\dev-setup.ps1"
Write-Host "   2. Start developing with hot reloading!"
Write-Host ""
Write-Status "Services will be available at:"
Write-Host "   • Frontend:  http://localhost:3000"
Write-Host "   • Backend:   http://localhost:8000"
Write-Host "   • API Docs:  http://localhost:8000/docs"
Write-Host ""
Write-Status "All development files are in place and ready for contributors! 🚀"