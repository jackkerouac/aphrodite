# Aphrodite v2 Quick Docker Commands - PowerShell
# Common Docker Compose commands for managing Aphrodite v2

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "update", "clean", "reset", "help")]
    [string]$Action = "help"
)

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "🐋 $Title" -ForegroundColor Blue
    Write-Host "=================================="
}

function Write-Step {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Yellow
}

switch ($Action) {
    "start" {
        Write-Header "Starting Aphrodite v2"
        Write-Info "Starting all services..."
        docker-compose up -d
        Write-Step "Services started! Visit http://localhost:8000"
    }
    
    "stop" {
        Write-Header "Stopping Aphrodite v2"
        Write-Info "Stopping all services..."
        docker-compose down
        Write-Step "All services stopped"
    }
    
    "restart" {
        Write-Header "Restarting Aphrodite v2"
        Write-Info "Restarting all services..."
        docker-compose restart
        Write-Step "Services restarted!"
    }
    
    "logs" {
        Write-Header "Aphrodite v2 Logs"
        Write-Info "Showing recent logs (Ctrl+C to exit)..."
        docker-compose logs -f
    }
    
    "status" {
        Write-Header "Service Status"
        docker-compose ps
        Write-Host ""
        Write-Info "Health check..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health/live" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Step "API is healthy and responding"
            } else {
                Write-Host "⚠️  API health check failed" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ API is not accessible" -ForegroundColor Red
        }
    }
    
    "update" {
        Write-Header "Updating Aphrodite v2"
        Write-Info "Pulling latest images..."
        docker-compose pull
        Write-Info "Recreating containers..."
        docker-compose up -d
        Write-Step "Update complete!"
    }
    
    "clean" {
        Write-Header "Cleaning Up"
        Write-Info "Removing unused Docker images..."
        docker image prune -f
        Write-Step "Cleanup complete!"
    }
    
    "reset" {
        Write-Header "Resetting Aphrodite v2"
        Write-Host "⚠️  WARNING: This will delete ALL data including:" -ForegroundColor Red
        Write-Host "   • Database content" -ForegroundColor Yellow
        Write-Host "   • Cache and logs" -ForegroundColor Yellow
        Write-Host "   • Configuration (but not your .env file)" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "Are you sure? Type 'yes' to confirm"
        
        if ($confirm -eq "yes") {
            Write-Info "Stopping services and removing volumes..."
            docker-compose down -v
            Write-Info "Starting fresh..."
            docker-compose up -d
            Write-Step "Reset complete! Visit http://localhost:8000 to reconfigure"
        } else {
            Write-Info "Reset cancelled"
        }
    }
    
    "help" {
        Write-Header "Aphrodite v2 Docker Management"
        Write-Host ""
        Write-Host "Usage: .\manage.ps1 <action>" -ForegroundColor White
        Write-Host ""
        Write-Host "Available actions:" -ForegroundColor Yellow
        Write-Host "  start    - Start all services" -ForegroundColor White
        Write-Host "  stop     - Stop all services" -ForegroundColor White
        Write-Host "  restart  - Restart all services" -ForegroundColor White
        Write-Host "  logs     - Show and follow logs" -ForegroundColor White
        Write-Host "  status   - Show service status and health" -ForegroundColor White
        Write-Host "  update   - Update to latest version" -ForegroundColor White
        Write-Host "  clean    - Clean up unused Docker images" -ForegroundColor White
        Write-Host "  reset    - Reset all data (⚠️  destructive)" -ForegroundColor White
        Write-Host "  help     - Show this help" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\manage.ps1 start" -ForegroundColor Green
        Write-Host "  .\manage.ps1 logs" -ForegroundColor Green
        Write-Host "  .\manage.ps1 status" -ForegroundColor Green
        Write-Host ""
        Write-Host "Quick access:" -ForegroundColor Yellow
        Write-Host "  • Web Interface: http://localhost:8000" -ForegroundColor White
        Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor White
    }
}
