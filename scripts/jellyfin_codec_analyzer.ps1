# Jellyfin Codec and Resolution Analyzer
# Polls all movies and series from Jellyfin and saves detailed codec information for analysis

param(
    [string]$OutputFile = "jellyfin_codec_analysis.json",
    [string]$ConfigFile = ".env",
    [int]$MaxItems = 0,  # 0 = no limit
    [switch]$Verbose
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
        [string]$ApiKey,
        [hashtable]$QueryParams = @{}
    )
    
    $headers = @{
        "X-Emby-Token" = $ApiKey
        "Content-Type" = "application/json"
    }
    
    $url = $BaseUrl.TrimEnd('/') + $Endpoint
    
    if ($QueryParams.Count -gt 0) {
        $queryString = ($QueryParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
        $url += "?$queryString"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -TimeoutSec 30
        return $response
    }
    catch {
        Write-Warning "API call failed for $url : $($_.Exception.Message)"
        return $null
    }
}

# Function to extract detailed codec information from media item
function Get-DetailedCodecInfo {
    param([object]$MediaItem)
    
    $maxHeight = 0
    $detectedHDR = $false
    $detectedDV = $false
    $mediaSources = @()
    
    # Process MediaSources if available
    if ($MediaItem.MediaSources) {
        foreach ($source in $MediaItem.MediaSources) {
            $videoStreams = @()
            $audioStreams = @()
            $subtitleStreams = @()
            
            # Process MediaStreams
            if ($source.MediaStreams) {
                foreach ($stream in $source.MediaStreams) {
                    if ($stream.Type -eq "Video") {
                        $videoStreams += [PSCustomObject]@{
                            Index = $stream.Index
                            Type = $stream.Type
                            Codec = $stream.Codec
                            Profile = $stream.Profile
                            Level = $stream.Level
                            Width = $stream.Width
                            Height = $stream.Height
                            AspectRatio = $stream.AspectRatio
                            VideoRange = $stream.VideoRange
                            ColorSpace = $stream.ColorSpace
                            ColorTransfer = $stream.ColorTransfer
                            ColorPrimaries = $stream.ColorPrimaries
                            FrameRate = $stream.RealFrameRate
                            BitRate = $stream.BitRate
                            BitDepth = $stream.BitDepth
                            PixelFormat = $stream.PixelFormat
                        }
                        
                        # Track highest resolution across all video streams
                        if ($stream.Height -and [int]$stream.Height -gt $maxHeight) {
                            $maxHeight = [int]$stream.Height
                        }
                        
                        # Detect HDR
                        $videoRange = $stream.VideoRange
                        $colorSpace = $stream.ColorSpace
                        $codec = $stream.Codec
                        
                        if ($videoRange -match "HDR|HDR10|DOLBY" -or 
                            $colorSpace -match "BT2020" -or 
                            $codec -match "HDR") {
                            $detectedHDR = $true
                        }
                        
                        # Detect Dolby Vision
                        if ($videoRange -match "DOLBY|DV" -or 
                            $codec -match "DOLBY|DV" -or
                            $stream.Profile -match "DOLBY|DV") {
                            $detectedDV = $true
                        }
                    }
                    elseif ($stream.Type -eq "Audio") {
                        $audioStreams += [PSCustomObject]@{
                            Index = $stream.Index
                            Type = $stream.Type
                            Codec = $stream.Codec
                            Profile = $stream.Profile
                            Level = $stream.Level
                            Channels = $stream.Channels
                            ChannelLayout = $stream.ChannelLayout
                            SampleRate = $stream.SampleRate
                            BitRate = $stream.BitRate
                            Language = $stream.Language
                            Title = $stream.Title
                            IsDefault = $stream.IsDefault
                        }
                    }
                    elseif ($stream.Type -eq "Subtitle") {
                        $subtitleStreams += [PSCustomObject]@{
                            Index = $stream.Index
                            Type = $stream.Type
                            Codec = $stream.Codec
                            Profile = $stream.Profile
                            Level = $stream.Level
                            Language = $stream.Language
                            Title = $stream.Title
                            IsDefault = $stream.IsDefault
                            IsForced = $stream.IsForced
                        }
                    }
                }
            }
            
            $mediaSources += [PSCustomObject]@{
                Id = $source.Id
                Path = $source.Path
                Container = $source.Container
                Size = $source.Size
                VideoStreams = $videoStreams
                AudioStreams = $audioStreams
                SubtitleStreams = $subtitleStreams
            }
        }
    }
    
    # Determine final resolution based on highest height found
    $detectedResolution = $null
    if ($maxHeight -gt 0) {
        $baseResolution = switch ($maxHeight) {
            { $_ -ge 2160 } { "4K" }
            { $_ -ge 1440 } { "1440p" }
            { $_ -ge 1080 } { "1080p" }
            { $_ -ge 720 } { "720p" }
            { $_ -ge 480 } { "480p" }
            default { "${maxHeight}p" }
        }
        
        # Add HDR suffix if detected
        if ($detectedDV) {
            $detectedResolution = "$baseResolution DV"
        } elseif ($detectedHDR) {
            $detectedResolution = "$baseResolution HDR"
        } else {
            $detectedResolution = $baseResolution
        }
    }
    
    return [PSCustomObject]@{
        Id = $MediaItem.Id
        Name = $MediaItem.Name
        Type = $MediaItem.Type
        Year = $MediaItem.ProductionYear
        Path = $MediaItem.Path
        MediaSources = $mediaSources
        DetectedResolution = $detectedResolution
        DetectedHDR = $detectedHDR
        DetectedDolbyVision = $detectedDV
        LibraryName = ""
    }
}

