@echo off
REM Windows Frontend Build Script for Docker
REM Handles permission issues with Tailwind CSS native modules

echo [INFO] Starting Windows-compatible frontend build...

cd /d "%~dp0"

echo [INFO] Current directory: %CD%

REM Clean node_modules if it exists and is problematic
if exist "node_modules" (
    echo [INFO] Removing existing node_modules...
    rmdir /s /q "node_modules" 2>nul
    if exist "node_modules" (
        echo [WARNING] Could not remove node_modules completely, trying alternative approach...
        timeout /t 2 /nobreak >nul
        rmdir /s /q "node_modules" 2>nul
    )
)

REM Clean package-lock.json to force fresh install
if exist "package-lock.json" (
    echo [INFO] Removing package-lock.json for fresh install...
    del "package-lock.json"
)

REM Clean .next directory for fresh build
if exist ".next" (
    echo [INFO] Cleaning existing build...
    rmdir /s /q ".next" 2>nul
)

echo [INFO] Installing dependencies with npm install...
npm install --no-package-lock --legacy-peer-deps

if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm install failed
    exit /b 1
)

echo [INFO] Building frontend for Docker...
npm run build:docker

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend build failed
    exit /b 1
)

echo [SUCCESS] Frontend build completed successfully!

REM Verify build output
if exist ".next" (
    echo [SUCCESS] Build directory .next exists
    dir .next
) else (
    echo [ERROR] Build directory .next not found
    exit /b 1
)

echo [INFO] Frontend is ready for Docker deployment
