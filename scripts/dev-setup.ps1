# Aphrodite Development Setup Script (PowerShell)
# Automated setup for new contributors

param(
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Aphrodite Development Setup Script

USAGE:
    .\dev-setup.ps1 [OPTIONS]

OPTIONS:
    -Force    Skip confirmation prompts
    -Help     Show this help message

DESCRIPTION:
    Sets up a complete development environment for Aphrodite with hot reloading.
    Requires Docker Desktop to be installed and running.

EXAMPLE:
    .\dev-setup.ps1
    .\dev-setup.ps1 -Force
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🚀 Setting up Aphrodite development environment..." -ForegroundColor Cyan

# Check prerequisites
Write-Status "Checking prerequisites..."

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed. Please install Docker Desktop."
    exit 1
}

# Check Docker Compose
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Compose is not installed. Please install Docker Desktop."
    exit 1
}

# Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed. Please install Git."
    exit 1
}

Write-Success "All prerequisites found!"

# Create .env.development if it doesn't exist
if (-not (Test-Path ".env.development")) {
    Write-Status "Creating .env.development..."
    Copy-Item ".env.development" ".env.development" -ErrorAction SilentlyContinue
    Write-Success ".env.development created"
} else {
    Write-Status ".env.development already exists"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
$directories = @(
    "logs", "data", "media", "api/static/originals", 
    "api/static/preview", "api/static/processed",
    "api/static/awards/black", "api/static/awards/white"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Success "Directories created"

# Check if Docker daemon is running
try {
    docker info | Out-Null
} catch {
    Write-Error "Docker daemon is not running. Please start Docker Desktop."
    exit 1
}

# Stop any existing containers
Write-Status "Stopping any existing containers..."
try {
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>$null
} catch {
    # Ignore errors if no containers are running
}

# Pull base images
Write-Status "Pulling base Docker images..."
$images = @("python:3.11-slim", "node:18-alpine", "postgres:15-alpine", "redis:7-alpine")
foreach ($image in $images) {
    Write-Status "Pulling $image..."
    docker pull $image
}

# Build development images
Write-Status "Building development images..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Start database services first
Write-Status "Starting database services..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for database to be ready
Write-Status "Waiting for database to be ready..."
Start-Sleep -Seconds 10

# Check database health
$retries = 0
$maxRetries = 6
do {
    try {
        docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite | Out-Null
        break
    } catch {
        $retries++
        if ($retries -ge $maxRetries) {
            Write-Warning "Database taking longer than expected to start"
            break
        }
        Write-Status "Database not ready yet, waiting... ($retries/$maxRetries)"
        Start-Sleep -Seconds 5
    }
} while ($retries -lt $maxRetries)

# Initialize database
Write-Status "Initializing database..."
docker-compose -f docker-compose.dev.yml up -d api
Start-Sleep -Seconds 5

# Run database initialization if needed
try {
    docker-compose -f docker-compose.dev.yml exec api python database_defaults_init.py
} catch {
    Write-Warning "Database initialization may have failed - this is normal on first run"
}

# Start all services
Write-Status "Starting all development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
Write-Status "Waiting for services to start..."
Start-Sleep -Seconds 15

# Check service health
Write-Status "Checking service health..."

# Check API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health/live" -TimeoutSec 5 -ErrorAction Stop
    Write-Success "Backend API is running"
} catch {
    Write-Warning "Backend API may still be starting up"
}

# Check Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Success "Frontend is running"
} catch {
    Write-Warning "Frontend may still be starting up"
}

# Show service status
Write-Status "Service status:"
docker-compose -f docker-compose.dev.yml ps

Write-Host ""
Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access your services:" -ForegroundColor Cyan
Write-Host "   • Frontend:  http://localhost:3000"
Write-Host "   • Backend:   http://localhost:8000"
Write-Host "   • API Docs:  http://localhost:8000/docs"
Write-Host "   • Database:  localhost:5433 (user: aphrodite, password: aphrodite123)"
Write-Host "   • Redis:     localhost:6379"
Write-Host ""
Write-Host "🔧 Useful commands:" -ForegroundColor Cyan
Write-Host "   • View logs:        docker-compose -f docker-compose.dev.yml logs -f"
Write-Host "   • Stop services:    docker-compose -f docker-compose.dev.yml down"
Write-Host "   • Restart service:  docker-compose -f docker-compose.dev.yml restart <service>"
Write-Host "   • Rebuild:          docker-compose -f docker-compose.dev.yml up --build"
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Configure Jellyfin connection at http://localhost:3000/settings"
Write-Host "   2. Import your anime library"
Write-Host "   3. Start developing! Code changes will auto-reload."
Write-Host ""
Write-Host "❓ Need help? Check CONTRIBUTING.md or open a GitHub Discussion." -ForegroundColor Yellow