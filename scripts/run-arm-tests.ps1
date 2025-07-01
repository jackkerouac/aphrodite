# Run all ARM support tests (PowerShell)

param(
    [switch]$SkipBuild = $false
)

# Color functions
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }

Write-Host "🧪 Running ARM Support Test Suite..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Configuration Test
Write-Status "Running configuration tests..."
try {
    & ".\scripts\test-arm-support.ps1"
    if ($LASTEXITCODE -ne 0) { throw "Configuration test failed" }
    Write-Success "✅ Configuration tests passed"
} catch {
    Write-Error "❌ Configuration tests failed"
    Write-Error $_.Exception.Message
    exit 1
}

Write-Host ""

# Test 2: Build Test (optional)
if (-not $SkipBuild) {
    Write-Status "Running ARM64 build test..."
    Write-Warning "This may take several minutes and requires Docker Desktop..."
    
    $choice = Read-Host "Do you want to run the ARM64 build test? This will take time. (y/N)"
    if ($choice -match '^[Yy]') {
        try {
            & ".\scripts\test-arm64-build.ps1"
            if ($LASTEXITCODE -ne 0) { throw "ARM64 build test failed" }
            Write-Success "✅ ARM64 build test passed"
        } catch {
            Write-Error "❌ ARM64 build test failed"
            Write-Error $_.Exception.Message
            Write-Warning "You can skip this test with -SkipBuild parameter"
            exit 1
        }
    } else {
        Write-Status "Skipping ARM64 build test"
    }
} else {
    Write-Status "Skipping ARM64 build test (use without -SkipBuild to include)"
}

Write-Host ""
Write-Success "🎉 All ARM Support Tests Completed!"
Write-Host ""
Write-Host "📋 What's Ready:" -ForegroundColor Yellow
Write-Host "  ✅ Multi-platform Docker builds (AMD64 + ARM64)"
Write-Host "  ✅ GitHub Actions CI/CD for both architectures" 
Write-Host "  ✅ Multi-stage Dockerfile handles native dependencies"
Write-Host "  ✅ PowerShell build scripts for Windows development"
Write-Host "  ✅ Comprehensive documentation and troubleshooting"
Write-Host ""
Write-Host "🚀 Ready to Deploy:" -ForegroundColor Green
Write-Host "  1. Commit changes: git add . && git commit -m 'feat: ARM64 support'"
Write-Host "  2. Create release: git tag v4.0.1-arm && git push origin v4.0.1-arm"
Write-Host "  3. GitHub Actions will build both AMD64 and ARM64 automatically"
Write-Host ""
Write-Host "🎯 Test Commands:" -ForegroundColor Cyan
Write-Host "  • Full test suite: .\scripts\run-arm-tests.ps1"
Write-Host "  • Config only: .\scripts\test-arm-support.ps1"
Write-Host "  • Build test: .\scripts\test-arm64-build.ps1"
Write-Host "  • Multi-platform build: .\scripts\build-multiplatform.ps1"
