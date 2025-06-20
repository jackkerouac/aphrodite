# Aphrodite Docker Build Scripts

This directory contains modular scripts for building and releasing multi-platform Docker images for Aphrodite v2.

## 🎯 Overview

These scripts bypass the broken GitHub Actions workflow and provide a manual, reliable way to build and publish multi-platform Docker images.

## 📋 Scripts

### Core Scripts

- **`master-build.sh`** - Orchestrates the entire build and release process
- **`authenticate.sh`** - Handles Docker registry authentication
- **`build-multiplatform.sh`** - Builds and pushes multi-platform images
- **`verify-images.sh`** - Verifies built images are accessible and functional
- **`create-release.sh`** - Creates GitHub release with release notes
- **`attach-assets.sh`** - Attaches docker-compose.yml and .env.example to release
- **`test-installation.sh`** - Tests end-to-end installation process

## 🚀 Quick Start

### Prerequisites

1. **Docker with buildx support**
2. **GitHub CLI (gh)** for release creation
3. **Environment variables:**
   ```bash
   export GITHUB_TOKEN=your_github_personal_access_token
   export DOCKERHUB_TOKEN=your_dockerhub_access_token
   ```

### Run Complete Build Process

```bash
# Make scripts executable
chmod +x docker-build-scripts/*.sh

# Run the complete build and release process
./docker-build-scripts/master-build.sh
```

### Run Individual Steps

```bash
# 1. Authenticate with registries
./docker-build-scripts/authenticate.sh

# 2. Build and push images
./docker-build-scripts/build-multiplatform.sh

# 3. Verify images
./docker-build-scripts/verify-images.sh

# 4. Create GitHub release
./docker-build-scripts/create-release.sh

# 5. Attach release assets
./docker-build-scripts/attach-assets.sh

# 6. Test installation
./docker-build-scripts/test-installation.sh
```

## 🔧 Configuration

### Version Settings

The version is set to `v4.0.2` in all scripts. To change the version:

1. Edit the `VERSION` variable in each script
2. Ensure the version doesn't already exist as a Git tag

### Registry Settings

- **GitHub Container Registry:** `ghcr.io/jackkerouac/aphrodite`
- **Docker Hub:** `jackkerouac/aphrodite`

## 🎯 What Gets Built

### Platforms
- `linux/amd64` - Standard x86_64 systems
- `linux/arm64` - ARM-based systems (Apple Silicon, Raspberry Pi 4+)

### Image Tags
- `ghcr.io/jackkerouac/aphrodite:v4.0.2`
- `ghcr.io/jackkerouac/aphrodite:latest`
- `jackkerouac/aphrodite:v4.0.2`
- `jackkerouac/aphrodite:latest`

## 📋 Build Process

1. **Setup buildx builder** for multi-platform support
2. **Authenticate** with GitHub Container Registry and Docker Hub
3. **Build and push** images for both platforms simultaneously
4. **Verify** images are accessible and functional
5. **Create GitHub release** with comprehensive release notes
6. **Attach assets** (docker-compose.yml, .env.example)
7. **Test installation** end-to-end

## 🧪 Testing

The `test-installation.sh` script performs:
- Image pull tests from both registries
- docker-compose.yml validation
- Container startup and health check tests
- Complete cleanup

## 🔍 Troubleshooting

### Build Fails
- Ensure Docker has sufficient memory (8GB+)
- Clear Docker cache: `docker system prune -a`
- Check disk space availability

### Authentication Fails
- Verify tokens are valid and have proper permissions
- Check token expiration dates
- Ensure repositories exist and are accessible

### Registry Push Fails
- Verify network connectivity
- Check registry status
- Ensure sufficient storage quota

## ✅ Success Criteria

The build is successful when:
- ✅ Images build without errors for both platforms
- ✅ Images are pushed to both registries
- ✅ Images can be pulled and run by end users
- ✅ GitHub release is created with proper assets
- ✅ docker-compose.yml works with published images

## 📚 File Structure

```
docker-build-scripts/
├── README.md                 # This file
├── master-build.sh          # Main orchestration script
├── authenticate.sh          # Registry authentication
├── build-multiplatform.sh   # Multi-platform build and push
├── verify-images.sh         # Image verification
├── create-release.sh        # GitHub release creation
├── attach-assets.sh         # Release asset attachment
└── test-installation.sh     # End-to-end testing
```

## 🎉 Expected Output

After successful completion:
- Multi-platform Docker images available on both registries
- GitHub release v4.0.2 with release notes and assets
- Verified functionality across platforms
- Ready-to-use installation instructions for users

---

**Created:** 2025-06-20  
**Purpose:** Manual multi-platform Docker build for Aphrodite v2  
**Status:** Production Ready
