# Reset Development Database Script (PowerShell)
# Completely resets the development database with fresh data

param(
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Reset Development Database Script

USAGE:
    .\reset-db.ps1 [OPTIONS]

OPTIONS:
    -Force    Skip confirmation prompt
    -Help     Show this help message

DESCRIPTION:
    Completely resets the development database by removing the container,
    volume, and recreating everything with fresh data.

WARNING:
    This will delete ALL data in the development database.

EXAMPLES:
    .\reset-db.ps1         # Interactive mode with confirmation
    .\reset-db.ps1 -Force  # Skip confirmation
"@
    exit 0
}

# Color output functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🗄️ Resetting Aphrodite development database..." -ForegroundColor Cyan

# Confirm action unless -Force is used
if (-not $Force) {
    $response = Read-Host "This will delete ALL data in the development database. Are you sure? (y/N)"
    if ($response -notmatch "^[Yy]$") {
        Write-Status "Database reset cancelled."
        exit 0
    }
}

# Stop dependent services
Write-Status "Stopping API and worker services..."
docker-compose -f docker-compose.dev.yml stop api worker

# Stop and remove database container
Write-Status "Stopping and removing database container..."
docker-compose -f docker-compose.dev.yml stop postgres
docker-compose -f docker-compose.dev.yml rm -f postgres

# Remove database volume
Write-Status "Removing database volume..."
try {
    docker volume rm aphrodite_postgres_data 2>$null
} catch {
    # Volume might not exist, ignore error
}

# Start database service
Write-Status "Starting fresh database..."
docker-compose -f docker-compose.dev.yml up -d postgres

# Wait for database to be ready
Write-Status "Waiting for database to initialize..."
Start-Sleep -Seconds 15

# Check if database is ready
$retries = 0
$maxRetries = 30
do {
    try {
        docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite | Out-Null
        break
    } catch {
        $retries++
        if ($retries -ge $maxRetries) {
            Write-Error "Database failed to start after $maxRetries attempts"
            exit 1
        }
        Write-Status "Waiting for database... ($retries/$maxRetries)"
        Start-Sleep -Seconds 2
    }
} while ($retries -lt $maxRetries)

# Start API service
Write-Status "Starting API service..."
docker-compose -f docker-compose.dev.yml up -d api

# Wait for API to be ready
Start-Sleep -Seconds 10

# Initialize database with default data
Write-Status "Initializing database with default settings..."
try {
    docker-compose -f docker-compose.dev.yml exec api python database_defaults_init.py
} catch {
    Write-Warning "Database initialization encountered an issue - this may be normal"
}

# Start worker service
Write-Status "Starting worker service..."
docker-compose -f docker-compose.dev.yml up -d worker

# Verify services are running
Write-Status "Verifying services..."
Start-Sleep -Seconds 5

try {
    docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aphrodite | Out-Null
    Write-Success "Database is ready"
} catch {
    Write-Error "Database failed to start properly"
    exit 1
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health/live" -TimeoutSec 5 -ErrorAction Stop
    Write-Success "API is running"
} catch {
    Write-Warning "API may still be starting up"
}

Write-Host ""
Write-Success "Database reset complete! 🎉"
Write-Host ""
Write-Status "Next steps:"
Write-Host "   1. Visit http://localhost:3000/settings to configure Jellyfin"
Write-Host "   2. Import your anime library"
Write-Host "   3. Set up user preferences"
Write-Host ""
Write-Status "Database details:"
Write-Host "   • Host: localhost:5433"
Write-Host "   • Database: aphrodite"
Write-Host "   • Username: aphrodite"
Write-Host "   • Password: aphrodite123"