# Main execution
Write-Host "Jellyfin Codec and Resolution Analyzer" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Load configuration
$config = Get-JellyfinConfig -EnvFile $ConfigFile
$jellyfinUrl = $config["JELLYFIN_URL"]
$jellyfinApiKey = $config["JELLYFIN_API_KEY"]
$jellyfinUserId = $config["JELLYFIN_USER_ID"]

if (-not $jellyfinUrl -or -not $jellyfinApiKey) {
    Write-Error "Jellyfin configuration not found in $ConfigFile. Please ensure JELLYFIN_URL and JELLYFIN_API_KEY are set."
    exit 1
}

Write-Host "Jellyfin Server: $jellyfinUrl" -ForegroundColor Cyan
Write-Host "Output File: $OutputFile" -ForegroundColor Cyan

# Test connection
Write-Host "`nTesting Jellyfin connection..." -ForegroundColor Yellow
$systemInfo = Invoke-JellyfinAPI -Endpoint "/System/Info" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey

if (-not $systemInfo) {
    Write-Error "Failed to connect to Jellyfin server. Please check your configuration."
    exit 1
}

Write-Host "Connected to: $($systemInfo.ServerName) v$($systemInfo.Version)" -ForegroundColor Green

# Get all libraries
Write-Host "`nFetching libraries..." -ForegroundColor Yellow
$libraries = Invoke-JellyfinAPI -Endpoint "/Library/VirtualFolders" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey

if (-not $libraries) {
    Write-Error "Failed to fetch libraries."
    exit 1
}

Write-Host "Found $($libraries.Count) libraries" -ForegroundColor Green

$allItems = @()
$processedCount = 0

foreach ($library in $libraries) {
    $libraryName = $library.Name
    $libraryId = $library.ItemId
    
    Write-Host "`nProcessing library: $libraryName" -ForegroundColor Cyan
    
    # Get all items in this library with detailed fields
    $queryParams = @{
        "ParentId" = $libraryId
        "Recursive" = "true"
        "Fields" = "MediaSources,MediaStreams,Path,ProviderIds"
        "IncludeItemTypes" = "Movie,Series"
    }
    
    $libraryItems = Invoke-JellyfinAPI -Endpoint "/Items" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey -QueryParams $queryParams
    
    if ($libraryItems -and $libraryItems.Items) {
        Write-Host "  Found $($libraryItems.Items.Count) items" -ForegroundColor White
        
        foreach ($item in $libraryItems.Items) {
            $processedCount++
            
            if ($MaxItems -gt 0 -and $processedCount -gt $MaxItems) {
                Write-Host "  Reached maximum item limit ($MaxItems)" -ForegroundColor Yellow
                break
            }
            
            if ($Verbose) {
                Write-Host "    Processing: $($item.Name) ($($item.Type))" -ForegroundColor Gray
            }
            
            # Get detailed item information with MediaSources
            $detailedItem = $null
            if ($jellyfinUserId) {
                $detailedItem = Invoke-JellyfinAPI -Endpoint "/Users/$jellyfinUserId/Items/$($item.Id)" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey -QueryParams @{"Fields" = "MediaSources,MediaStreams"}
            }
            
            if (-not $detailedItem) {
                $detailedItem = Invoke-JellyfinAPI -Endpoint "/Items/$($item.Id)" -BaseUrl $jellyfinUrl -ApiKey $jellyfinApiKey -QueryParams @{"Fields" = "MediaSources,MediaStreams"}
            }
            
            if ($detailedItem) {
                $codecInfo = Get-DetailedCodecInfo -MediaItem $detailedItem
                $codecInfo.LibraryName = $libraryName
                $allItems += $codecInfo
            }
            
            # Progress indicator
            if ($processedCount % 10 -eq 0) {
                Write-Host "    Processed $processedCount items..." -ForegroundColor Gray
            }
        }
        
        if ($MaxItems -gt 0 -and $processedCount -ge $MaxItems) {
            break
        }
    }
}

