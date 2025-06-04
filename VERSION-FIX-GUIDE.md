# Aphrodite Version Fix - Troubleshooting Guide

## The Problem
- Docker compose shows `ghcr.io/jackkerouac/aphrodite:2.2.2`
- Web interface shows `v2.2.0`
- Version mismatch causing confusion

## Root Causes
1. **Docker Image Cache**: Old images cached locally
2. **Browser Cache**: Frontend cached with old version info
3. **Config Mismatch**: docker-compose.yml was using `:latest` instead of `:2.2.2`
4. **Multiple Compose Files**: Development vs Production confusion

## Complete Solution Applied

### 1. Fixed docker-compose.yml
```yaml
# BEFORE:
image: ghcr.io/jackkerouac/aphrodite:latest

# AFTER: 
image: ghcr.io/jackkerouac/aphrodite:2.2.2
```

### 2. Created Automated Fix Scripts
- **`complete-fix.bat`** - Windows complete cleanup and restart
- **`update-aphrodite.bat`** - Future update script
- **`check-version.bat`** - Quick version verification

### 3. Updated Frontend Version Checker
- Fixed hardcoded fallback version: `1.4.8` → `2.2.2`
- Added cache-busting to API calls
- Better error handling for version mismatches

## How to Use the Fix

### Method 1: Automated Script (Recommended)
```bash
# Run the complete fix
./complete-fix.bat

# Then CLEAR YOUR BROWSER CACHE
# Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
```

### Method 2: Manual Steps
```bash
# 1. Stop everything
docker compose down
docker compose -f docker-compose.dev.yml down

# 2. Clean up
docker container rm aphrodite aphrodite-dev
docker image rm ghcr.io/jackkerouac/aphrodite:latest
docker image rm ghcr.io/jackkerouac/aphrodite:2.2.0
docker system prune -f

# 3. Fresh pull
docker pull ghcr.io/jackkerouac/aphrodite:2.2.2

# 4. Start fresh
docker compose up -d

# 5. Clear browser cache
```

## Verification Steps

### 1. Check Docker Image
```bash
docker images | grep aphrodite
# Should show: ghcr.io/jackkerouac/aphrodite:2.2.2

docker inspect aphrodite --format="{{.Config.Image}}"
# Should show: ghcr.io/jackkerouac/aphrodite:2.2.2
```

### 2. Check Container Version
```bash
docker exec aphrodite cat /app/version.yml
# Should show: version: 2.2.2
```

### 3. Check API Response
```bash
curl http://localhost:2125/api/version/current
# Should show: {"current_version": "2.2.2", "success": true}
```

### 4. Check Web Interface
- Open http://localhost:2125
- Look at bottom of sidebar for version number
- Should show "v2.2.2"

## Browser Cache Issues

### Symptoms
- Docker shows 2.2.2 but web shows 2.2.0
- API returns 2.2.2 but UI doesn't update

### Solutions
1. **Hard Refresh**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. **Clear Cache**: Ctrl+Shift+Delete, select "Cached images and files"
3. **Private Mode**: Open in Incognito/Private window
4. **Developer Tools**: F12 → Network tab → "Disable cache" checkbox

## Future Updates

### Use the Update Script
```bash
# Edit docker-compose.yml to new version first
# Then run:
./update-aphrodite.bat
```

### Manual Version Updates
1. Edit `docker-compose.yml`: `image: ghcr.io/jackkerouac/aphrodite:X.X.X`
2. Edit `version.yml`: `version: X.X.X`
3. Edit `VersionChecker.vue`: `currentVersion: 'X.X.X'`
4. Run fix script

## Development vs Production

### Production (Docker Hub Image)
- Use `docker-compose.yml` 
- Image: `ghcr.io/jackkerouac/aphrodite:2.2.2`
- For stable releases

### Development (Local Build)
- Use `docker-compose.dev.yml`
- Builds from local source code
- For development/testing

### Which Should You Use?
- **Production users**: Use `docker-compose.yml` with specific version tags
- **Developers**: Use `docker-compose.dev.yml` for local changes
- **Never mix them**: Pick one approach and stick with it

## Common Mistakes to Avoid

1. **Using `:latest` tag** - Always use specific versions
2. **Mixing dev/prod** - Don't switch between compose files
3. **Ignoring browser cache** - Always clear cache after updates
4. **Not verifying** - Always check all three: Docker, API, Web UI

## Files Modified

- ✅ `docker-compose.yml` - Fixed image tag
- ✅ `complete-fix.bat` - Complete cleanup script
- ✅ `update-aphrodite.bat` - Future update script  
- ✅ `check-version.bat` - Version verification
- ✅ `VersionChecker.vue` - Fixed frontend version handling

---

**This fix should permanently resolve version mismatch issues!**
