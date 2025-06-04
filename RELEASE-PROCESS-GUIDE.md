# Aphrodite Release Process Guide

## The Problem We Solved

**Before**: Version mismatches where Docker images tagged as `2.2.2` would show `v2.2.0` in the web interface because:
- Dockerfile hardcoded fallback version to 2.2.0
- GitHub workflow didn't pass version info to Docker build
- Multiple version files weren't synchronized
- End users got inconsistent versions

**After**: Automatic version synchronization from GitHub release tags to all components.

## Fixed Components

### 1. Dockerfile ✅
- Now accepts `VERSION` build argument
- Creates correct version.yml during build
- Falls back to 2.2.2 if no version provided

### 2. GitHub Workflow ✅  
- Extracts version from release tag
- Passes version to Docker build as build argument
- Supports both releases and development builds

### 3. Version Management Script ✅
- `update_version.py` updates all version files consistently
- Updates YAML files and Vue component
- Provides checklist for complete releases

## How End Users Are Affected

### Before These Fixes:
- Downloaded `ghcr.io/jackkerouac/aphrodite:2.2.2`
- Web interface showed `v2.2.0` 
- Confusion about actual version

### After These Fixes:
- Download `ghcr.io/jackkerouac/aphrodite:2.2.2`
- Web interface shows `v2.2.2`
- Perfect version consistency

## Release Process for Maintainers

### Step 1: Prepare Release
```bash
# Update all version files
python update_version.py 2.2.3

# Update docker-compose.yml manually
# Change: image: ghcr.io/jackkerouac/aphrodite:2.2.3

# Commit changes
git add .
git commit -m "Release v2.2.3"
git push
```

### Step 2: Create GitHub Release  
1. Go to GitHub → Releases → Create Release
2. Tag: `v2.2.3`
3. Title: `Aphrodite v2.2.3`
4. Generate release notes
5. Publish release

### Step 3: Automatic Docker Build
- GitHub workflow automatically triggers
- Extracts version `2.2.3` from tag `v2.2.3`
- Builds Docker image with correct version
- Publishes as `ghcr.io/jackkerouac/aphrodite:2.2.3`

### Step 4: Verification
```bash
# Check the published image
docker pull ghcr.io/jackkerouac/aphrodite:2.2.3
docker run --rm ghcr.io/jackkerouac/aphrodite:2.2.3 cat /app/version.yml
# Should show: version: 2.2.3
```

## File Structure

```
aphrodite/
├── version.yml                    # Main version file (copied to Docker)
├── config/version.yml             # Config version file  
├── docker-compose.yml             # Update image tag manually
├── Dockerfile                     # ✅ Fixed: Accepts VERSION build arg
├── .github/workflows/
│   └── docker-publish.yml         # ✅ Fixed: Passes version to build
├── aphrodite-web/frontend/src/components/
│   └── VersionChecker.vue         # ✅ Fixed: Updated by script
└── update_version.py              # ✅ New: Version management script
```

## For End Users

### Current Docker Compose
```yaml
services:
  aphrodite:
    image: ghcr.io/jackkerouac/aphrodite:2.2.2  # Use specific versions
    # ... rest of config
```

### How to Update
```bash
# Edit docker-compose.yml image tag to new version
# Then:
docker compose pull
docker compose up -d
```

### Verification After Update
```bash
# Check container version
docker exec aphrodite cat /app/version.yml

# Check web interface version  
curl http://localhost:2125/api/version/current

# Both should show the same version!
```

## Development vs Production

### Development Builds (from main branch)
- Version: `dev-<git-sha>`
- Image: `ghcr.io/jackkerouac/aphrodite:main`
- For testing unreleased features

### Release Builds (from tags)
- Version: `2.2.2` (extracted from `v2.2.2` tag)
- Image: `ghcr.io/jackkerouac/aphrodite:2.2.2`
- For production use

## Rollback Strategy

### If a Release Has Issues:
1. **Remove the GitHub release** (this stops new downloads)
2. **Users can rollback** by changing docker-compose.yml to previous version:
   ```yaml
   image: ghcr.io/jackkerouac/aphrodite:2.2.1  # Previous working version
   ```
3. **Fix issues and re-release** with incremented version

## Testing New Releases

### Before Publishing:
```bash
# Test local build with version
docker build --build-arg VERSION=2.2.3 -t test-aphrodite .
docker run --rm test-aphrodite cat /app/version.yml
# Should show: version: 2.2.3

# Test web interface
docker run -p 2125:5000 test-aphrodite
# Visit http://localhost:2125 and check version in UI
```

## Benefits of This Fix

### For End Users:
- ✅ Consistent version display across all interfaces
- ✅ Clear understanding of what version they're running
- ✅ Proper update notifications work correctly
- ✅ No more confusion about version mismatches

### For Maintainers:  
- ✅ Automated version management in Docker builds
- ✅ Single script updates all version files
- ✅ Clear release process with verification steps
- ✅ Reliable version tracking for support/debugging

### For the Project:
- ✅ Professional release management
- ✅ User trust through consistent versioning  
- ✅ Easier debugging when users report issues
- ✅ Foundation for automatic update notifications

---

**This fix ensures that every end user gets exactly the version they expect, with perfect consistency between Docker tags and web interface display.**
