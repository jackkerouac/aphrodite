# Aphrodite Clean Development Environment Script (PowerShell)
# Removes all development containers, volumes, and build artifacts

param(
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Aphrodite Clean Development Environment Script

USAGE:
    .\clean.ps1 [OPTIONS]

OPTIONS:
    -Force    Skip confirmation prompt
    -Help     Show this help message

DESCRIPTION:
    Removes all development containers, volumes, and build artifacts.
    This is useful for completely resetting your development environment.

WARNING:
    This will remove all containers, volumes, and build artifacts.
    Source code and configuration files will be preserved.

EXAMPLES:
    .\clean.ps1         # Interactive mode with confirmation
    .\clean.ps1 -Force  # Skip confirmation
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🧹 Cleaning Aphrodite development environment..." -ForegroundColor Cyan

# Confirm action unless -Force is used
if (-not $Force) {
    $response = Read-Host "This will remove all containers, volumes, and build artifacts. Continue? (y/N)"
    if ($response -notmatch "^[Yy]$") {
        Write-Status "Clean operation cancelled."
        exit 0
    }
}

# Stop and remove all development services
Write-Status "Stopping development services..."
try {
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>$null
} catch {
    # Ignore errors if no services are running
}

# Remove development volumes
Write-Status "Removing development volumes..."
$volumes = @(
    "aphrodite_postgres_data",
    "aphrodite_redis_data", 
    "aphrodite_aphrodite_data",
    "aphrodite_aphrodite_logs",
    "aphrodite_aphrodite_media",
    "aphrodite_aphrodite_static",
    "aphrodite_frontend_node_modules"
)

foreach ($volume in $volumes) {
    try {
        docker volume rm $volume -f 2>$null
    } catch {
        # Volume might not exist, ignore error
    }
}

# Remove development images
Write-Status "Removing development images..."
$images = @("aphrodite_api", "aphrodite_frontend", "aphrodite_worker")
foreach ($image in $images) {
    try {
        docker image rm $image -f 2>$null
    } catch {
        # Image might not exist, ignore error
    }
}

# Clean frontend build artifacts
Write-Status "Cleaning frontend build artifacts..."
if (Test-Path "frontend\.next") {
    Remove-Item -Recurse -Force "frontend\.next"
    Write-Status "Removed frontend\.next"
}

if (Test-Path "frontend\node_modules") {
    Remove-Item -Recurse -Force "frontend\node_modules"
    Write-Status "Removed frontend\node_modules"
}

# Clean backend artifacts
Write-Status "Cleaning backend artifacts..."
Get-ChildItem -Recurse -Name "__pycache__" -Directory | ForEach-Object {
    Remove-Item -Recurse -Force $_
}
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
Get-ChildItem -Recurse -Name "*.pyo" | Remove-Item -Force

# Clean logs
Write-Status "Cleaning logs..."
if (Test-Path "logs") {
    Get-ChildItem "logs\*" | Remove-Item -Recurse -Force
    Write-Status "Cleared logs directory"
}

if (Test-Path "api\logs") {
    Get-ChildItem "api\logs\*" | Remove-Item -Recurse -Force
    Write-Status "Cleared api\logs directory"
}

# Clean temporary files
Write-Status "Cleaning temporary files..."
if (Test-Path "temp") {
    Get-ChildItem "temp\*" | Remove-Item -Recurse -Force
}
if (Test-Path "tmp") {
    Get-ChildItem "tmp\*" | Remove-Item -Recurse -Force
}

# Clean Docker system (careful - only remove development artifacts)
Write-Status "Cleaning Docker system..."
try {
    docker system prune -f --filter "label=aphrodite-dev" 2>$null
} catch {
    # Ignore if nothing to clean
}

# Clean unused Docker resources
Write-Status "Cleaning unused Docker resources..."
try {
    docker image prune -f 2>$null
    docker volume prune -f 2>$null
} catch {
    # Ignore if nothing to clean
}

# Show remaining Docker resources
Write-Status "Remaining Docker resources:"
Write-Host "Images:"
try {
    docker images --filter "reference=*aphrodite*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
} catch {
    Write-Host "No Aphrodite images found"
}

Write-Host ""
Write-Host "Volumes:"
try {
    docker volume ls --filter "name=aphrodite" --format "table {{.Name}}\t{{.Driver}}"
} catch {
    Write-Host "No Aphrodite volumes found"
}

Write-Host ""
Write-Success "Development environment cleaned! 🧹"
Write-Host ""
Write-Status "To restart development:"
Write-Host "   .\scripts\dev-setup.ps1"
Write-Host ""
Write-Status "Files preserved:"
Write-Host "   • Source code"
Write-Host "   • Configuration files (.env.*)"
Write-Host "   • Documentation"
Write-Host "   • Git history"