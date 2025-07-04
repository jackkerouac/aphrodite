# Fresh Aphrodite Setup Guide (PowerShell)

## 🚀 Complete Reset and Fresh Install

### Step 1: Reset Environment
```powershell
# Run the reset script
.\reset-dev-environment.ps1

# Optional: Force rebuild Docker images
docker rmi aphrodite-api aphrodite-frontend aphrodite-worker 2>$null
docker image prune -f
```

### Step 2: Configure Environment Variables
Create/edit `.env` file:
```bash
# Database (these will create fresh containers)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aphrodite
POSTGRES_USER=aphrodite
POSTGRES_PASSWORD=aphrodite123

# Redis
REDIS_URL=redis://localhost:6379/0

# Jellyfin (configure to match your setup or user's setup)
JELLYFIN_URL=http://your-jellyfin-server:8096
JELLYFIN_API_KEY=your-api-key-here
JELLYFIN_USER_ID=your-user-id-here

# Development
DEBUG=true
ENVIRONMENT=development
```

### Step 3: Start Fresh Containers
```powershell
# Build and start everything
docker-compose up --build

# Watch the logs for:
# ✅ Database migrations running
# ✅ Tables being created
# ✅ Redis connection established
# ✅ Frontend build completing
```

### Step 4: Verify Fresh Install
```powershell
# Check containers are running
docker-compose ps

# Check database is empty (should show empty tables)
docker-compose exec postgres psql -U aphrodite -d aphrodite -c "\dt"

# Check logs for any errors
docker-compose logs api
docker-compose logs worker
```

### Step 5: Access Fresh Installation
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (aphrodite/aphrodite123)

## 🔍 Replicating User Issues

### Scenario 1: Invalid Jellyfin Configuration
```powershell
# Test with wrong Jellyfin URL
$env:JELLYFIN_URL="http://invalid-server:8096"
docker-compose restart api worker
```

### Scenario 2: Invalid API Key
```powershell
# Test with wrong API key
$env:JELLYFIN_API_KEY="invalid-key"
docker-compose restart api worker
```

### Scenario 3: Missing/Deleted Items
1. Set up Jellyfin connection properly
2. Create a batch job with poster IDs
3. Delete some items from Jellyfin
4. Run the batch job → should get HTTP 404 errors

### Scenario 4: Network Issues
```powershell
# Test with unreachable Jellyfin server
$env:JELLYFIN_URL="http://192.168.999.999:8096"
docker-compose restart api worker
```

## 🛠️ Testing the Diagnostics Tool

### Test Fresh Diagnostics
1. Go to http://localhost:3000/diagnostics
2. Test all tabs:
   - **Connection**: Should show your Jellyfin status
   - **Configuration**: Should show loaded settings
   - **Media Tests**: Should test sample items
   - **Batch Jobs**: Should show "No failed jobs" initially
   - **Custom ID Test**: Test specific Jellyfin IDs

### Create Test Batch Job Failures
1. Go to Poster Manager
2. Select 2+ posters
3. Create batch job
4. If working properly, diagnose any failures using the new tool

## 📊 Monitoring Fresh Install

### Check Database Content
```powershell
# Connect to database
docker-compose exec postgres psql -U aphrodite -d aphrodite

# Check tables exist
\dt

# Check system config
SELECT key, value FROM system_config;

# Check batch jobs
SELECT id, status, total_posters, failed_posters FROM batch_jobs;
```

### Check Redis
```powershell
# Connect to Redis
docker-compose exec redis redis-cli

# Check for any data
KEYS *
```

### Check Logs in Real-time
```powershell
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f api
docker-compose logs -f worker
```

## 🐛 Common Fresh Install Issues

### Database Connection Fails
```powershell
# Check if postgres container is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Manual connection test
docker-compose exec postgres psql -U aphrodite -d aphrodite -c "SELECT 1"
```

### Jellyfin Connection Fails
1. Verify Jellyfin URL is accessible: `curl http://your-jellyfin:8096/System/Info`
2. Test API key in browser: `http://your-jellyfin:8096/System/Info?api_key=your-key`
3. Use Diagnostics tool to test connection

### Worker Not Processing
```powershell
# Check Celery worker logs
docker-compose logs worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

This gives you a complete fresh start to replicate user issues!
