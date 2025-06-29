# Jellyfin Codec Analysis Results Viewer
# Analyzes the output from jellyfin_codec_analyzer.ps1 to help improve resolution detection

param(
    [string]$InputFile = "jellyfin_codec_analysis.json",
    [switch]$ShowMisdetections,
    [switch]$ShowCodecImages,
    [switch]$ExportCSV
)

function Show-ResolutionAnalysis {
    param([object]$Data)
    
    Write-Host "`n=== RESOLUTION ANALYSIS ===" -ForegroundColor Green
    
    # Show current detection patterns
    $resolutionGroups = $Data.Items | Group-Object -Property DetectedResolution | Sort-Object Count -Descending
    
    Write-Host "`nCurrent Resolution Detection Results:" -ForegroundColor Yellow
    foreach ($group in $resolutionGroups) {
        $resName = if ($group.Name) { $group.Name } else { "Unknown" }
        Write-Host "  ${resName}: $($group.Count) items" -ForegroundColor White
    }
    
    # Analyze potential misdetections by examining actual video dimensions
    Write-Host "`nPotential Resolution Misdetections:" -ForegroundColor Yellow
    $misdetections = @()
    
    foreach ($item in $Data.Items) {
        foreach ($source in $item.MediaSources) {
            foreach ($videoStream in $source.VideoStreams) {
                if ($videoStream.Height -and $videoStream.Width) {
                    $actualHeight = [int]$videoStream.Height
                    $actualWidth = [int]$videoStream.Width
                    $detectedRes = $item.DetectedResolution
                    
                    $expectedRes = switch ($actualHeight) {
                        { $_ -ge 2160 } { "4K" }
                        { $_ -ge 1440 } { "1440p" }
                        { $_ -ge 1080 } { "1080p" }
                        { $_ -ge 720 } { "720p" }
                        { $_ -ge 480 } { "480p" }
                        default { "${actualHeight}p" }
                    }
                    
                    if ($detectedRes -ne $expectedRes) {
                        $misdetections += @{
                            Name = $item.Name
                            Type = $item.Type
                            ActualDimensions = "${actualWidth}x${actualHeight}"
                            ExpectedResolution = $expectedRes
                            DetectedResolution = $detectedRes
                            VideoRange = $videoStream.VideoRange
                            ColorSpace = $videoStream.ColorSpace
                            Codec = $videoStream.Codec
                        }
                    }
                }
            }
        }
    }
    
    if ($misdetections.Count -gt 0) {
        Write-Host "  Found $($misdetections.Count) potential misdetections:" -ForegroundColor Red
        $misdetections | Select-Object -First 10 | ForEach-Object {
            Write-Host "    $($_.Name): $($_.ActualDimensions) -> Expected: $($_.ExpectedResolution), Got: $($_.DetectedResolution)" -ForegroundColor Red
        }
        if ($misdetections.Count -gt 10) {
            Write-Host "    ... and $($misdetections.Count - 10) more" -ForegroundColor Red
        }
    } else {
        Write-Host "  No resolution misdetections found!" -ForegroundColor Green
    }
    
    return $misdetections
}

