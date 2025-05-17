@echo off
REM Script to build and push Docker images for Aphrodite

REM Configuration
set IMAGE_NAME=aphrodite
for /f "tokens=*" %%i in ('findstr /r "VERSION\s*=\s*['\"]v[^'\"]*" aphrodite.py ^| find "="') do (
    for /f "tokens=2 delims=v'\"" %%a in ("%%i") do (
        set VERSION=%%a
    )
)
if "%VERSION%"=="" set VERSION=0.1.0
set GITHUB_REPO=

echo Building Aphrodite Docker image v%VERSION%

REM Build the image
echo Building Docker image: %IMAGE_NAME%:%VERSION%
docker build -t %IMAGE_NAME%:%VERSION% -t %IMAGE_NAME%:latest .

REM Check if build was successful
if %ERRORLEVEL% neq 0 (
    echo Failed to build Docker image
    exit /b 1
)

echo Successfully built Docker image: %IMAGE_NAME%:%VERSION%

REM Ask if we should push to GitHub Container Registry
if not "%GITHUB_REPO%"=="" (
    set /p REPLY="Do you want to push to GitHub Container Registry? (y/n) "
    if /i "%REPLY%"=="y" (
        REM Tag for GitHub Container Registry
        set GITHUB_IMAGE=ghcr.io/%GITHUB_REPO%/%IMAGE_NAME%
        echo Tagging for GitHub Container Registry: %GITHUB_IMAGE%:%VERSION%
        docker tag %IMAGE_NAME%:%VERSION% %GITHUB_IMAGE%:%VERSION%
        docker tag %IMAGE_NAME%:%VERSION% %GITHUB_IMAGE%:latest
        
        echo Pushing to GitHub Container Registry
        docker push %GITHUB_IMAGE%:%VERSION%
        docker push %GITHUB_IMAGE%:latest
        
        echo Successfully pushed to GitHub Container Registry
    )
) else (
    echo No GitHub repository configured. Skipping push.
    echo To enable pushing to GitHub Container Registry, edit this script and add your GitHub username/repo.
)

echo Docker image build complete: %IMAGE_NAME%:%VERSION%
echo You can now run it with: docker run -p 5000:5000 %IMAGE_NAME%:latest
