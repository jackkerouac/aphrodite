# Aphrodite Local Development Guide

## Local Build Process

For the easiest local development experience, use the provided build scripts:

```
# On Windows
local-build.bat

# On Linux/Mac
./local-build.sh
```

These scripts handle:
1. Building the Next.js frontend
2. Stopping any running containers
3. Building Docker images
4. Starting containers without rebuilding

## Manual Build Process

If you prefer to run the steps manually:

1. Build the Next.js frontend:
   ```
   cd frontend
   npm run build
   cd ..
   ```

2. Stop any running containers:
   ```
   docker-compose -f docker-compose.local.yml down
   ```

3. Build the Docker images:
   ```
   docker-compose -f docker-compose.local.yml build
   ```

4. Start the containers:
   ```
   docker-compose -f docker-compose.local.yml up -d --no-build
   ```

## Common Issues

### Double Building Issue

**Problem**: Docker Compose builds the image twice - once during `docker-compose build` and once during `docker-compose up`.

**Solution**: We've addressed this by:
1. Adding the `--no-build` flag with `docker-compose up` to prevent rebuilding
2. Using proper shutdown before rebuilding to ensure clean state

### Frontend Not Available

**Problem**: After building, the API shows "Frontend build not available, API-only mode".

**Possible causes and solutions**:

1. **Modern Next.js App Router vs. Pages Router**: 
   - Next.js has changed its build output format in newer versions
   - We've updated the server to handle both the App Router and Pages Router formats

2. **Missing frontend build**:
   - Ensure you run `npm run build` in the frontend directory before building Docker
   - The frontend/.next directory must exist and contain the built files
   - Our build scripts handle this automatically

3. **Build structure issues**:
   - We now check for both `server/app/page.js` (App Router) and `server/pages/index.html` (Pages Router)
   - Enhanced logging helps identify what's being detected

### Checking Build Status

To check if the frontend was correctly included in the Docker image:

1. Log into the container:
   ```
   docker-compose -f docker-compose.local.yml exec aphrodite bash
   ```

2. Check if the frontend directory exists:
   ```
   ls -la /app/frontend/.next
   ```

3. Check the application logs:
   ```
   docker-compose -f docker-compose.local.yml logs aphrodite
   ```

### Next.js App Router Special Considerations

Modern Next.js (version 13+) uses the App Router by default. This means:

1. Files are in `/frontend/.next/server/app/` rather than `/frontend/.next/server/pages/`
2. The server serves JavaScript files rather than HTML files
3. We now use a custom HTML wrapper to load the necessary JavaScript files

## Environment Variables

If you're encountering issues, check that your environment variables are correctly set. You may need to create a `.env` file in the project root with appropriate settings.