function Show-HDRAnalysis {
    param([object]$Data)
    
    Write-Host "`n=== HDR/DOLBY VISION ANALYSIS ===" -ForegroundColor Green
    
    $hdrItems = $Data.Items | Where-Object { $_.DetectedHDR }
    $dolbyVisionItems = $Data.Items | Where-Object { $_.DetectedDolbyVision }
    
    Write-Host "`nHDR Detection Results:" -ForegroundColor Yellow
    Write-Host "  HDR Items: $($hdrItems.Count)" -ForegroundColor White
    Write-Host "  Dolby Vision Items: $($dolbyVisionItems.Count)" -ForegroundColor White
    
    # Analyze HDR detection patterns
    Write-Host "`nHDR Detection Patterns:" -ForegroundColor Yellow
    $hdrPatterns = @{}
    
    foreach ($item in $Data.Items) {
        foreach ($source in $item.MediaSources) {
            foreach ($videoStream in $source.VideoStreams) {
                $videoRange = $videoStream.VideoRange
                $colorSpace = $videoStream.ColorSpace
                $codec = $videoStream.Codec
                
                if ($videoRange -or $colorSpace -or $codec) {
                    $pattern = "$videoRange|$colorSpace|$codec"
                    if (-not $hdrPatterns.ContainsKey($pattern)) {
                        $hdrPatterns[$pattern] = @{
                            Count = 0
                            Items = @()
                            HDRDetected = 0
                            DVDetected = 0
                        }
                    }
                    $hdrPatterns[$pattern].Count++
                    $hdrPatterns[$pattern].Items += $item.Name
                    if ($item.DetectedHDR) { $hdrPatterns[$pattern].HDRDetected++ }
                    if ($item.DetectedDolbyVision) { $hdrPatterns[$pattern].DVDetected++ }
                }
            }
        }
    }
    
    $sortedPatterns = $hdrPatterns.GetEnumerator() | Sort-Object { $_.Value.Count } -Descending | Select-Object -First 15
    
    foreach ($pattern in $sortedPatterns) {
        $parts = $pattern.Key -split '\|'
        $videoRange = $parts[0]
        $colorSpace = $parts[1] 
        $codec = $parts[2]
        
        $info = $pattern.Value
        $hdrRate = if ($info.Count -gt 0) { [math]::Round(($info.HDRDetected / $info.Count) * 100, 1) } else { 0 }
        $dvRate = if ($info.Count -gt 0) { [math]::Round(($info.DVDetected / $info.Count) * 100, 1) } else { 0 }
        
        Write-Host "  Pattern: VideoRange='$videoRange' ColorSpace='$colorSpace' Codec='$codec'" -ForegroundColor White
        Write-Host "    Count: $($info.Count), HDR: $($info.HDRDetected) (${hdrRate}%), DV: $($info.DVDetected) (${dvRate}%)" -ForegroundColor Gray
    }
}

function Show-CodecImageMapping {
    param([object]$Data)
    
    Write-Host "`n=== CODEC IMAGE MAPPING ===" -ForegroundColor Green
    
    # Get available codec images
    $codecImagePath = "images\codec"
    if (Test-Path $codecImagePath) {
        $availableImages = Get-ChildItem -Path $codecImagePath -Filter "*.png" | Select-Object -ExpandProperty BaseName
        Write-Host "`nAvailable Codec Images:" -ForegroundColor Yellow
        $availableImages | Sort-Object | ForEach-Object {
            Write-Host "  $_" -ForegroundColor White
        }
    }
    
    # Analyze audio codec combinations
    Write-Host "`nDetected Audio/Video Combinations:" -ForegroundColor Yellow
    $combinations = @{}
    
    foreach ($item in $Data.Items) {
        foreach ($source in $item.MediaSources) {
            $audioCodecs = $source.AudioStreams | ForEach-Object { $_.Codec } | Where-Object { $_ } | Select-Object -Unique
            $videoInfo = @{
                Resolution = $item.DetectedResolution
                HDR = $item.DetectedHDR
                DolbyVision = $item.DetectedDolbyVision
            }
            
            foreach ($audioCodec in $audioCodecs) {
                $key = "$audioCodec|$($videoInfo.Resolution)|$($videoInfo.HDR)|$($videoInfo.DolbyVision)"
                if (-not $combinations.ContainsKey($key)) {
                    $combinations[$key] = 0
                }
                $combinations[$key]++
            }
        }
    }
    
    $sortedCombinations = $combinations.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 20
    
    foreach ($combo in $sortedCombinations) {
        $parts = $combo.Key -split '\|'
        $audioCodec = $parts[0]
        $resolution = $parts[1]
        $isHDR = $parts[2] -eq "True"
        $isDV = $parts[3] -eq "True"
        
        $displayName = $audioCodec
        if ($isDV) { $displayName = "DV-$displayName" }
        elseif ($isHDR) { $displayName = "HDR-$displayName" }
        
        $imageExists = $availableImages -contains $displayName
        $status = if ($imageExists) { "[EXISTS]" } else { "[MISSING]" }
        $color = if ($imageExists) { "Green" } else { "Red" }
        
        Write-Host "  $displayName ($($combo.Value) items) $status" -ForegroundColor $color
    }
}

