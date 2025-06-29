# Jellyfin Codec and Resolution Analyzer - Robust Version
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

# Function to safely convert data to JSON with fallback
function Export-SafeJson {
    param(
        [object]$Data,
        [string]$FilePath
    )
    
    try {
        # Try PowerShell's ConvertTo-Json first
        $json = $Data | ConvertTo-Json -Depth 10 -Compress:$false
        $json | Out-File -FilePath $FilePath -Encoding UTF8 -Force
        Write-Host "Successfully saved JSON to: $FilePath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Warning "ConvertTo-Json failed: $($_.Exception.Message)"
        
        # Fallback: Create a simpler structure
        try {
            $simpleData = @{
                "Summary" = @{
                    "TotalItems" = $Data.Summary.TotalItems
                    "Movies" = $Data.Summary.Movies
                    "Series" = $Data.Summary.Series
                    "HDRCount" = $Data.Summary.HDRCount
                    "DolbyVisionCount" = $Data.Summary.DolbyVisionCount
                    "ProcessedAt" = $Data.Summary.ProcessedAt
                }
                "Items" = @()
            }
            
            # Add simplified items
            foreach ($item in $Data.Items) {
                $simpleItem = @{
                    "Id" = $item.Id
                    "Name" = $item.Name
                    "Type" = $item.Type
                    "Year" = $item.Year
                    "LibraryName" = $item.LibraryName
                    "DetectedResolution" = $item.DetectedResolution
                    "DetectedHDR" = $item.DetectedHDR
                    "DetectedDolbyVision" = $item.DetectedDolbyVision
                    "VideoStreamsCount" = 0
                    "AudioStreamsCount" = 0
                }
                
                # Count streams
                foreach ($source in $item.MediaSources) {
                    $simpleItem.VideoStreamsCount += $source.VideoStreams.Count
                    $simpleItem.AudioStreamsCount += $source.AudioStreams.Count
                }
                
                $simpleData.Items += $simpleItem
            }
            
            $fallbackJson = $simpleData | ConvertTo-Json -Depth 5
            $fallbackJson | Out-File -FilePath $FilePath -Encoding UTF8 -Force
            Write-Host "Saved simplified JSON to: $FilePath" -ForegroundColor Yellow
            return $true
        }
        catch {
            Write-Error "Both JSON export methods failed: $($_.Exception.Message)"
            return $false
        }
    }
}

# Function to extract detailed codec information from media item
function Get-DetailedCodecInfo {
    param([object]$MediaItem)
    
    $maxHeight = 0
    $detectedHDR = $false
    $detectedDV = $false
    $videoCodecs = @()
    $audioCodecs = @()
    $videoRanges = @()
    $colorSpaces = @()
    
    # Process MediaSources if available
    if ($MediaItem.MediaSources) {
        foreach ($source in $MediaItem.MediaSources) {
            # Process MediaStreams
            if ($source.MediaStreams) {
                foreach ($stream in $source.MediaStreams) {
                    if ($stream.Type -eq "Video") {
                        # Track highest resolution
                        if ($stream.Height -and [int]$stream.Height -gt $maxHeight) {
                            $maxHeight = [int]$stream.Height
                        }
                        
                        # Collect codec info
                        if ($stream.Codec) { $videoCodecs += $stream.Codec }
                        if ($stream.VideoRange) { $videoRanges += $stream.VideoRange }
                        if ($stream.ColorSpace) { $colorSpaces += $stream.ColorSpace }
                        
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
                        if ($stream.Codec) { $audioCodecs += $stream.Codec }
                    }
                }
            }
        }
    }
    
    # Determine final resolution
    $detectedResolution = "Unknown"
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
    
    # Return simple structure that JSON can handle
    return @{
        Id = $MediaItem.Id
        Name = $MediaItem.Name
        Type = $MediaItem.Type
        Year = $MediaItem.ProductionYear
        Path = $MediaItem.Path
        LibraryName = ""
        DetectedResolution = $detectedResolution
        DetectedHDR = $detectedHDR
        DetectedDolbyVision = $detectedDV
        VideoCodecs = ($videoCodecs | Select-Object -Unique) -join ", "
        AudioCodecs = ($audioCodecs | Select-Object -Unique) -join ", "
        VideoRanges = ($videoRanges | Select-Object -Unique) -join ", "
        ColorSpaces = ($colorSpaces | Select-Object -Unique) -join ", "
        MaxHeight = $maxHeight
    }
}

# Main execution
Write-Host "Jellyfin Codec and Resolution Analyzer - Robust Version" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

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
            if ($processedCount % 50 -eq 0) {
                Write-Host "    Processed $processedCount items..." -ForegroundColor Gray
            }
        }
        
        if ($MaxItems -gt 0 -and $processedCount -ge $MaxItems) {
            break
        }
    }
}

Write-Host "`nTotal items processed: $processedCount" -ForegroundColor Green

# Generate summary statistics
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

# Calculate video codec distribution from VideoCodecs field
$allItems | ForEach-Object {
    if ($_.VideoCodecs) {
        $codecs = $_.VideoCodecs -split ", "
        foreach ($codec in $codecs) {
            $codec = $codec.Trim()
            if ($codec -and $codec -ne "") {
                if ($codecCounts.ContainsKey($codec)) {
                    $codecCounts[$codec]++
                } else {
                    $codecCounts[$codec] = 1
                }
            }
        }
    }
}

# Create final output structure
$output = @{
    Summary = @{
        TotalItems = $allItems.Count
        Movies = ($allItems | Where-Object { $_.Type -eq "Movie" }).Count
        Series = ($allItems | Where-Object { $_.Type -eq "Series" }).Count
        ResolutionDistribution = $resolutionCounts
        HDRCount = ($allItems | Where-Object { $_.DetectedHDR }).Count
        DolbyVisionCount = ($allItems | Where-Object { $_.DetectedDolbyVision }).Count
        CodecDistribution = $codecCounts
        ProcessedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    Items = $allItems
}

# Export to JSON with error handling
$jsonSaved = Export-SafeJson -Data $output -FilePath $OutputFile

# Also save a CSV backup for easier analysis
$csvFile = $OutputFile -replace "\.json$", ".csv"
try {
    $allItems | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8
    Write-Host "Also saved CSV backup to: $csvFile" -ForegroundColor Green
}
catch {
    Write-Warning "Could not save CSV backup: $($_.Exception.Message)"
}

Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "  Total Items: $($output.Summary.TotalItems)"
Write-Host "  Movies: $($output.Summary.Movies)"
Write-Host "  Series: $($output.Summary.Series)"
Write-Host "  HDR Items: $($output.Summary.HDRCount)"
Write-Host "  Dolby Vision Items: $($output.Summary.DolbyVisionCount)"

Write-Host "`nResolution Distribution:" -ForegroundColor Yellow
$resolutionCounts.GetEnumerator() | Sort-Object Key | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}

Write-Host "`nVideo Codec Distribution:" -ForegroundColor Yellow
$codecCounts.GetEnumerator() | Sort-Object Key | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}

if (-not $jsonSaved) {
    Write-Host "`nJSON export failed, but you can still analyze the CSV file:" -ForegroundColor Yellow
    Write-Host "  Import-Csv '$csvFile' | Format-Table" -ForegroundColor White
}

Write-Host "`nTo analyze results:" -ForegroundColor Green
Write-Host "  .\scripts\analyze_codec_results.ps1 -InputFile '$OutputFile'" -ForegroundColor White
