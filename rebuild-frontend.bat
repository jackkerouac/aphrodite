@echo off
REM Frontend Production Build Script for Windows
REM This script rebuilds the frontend with production settings to fix localhost hardcoding

echo 🔧 Rebuilding Aphrodite Frontend for Production...
echo    This will fix any hardcoded localhost URLs
echo.

REM Navigate to frontend directory
cd "%~dp0frontend"

echo 📋 Current build environment:
echo    NODE_ENV: %NODE_ENV%
echo    NEXT_PUBLIC_API_URL: %NEXT_PUBLIC_API_URL%
echo.

REM Clean previous build
echo 🧹 Cleaning previous build...
if exist .next rmdir /s /q .next
if exist out rmdir /s /q out
echo    ✅ Cleaned .next and out directories

REM Install dependencies if needed
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm ci
    echo    ✅ Dependencies installed
)

REM Build for production with correct environment
echo 🏗️ Building frontend for production...
echo    Using .env.production file with NEXT_PUBLIC_API_URL=

REM Explicitly set production environment
set NODE_ENV=production
set NEXT_PUBLIC_API_URL=

REM Build the application
npm run build

echo.
echo ✅ Frontend build complete!
echo.
echo 🔍 Next steps:
echo    1. Run verification: node ..\test-build-verification.js
echo    2. If verification passes, rebuild Docker container
echo    3. Test on remote machine

pause
