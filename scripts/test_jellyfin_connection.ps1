# Jellyfin Connection Test
# Quick test to verify Jellyfin settings and connectivity before running the full analysis

param(
    [string]$ConfigFile = ".env"
)

# Function to read .env file and extract Jellyfin settings
function Get-JellyfinConfig {
    param([string]$EnvFile)
    
    $config = @{}
    
    if (Test-Path $EnvFile) {
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                $config[$key] = $value
            }
        }
    }
    
    return $config
}

# Function to make authenticated Jellyfin API calls
function Invoke-JellyfinAPI {
    param(
        [string]$Endpoint,
        [string]$BaseUrl,
        [string]$ApiKey
    )
    
    $headers = @{
        "X-Emby-Token" = $ApiKey
        "Content-Type" = "application/json"
    }
    
    $url = $BaseUrl.TrimEnd('/') + $Endpoint
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -TimeoutSec 10
        return $response
    }
    catch {
        Write-Warning "API call failed for $url : $($_.Exception.Message)"
        return $null
    }
}

Write-Host "Jellyfin Connection Test" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Load configuration
Write-Host "`nLoading configuration from: $ConfigFile" -ForegroundColor Cyan
$config = Get-JellyfinConfig -EnvFile $ConfigFile

$jellyfinUrl = $config["JELLYFIN_URL"]
$jellyfinApiKey = $config["JELLYFIN_API_KEY"]
$jellyfinUserId = $config["JELLYFIN_USER_ID"]

Write-Host "JELLYFIN_URL: $jellyfinUrl" -ForegroundColor White
Write-Host "JELLYFIN_API_KEY: $($jellyfinApiKey ? '***CONFIGURED***' : 'NOT SET')" -ForegroundColor White
Write-Host "JELLYFIN_USER_ID: $jellyfinUserId" -ForegroundColor White

if (-not $jellyfinUrl -or -not $jellyfinApiKey) {
    Write-Host "`nERROR: Missing required Jellyfin configuration!" -ForegroundColor Red
    Write-Host "Please ensure the following are set in ${ConfigFile}:" -ForegroundColor Red
    Write-Host "  JELLYFIN_URL=http://your-jellyfin-server:8096" -ForegroundColor Yellow
    Write-Host "  JELLYFIN_API_KEY=your-api-key-here" -ForegroundColor Yellow
    Write-Host "  JELLYFIN_USER_ID=your-user-id-here (optional)" -ForegroundColor Yellow
    exit 1
}

# Test system info endpoint
Write-Host "`nTesting connection to Jellyfin..." -ForegroundColor Cyan
$systemInfo = Invoke-JellyfinAPI -Endpoint "/System/Info" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey

if ($systemInfo) {
    Write-Host "SUCCESS: Connected to Jellyfin!" -ForegroundColor Green
    Write-Host "  Server: $($systemInfo.ServerName)" -ForegroundColor White
    Write-Host "  Version: $($systemInfo.Version)" -ForegroundColor White
    Write-Host "  ID: $($systemInfo.Id)" -ForegroundColor White
} else {
    Write-Host "FAILED: Could not connect to Jellyfin server" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Red
    Write-Host "  1. Jellyfin server is running and accessible" -ForegroundColor Yellow
    Write-Host "  2. URL is correct (include http/https and port)" -ForegroundColor Yellow  
    Write-Host "  3. API key is valid" -ForegroundColor Yellow
    exit 1
}

# Test libraries endpoint
Write-Host "`nTesting library access..." -ForegroundColor Cyan
$libraries = Invoke-JellyfinAPI -Endpoint "/Library/VirtualFolders" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey

if ($libraries) {
    Write-Host "SUCCESS: Can access libraries!" -ForegroundColor Green
    Write-Host "Found $($libraries.Count) libraries:" -ForegroundColor White
    foreach ($library in $libraries) {
        Write-Host "  - $($library.Name) (ID: $($library.ItemId))" -ForegroundColor Gray
    }
} else {
    Write-Host "WARNING: Could not access libraries" -ForegroundColor Yellow
    Write-Host "This might indicate a permissions issue with the API key" -ForegroundColor Yellow
}

# Test user-specific endpoint if user ID provided
if ($jellyfinUserId) {
    Write-Host "`nTesting user-specific access..." -ForegroundColor Cyan
    $userInfo = Invoke-JellyfinAPI -Endpoint "/Users/$jellyfinUserId" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey
    
    if ($userInfo) {
        Write-Host "SUCCESS: Can access user data!" -ForegroundColor Green
        Write-Host "  User: $($userInfo.Name)" -ForegroundColor White
    } else {
        Write-Host "WARNING: Could not access user data" -ForegroundColor Yellow
        Write-Host "User ID might be incorrect or API key lacks permissions" -ForegroundColor Yellow
    }
}

Write-Host "`nConnection test complete!" -ForegroundColor Green
Write-Host "`nIf all tests passed, you can now run:" -ForegroundColor Cyan
Write-Host "  .\scripts\jellyfin_codec_analyzer.ps1" -ForegroundColor White
Write-Host "`nFor a small test run, try:" -ForegroundColor Cyan  
Write-Host "  .\scripts\jellyfin_codec_analyzer.ps1 -MaxItems 10 -Verbose" -ForegroundColor White