function Export-ToCSV {
    param([object]$Data, [string]$BaseFileName)
    
    Write-Host "`n=== EXPORTING TO CSV ===" -ForegroundColor Green
    
    # Export detailed item information
    $itemsCSV = $BaseFileName -replace "\.json$", "_items.csv"
    $csvData = @()
    
    foreach ($item in $Data.Items) {
        foreach ($source in $item.MediaSources) {
            $videoStream = $source.VideoStreams | Select-Object -First 1
            $audioStream = $source.AudioStreams | Select-Object -First 1
            
            $csvData += [PSCustomObject]@{
                Name = $item.Name
                Type = $item.Type
                Year = $item.Year
                Library = $item.LibraryName
                DetectedResolution = $item.DetectedResolution
                DetectedHDR = $item.DetectedHDR
                DetectedDolbyVision = $item.DetectedDolbyVision
                ActualWidth = $videoStream.Width
                ActualHeight = $videoStream.Height
                VideoCodec = $videoStream.Codec
                VideoRange = $videoStream.VideoRange
                ColorSpace = $videoStream.ColorSpace
                AudioCodec = $audioStream.Codec
                AudioChannels = $audioStream.Channels
                Container = $source.Container
                Path = $source.Path
            }
        }
    }
    
    $csvData | Export-Csv -Path $itemsCSV -NoTypeInformation -Encoding UTF8
    Write-Host "Exported detailed data to: $itemsCSV" -ForegroundColor Green
    
    # Export summary statistics
    $summaryCSV = $BaseFileName -replace "\.json$", "_summary.csv"
    $Data.Summary | ConvertTo-Json | ConvertFrom-Json | Export-Csv -Path $summaryCSV -NoTypeInformation -Encoding UTF8
    Write-Host "Exported summary to: $summaryCSV" -ForegroundColor Green
}

# Main execution
Write-Host "Jellyfin Codec Analysis Results Viewer" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

if (-not (Test-Path $InputFile)) {
    Write-Error "Input file '$InputFile' not found. Please run jellyfin_codec_analyzer.ps1 first."
    exit 1
}

Write-Host "Loading analysis data from: $InputFile" -ForegroundColor Cyan

try {
    $analysisData = Get-Content -Path $InputFile -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-Error "Failed to load or parse JSON file: $($_.Exception.Message)"
    exit 1
}

Write-Host "Data loaded successfully!" -ForegroundColor Green
Write-Host "Analysis performed: $($analysisData.Summary.ProcessedAt)" -ForegroundColor Cyan

# Show basic summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Green
Write-Host "Total Items: $($analysisData.Summary.TotalItems)" -ForegroundColor White
Write-Host "Movies: $($analysisData.Summary.Movies)" -ForegroundColor White  
Write-Host "Series: $($analysisData.Summary.Series)" -ForegroundColor White
Write-Host "HDR Items: $($analysisData.Summary.HDRCount)" -ForegroundColor White
Write-Host "Dolby Vision Items: $($analysisData.Summary.DolbyVisionCount)" -ForegroundColor White

# Perform detailed analysis
$misdetections = Show-ResolutionAnalysis -Data $analysisData
Show-HDRAnalysis -Data $analysisData

if ($ShowCodecImages) {
    Show-CodecImageMapping -Data $analysisData
}

if ($ShowMisdetections -and $misdetections.Count -gt 0) {
    Write-Host "`n=== DETAILED MISDETECTIONS ===" -ForegroundColor Red
    $misdetections | ForEach-Object {
        Write-Host "`nItem: $($_.Name) ($($_.Type))" -ForegroundColor Yellow
        Write-Host "  Actual: $($_.ActualDimensions)" -ForegroundColor White
        Write-Host "  Expected: $($_.ExpectedResolution)" -ForegroundColor White  
        Write-Host "  Detected: $($_.DetectedResolution)" -ForegroundColor Red
        Write-Host "  Video Range: $($_.VideoRange)" -ForegroundColor Gray
        Write-Host "  Color Space: $($_.ColorSpace)" -ForegroundColor Gray
        Write-Host "  Codec: $($_.Codec)" -ForegroundColor Gray
    }
}

if ($ExportCSV) {
    Export-ToCSV -Data $analysisData -BaseFileName $InputFile
}

Write-Host "`nAnalysis complete!" -ForegroundColor Green
Write-Host "`nUsage examples:" -ForegroundColor Yellow
Write-Host "  .\scripts\analyze_codec_results.ps1 -ShowMisdetections" -ForegroundColor White
Write-Host "  .\scripts\analyze_codec_results.ps1 -ShowCodecImages" -ForegroundColor White
Write-Host "  .\scripts\analyze_codec_results.ps1 -ExportCSV" -ForegroundColor White