Write-Host "`nTotal items processed: $processedCount" -ForegroundColor Green

# Generate summary statistics (using PSCustomObject for proper JSON serialization)
$resolutionCounts = @{}
$codecCounts = @{}

# Calculate resolution distribution
$allItems | ForEach-Object {
    $res = $_.DetectedResolution
    if ($res) {
        if ($resolutionCounts.ContainsKey($res)) {
            $resolutionCounts[$res]++
        } else {
            $resolutionCounts[$res] = 1
        }
    }
}

# Calculate video codec distribution
$allItems | ForEach-Object {
    foreach ($source in $_.MediaSources) {
        foreach ($videoStream in $source.VideoStreams) {
            $codec = $videoStream.Codec
            if ($codec) {
                if ($codecCounts.ContainsKey($codec)) {
                    $codecCounts[$codec]++
                } else {
                    $codecCounts[$codec] = 1
                }
            }
        }
    }
}

# Create summary using PSCustomObject for better JSON serialization
$summary = [PSCustomObject]@{
    TotalItems = $allItems.Count
    Movies = ($allItems | Where-Object { $_.Type -eq "Movie" }).Count
    Series = ($allItems | Where-Object { $_.Type -eq "Series" }).Count
    ResolutionDistribution = $resolutionCounts
    HDRCount = ($allItems | Where-Object { $_.DetectedHDR }).Count
    DolbyVisionCount = ($allItems | Where-Object { $_.DetectedDolbyVision }).Count
    CodecDistribution = $codecCounts
    ProcessedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Create final output using PSCustomObject
$output = [PSCustomObject]@{
    Summary = $summary
    Items = $allItems
}

# Save to JSON file with better error handling
try {
    $json = $output | ConvertTo-Json -Depth 10
    $json | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host "`nAnalysis complete!" -ForegroundColor Green
    Write-Host "Results saved to: $OutputFile" -ForegroundColor Cyan
} catch {
    Write-Warning "Error saving JSON file: $($_.Exception.Message)"
    Write-Host "Continuing with summary display..." -ForegroundColor Yellow
}

Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "  Total Items: $($summary.TotalItems)"
Write-Host "  Movies: $($summary.Movies)"
Write-Host "  Series: $($summary.Series)"
Write-Host "  HDR Items: $($summary.HDRCount)"
Write-Host "  Dolby Vision Items: $($summary.DolbyVisionCount)"
Write-Host "`nResolution Distribution:" -ForegroundColor Yellow
$resolutionCounts.GetEnumerator() | Sort-Object Key | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}
Write-Host "`nVideo Codec Distribution:" -ForegroundColor Yellow
$codecCounts.GetEnumerator() | Sort-Object Key | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}

Write-Host "`nTo run this script:" -ForegroundColor Green
Write-Host "  .\scripts\jellyfin_codec_analyzer.ps1" -ForegroundColor White
Write-Host "  .\scripts\jellyfin_codec_analyzer.ps1 -OutputFile 'my_analysis.json' -Verbose" -ForegroundColor White
Write-Host "  .\scripts\jellyfin_codec_analyzer.ps1 -MaxItems 100" -ForegroundColor White
