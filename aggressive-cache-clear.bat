@echo off
REM AGGRESSIVE FRONTEND CACHE CLEARING AND REBUILD
REM This script clears ALL caches and rebuilds from scratch

echo 🧹 AGGRESSIVE CACHE CLEARING FOR APHRODITE FRONTEND
echo ==================================================
echo.

REM Navigate to frontend directory
cd "%~dp0frontend"

echo 1️⃣ Removing ALL build artifacts...
if exist .next rmdir /s /q .next
if exist out rmdir /s /q out
if exist dist rmdir /s /q dist
echo    ✅ Removed .next, out, dist

echo.
echo 2️⃣ Clearing Node.js caches...
if exist node_modules\.cache rmdir /s /q node_modules\.cache
if exist .npm rmdir /s /q .npm
echo    ✅ Cleared Node.js caches

echo.
echo 3️⃣ Clearing TypeScript cache...
if exist .tsbuildinfo del .tsbuildinfo
if exist tsconfig.tsbuildinfo del tsconfig.tsbuildinfo
echo    ✅ Cleared TypeScript cache

echo.
echo 4️⃣ Verifying source code is correct...
findstr /c:"getApiBaseUrl" src\services\api.ts >nul
if errorlevel 1 (
    echo    ❌ ERROR: Source missing getApiBaseUrl function!
    pause
    exit /b 1
) else (
    echo    ✅ Source has getApiBaseUrl function
)

findstr /c:"window.location.origin" src\services\api.ts >nul
if errorlevel 1 (
    echo    ❌ ERROR: Source missing window.location.origin!
    pause
    exit /b 1
) else (
    echo    ✅ Source has window.location.origin logic
)

echo.
echo 5️⃣ Setting production environment...
set NODE_ENV=production
set NEXT_PUBLIC_API_URL=
echo    NODE_ENV: %NODE_ENV%
echo    NEXT_PUBLIC_API_URL: '%NEXT_PUBLIC_API_URL%'

echo.
echo 6️⃣ Installing fresh dependencies...
npm ci --prefer-offline=false
echo    ✅ Fresh dependencies installed

echo.
echo 7️⃣ Building with production settings...
npm run build

echo.
echo ✅ REBUILD COMPLETE!
echo.
echo 🔍 VERIFICATION STEPS:
echo 1. Run: node ..\test-build-verification.js
echo 2. Look for 'No hardcoded localhost:8000 found'
echo 3. Look for 'Found window.location.origin references'
echo.
echo If verification passes:
echo - Rebuild Docker container
echo - Test on remote machine
echo - Dashboard should show 'Online' status

pause
