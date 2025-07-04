# Aphrodite Local Development Reset Script (PowerShell)
# Run this in your VSCode PowerShell terminal

Write-Host "🧹 Resetting Aphrodite Local Development Environment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Stop all containers first
Write-Host "1. Stopping Docker containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "2. Removing Docker volumes (database data)..." -ForegroundColor Yellow
# Remove named volumes
docker volume rm aphrodite_postgres_data 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   - postgres_data volume not found (ok)" -ForegroundColor Gray }

docker volume rm aphrodite_redis_data 2>$null  
if ($LASTEXITCODE -ne 0) { Write-Host "   - redis_data volume not found (ok)" -ForegroundColor Gray }

# Remove any other aphrodite volumes
$volumes = docker volume ls --format "{{.Name}}" | Where-Object { $_ -like "*aphrodite*" }
if ($volumes) {
    $volumes | ForEach-Object { docker volume rm $_ }
    Write-Host "   - Removed additional volumes: $($volumes -join ', ')" -ForegroundColor Gray
}

Write-Host ""
Write-Host "3. Removing Docker containers and networks..." -ForegroundColor Yellow
docker-compose rm -f

# Remove aphrodite networks
$networks = docker network ls --format "{{.Name}}" | Where-Object { $_ -like "*aphrodite*" }
if ($networks) {
    $networks | ForEach-Object { docker network rm $_ 2>$null }
    Write-Host "   - Removed networks: $($networks -join ', ')" -ForegroundColor Gray
}

Write-Host ""
Write-Host "4. Clearing local cache and build files..." -ForegroundColor Yellow
# Clear Next.js build cache
if (Test-Path "frontend\.next") {
    Remove-Item -Recurse -Force "frontend\.next"
    Write-Host "   - Cleared Next.js .next directory" -ForegroundColor Gray
}

if (Test-Path "frontend\node_modules\.cache") {
    Remove-Item -Recurse -Force "frontend\node_modules\.cache"
    Write-Host "   - Cleared Node.js cache" -ForegroundColor Gray
}

# Clear Python cache
Get-ChildItem -Path "api" -Name "__pycache__" -Recurse -Directory | ForEach-Object {
    Remove-Item -Recurse -Force "api\$_" 2>$null
}
Get-ChildItem -Path "api" -Name "*.pyc" -Recurse -File | ForEach-Object {
    Remove-Item -Force "api\$_" 2>$null
}
Write-Host "   - Cleared Python cache files" -ForegroundColor Gray

# Clear any local logs
if (Test-Path "logs") {
    Get-ChildItem -Path "logs" -Name "*.log" | ForEach-Object {
        Remove-Item -Force "logs\$_" 2>$null
    }
    Write-Host "   - Cleared log files" -ForegroundColor Gray
}

Write-Host ""
Write-Host "5. Clearing static files and processed data..." -ForegroundColor Yellow
# Clear processed posters
if (Test-Path "api\static\posters\processed") {
    Get-ChildItem -Path "api\static\posters\processed" | Remove-Item -Recurse -Force 2>$null
    Write-Host "   - Cleared processed posters" -ForegroundColor Gray
}

if (Test-Path "api\static\preview") {
    Get-ChildItem -Path "api\static\preview" | Remove-Item -Recurse -Force 2>$null
    Write-Host "   - Cleared preview files" -ForegroundColor Gray
}

# Recreate directories
New-Item -ItemType Directory -Force -Path "api\static\posters\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "api\static\preview" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host ""
Write-Host "6. Resetting configuration..." -ForegroundColor Yellow
# Backup current .env files if they exist
if (Test-Path ".env") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item ".env" ".env.backup.$timestamp"
    Write-Host "   - Backed up .env to .env.backup.$timestamp" -ForegroundColor Gray
}

if (Test-Path ".env.development") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item ".env.development" ".env.development.backup.$timestamp"
    Write-Host "   - Backed up .env.development to .env.development.backup.$timestamp" -ForegroundColor Gray
}

Write-Host ""
Write-Host "7. Optional: Remove Docker images to force rebuild..." -ForegroundColor Yellow
Write-Host "   Run these commands if you want to rebuild from scratch:" -ForegroundColor Gray
Write-Host "   docker rmi aphrodite-api aphrodite-frontend aphrodite-worker 2>`$null" -ForegroundColor DarkGray
Write-Host "   docker image prune -f" -ForegroundColor DarkGray

Write-Host ""
Write-Host "✅ Environment reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your .env file with Jellyfin settings" -ForegroundColor White
Write-Host "2. Run: docker-compose up --build" -ForegroundColor White
Write-Host "3. Wait for database initialization" -ForegroundColor White
Write-Host "4. Access: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "To replicate user issues:" -ForegroundColor Cyan
Write-Host "- Use different Jellyfin server/credentials" -ForegroundColor White
Write-Host "- Test with libraries that have missing/deleted items" -ForegroundColor White
Write-Host "- Try batch processing with invalid poster IDs" -ForegroundColor White