# Script Cleanup Analysis (PowerShell)
# Analyzes all scripts in the scripts directory and categorizes them

Write-Host "📋 Analyzing scripts in the scripts directory..." -ForegroundColor Cyan
Write-Host ""

# Development scripts we just created (KEEP THESE)
$developmentScripts = @(
    "dev-setup.ps1",
    "test.ps1", 
    "reset-db.ps1",
    "build.ps1",
    "clean.ps1",
    "validate-setup.ps1",
    # Bash versions (can be deleted since you use PowerShell)
    "dev-setup.sh",
    "test.sh",
    "reset-db.sh", 
    "build.sh",
    "clean.sh",
    "validate-setup.sh",
    "make-executable.sh"
)

# Essential existing scripts (PROBABLY KEEP)
$essentialScripts = @(
    "setup.ps1",           # Existing setup script
    "manage.ps1",          # Management script
    "integration-test.sh"  # Integration testing
)

# Scripts that look like they're for specific debugging/fixes (PROBABLY DELETE)
$debugFixScripts = @(
    "check_ahsoka_provider_ids.py",
    "check_current_review_settings.py", 
    "check_review_settings.py",
    "check_review_settings_direct.py",
    "debug_filtering.py",
    "debug_image_paths.py",
    "diagnose_db.py",
    "disable_myanimelist.py",
    "disable_myanimelist_fixed.py", 
    "disable_myanimelist_simple.py",
    "fix_pink_badge_issue.py",
    "fix_review_enablement.py",
    "fix_review_enablement_direct.py",
    "pink_badge_fix_summary.py",
    "test_and_fix_review_issues.py",
    "test_and_fix_review_issues_clean.py",
    "test_all_fixes.py",
    "test_basic_fixes.py",
    "test_badge_settings_loading.py",
    "test_components_direct.py",
    "test_coverage_fixed.py",
    "test_enhanced_integration.py",
    "test_enhanced_resolution.py",
    "test_enhanced_resolution_settings.py",
    "test_enhanced_resolution_standalone.py",
    "test_integration.py",
    "test_integration_verify.py",
    "test_performance.py",
    "test_postgresql_badge_settings.py",
    "test_resolution_api.py",
    "test_resolution_fix.py",
    "test_review_filtering.py",
    "test_review_fix.py",
    "test_review_sources_fixed.py",
    "update_settings_components.py"
)

# Scripts that might be useful for operations (REVIEW BEFORE DELETING)
$operationalScripts = @(
    "analyze_codec_results.ps1",
    "jellyfin_codec_analyzer.ps1",
    "jellyfin_codec_analyzer_robust.ps1", 
    "test_jellyfin_connection.ps1",
    "resolution_diagnostic.ps1",
    "force-cache-bust.ps1",
    "fix-dockerignore.ps1",
    "nuclear-dockerfile.ps1",
    "push-fixes.ps1"
)

# Documentation and summary files (REVIEW)
$docFiles = @(
    "integration_complete.md",
    "phase1_summary.md"
)

# Utility scripts (MIGHT KEEP)
$utilityScripts = @(
    "check_syntax.py",
    "quick_test.py",
    "setup.sh"  # Bash version of setup
)

# Get all files in scripts directory
$allFiles = Get-ChildItem "scripts" -File | Select-Object -ExpandProperty Name

Write-Host "🟢 DEVELOPMENT SCRIPTS (KEEP - Created for contributors):" -ForegroundColor Green
foreach ($script in $developmentScripts) {
    if ($script -in $allFiles) {
        Write-Host "   ✓ $script" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🟡 ESSENTIAL EXISTING SCRIPTS (PROBABLY KEEP):" -ForegroundColor Yellow  
foreach ($script in $essentialScripts) {
    if ($script -in $allFiles) {
        Write-Host "   ? $script" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🔧 OPERATIONAL SCRIPTS (REVIEW - May be useful):" -ForegroundColor Cyan
foreach ($script in $operationalScripts) {
    if ($script -in $allFiles) {
        Write-Host "   ? $script" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "📄 UTILITY SCRIPTS (REVIEW):" -ForegroundColor Magenta
foreach ($script in $utilityScripts) {
    if ($script -in $allFiles) {
        Write-Host "   ? $script" -ForegroundColor Magenta
    }
}

Write-Host ""
Write-Host "📋 DOCUMENTATION FILES (REVIEW):" -ForegroundColor Blue
foreach ($doc in $docFiles) {
    if ($doc -in $allFiles) {
        Write-Host "   ? $doc" -ForegroundColor Blue
    }
}

Write-Host ""
Write-Host "🔴 DEBUG/FIX SCRIPTS (PROBABLY DELETE - Look like one-time fixes):" -ForegroundColor Red
foreach ($script in $debugFixScripts) {
    if ($script -in $allFiles) {
        Write-Host "   ✗ $script" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 SUMMARY:" -ForegroundColor White
Write-Host "   Total files in scripts/: $($allFiles.Count)"
Write-Host "   Development scripts (keep): $($developmentScripts.Where({$_ -in $allFiles}).Count)"
Write-Host "   Debug/fix scripts (delete): $($debugFixScripts.Where({$_ -in $allFiles}).Count)"
Write-Host "   Review needed: $(($essentialScripts + $operationalScripts + $utilityScripts + $docFiles).Where({$_ -in $allFiles}).Count)"

Write-Host ""
Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host "   1. KEEP all development scripts (green) - these are for contributors"
Write-Host "   2. DELETE debug/fix scripts (red) - these look like one-time fixes"
Write-Host "   3. REVIEW operational scripts - some may be useful for maintenance"
Write-Host "   4. DELETE bash versions (.sh) since you use PowerShell"
Write-Host ""
Write-Host "🚨 IMPORTANT: Back up or commit before deleting anything!"