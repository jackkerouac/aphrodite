# Aphrodite v2 Docker Setup Script - PowerShell Version
# This script helps users set up Aphrodite v2 with Docker on Windows

function Write-Message {
    param(
        [string]$Color,
        [string]$Message
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Yellow
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "🐋 $Title" -ForegroundColor Blue
    Write-Host "=================================="
}

function Generate-Password {
    # Generate a random password
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $password = ""
    for ($i = 0; $i -lt 25; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

function Generate-SecretKey {
    # Generate a random secret key
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $key = ""
    for ($i = 0; $i -lt 64; $i++) {
        $key += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $key
}

Write-Header "Aphrodite v2 Quick Setup"
Write-Host ""
Write-Host "This script will set up Aphrodite v2 with Docker in just a few steps!"
Write-Host ""

# Check if Docker is available
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Step "Docker is installed: $dockerVersion"
    } else {
        Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
        Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Step "Docker Compose is available: $composeVersion"
    } else {
        Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

# Create essential directories
Write-Info "Creating directories..."
if (!(Test-Path "posters")) {
    New-Item -ItemType Directory -Path "posters" | Out-Null
}
if (!(Test-Path "images")) {
    New-Item -ItemType Directory -Path "images" | Out-Null
}
Write-Step "Created posters and images directories"

# Generate .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Info "Generating secure configuration..."
    
    $postgresPass = Generate-Password
    $redisPass = Generate-Password
    $secretKey = Generate-SecretKey
    
    # Get current user ID (Windows equivalent)
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $userSid = $currentUser.User.Value
    
    $envContent = @"
# Aphrodite v2 Configuration - Generated $(Get-Date)

# Database & Redis passwords (auto-generated)
POSTGRES_PASSWORD=$postgresPass
REDIS_PASSWORD=$redisPass

# Application ports
API_PORT=8000
FRONTEND_PORT=3000

# Security key (auto-generated)
SECRET_KEY=$secretKey

# User permissions (Windows - using default)
PUID=1000
PGID=1000

# Logging
LOG_LEVEL=INFO
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Step "Generated .env configuration with secure passwords"
} else {
    Write-Step ".env file already exists"
}

Write-Step "Setup completed successfully"

Write-Host ""
Write-Header "Ready to Start!"
Write-Host ""
Write-Host "🚀 Run these commands to start Aphrodite:" -ForegroundColor Green
Write-Host ""
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "📱 Then visit: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "📋 What to do next:" -ForegroundColor Yellow
Write-Host "   1. Wait for services to start (about 1-2 minutes)"
Write-Host "   2. Open http://localhost:8000 in your browser"
Write-Host "   3. Configure your Jellyfin server and API keys in the web interface"
Write-Host "   4. Start processing your media!"
Write-Host ""
Write-Host "📁 Directory info:" -ForegroundColor Yellow
Write-Host "   • .\posters\ - Your processed poster images will be saved here"
Write-Host "   • .\images\  - Badge images and assets (customize as needed)"
Write-Host ""
Write-Host "🔧 Need help? Check the logs with: docker-compose logs -f" -ForegroundColor Yellow
