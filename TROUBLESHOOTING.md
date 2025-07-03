# Batch Job Processing Troubleshooting Guide

## Issue: Batch jobs remain "queued" and never start processing

This guide helps diagnose and fix issues where batch jobs are created successfully but never begin processing.

## Quick Diagnosis

### Step 1: Check if the worker container is running

```bash
docker ps | grep aphrodite-worker
```

**Expected output:** You should see the `aphrodite-worker` container running.

**If not running:**
```bash
# Check worker logs
docker-compose logs aphrodite-worker

# Restart the worker
docker-compose restart aphrodite-worker
```

### Step 2: Check worker health

```bash
# Check worker container health
docker inspect aphrodite-worker | grep -A 10 "Health"

# Or check with docker-compose
docker-compose ps
```

**Expected output:** Worker should show as "healthy" or "starting".

### Step 3: Check Redis connectivity

```bash
# Test Redis from main container
docker-compose exec aphrodite python -c "
import redis
from app.core.config import get_settings
settings = get_settings()
client = redis.from_url(settings.celery_broker_url)
client.ping()
print('Redis connection OK')
"
```

**Expected output:** "Redis connection OK"

### Step 4: Check worker registration

```bash
# Run worker diagnostics
docker-compose exec aphrodite python celery_diagnostics.py
```

This will test:
- Redis connection
- Celery app configuration  
- Task registration
- Worker inspection
- Task dispatch

## Advanced Troubleshooting

### Debug Worker Startup

Use the debug configuration to see detailed worker startup logs:

```bash
# Stop the regular worker
docker-compose stop aphrodite-worker

# Start debug worker
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up aphrodite-worker-debug
```

Watch the output for any import errors or connection issues.

### Check Worker Logs in Detail

```bash
# Follow worker logs in real-time
docker-compose logs -f aphrodite-worker

# Check last 100 lines
docker-compose logs --tail=100 aphrodite-worker
```

Look for:
- Import errors
- Redis connection errors
- Task registration failures
- Memory or resource issues

### Manual Worker Health Check

```bash
# Test worker health script
docker-compose exec aphrodite-worker python worker_health.py
```

### Test Task Dispatch Manually

```bash
# Run comprehensive diagnostics
docker-compose exec aphrodite python -c "
import sys
sys.path.insert(0, '/app')
from celery_app import celery_app
from app.services.workflow.workers.batch_worker import process_batch_job

# Send test task
result = celery_app.send_task(
    'app.services.workflow.workers.batch_worker.process_batch_job',
    args=['test-job-123']
)
print(f'Task ID: {result.id}')
print(f'Task state: {result.state}')

# Check for active workers
inspector = celery_app.control.inspect()
active = inspector.active()
print(f'Active workers: {active}')
"
```

## Common Solutions

### Solution 1: Worker Not Starting

**Symptoms:** No worker container or constantly restarting worker

**Fix:**
```bash
# Check resource usage
docker stats

# Check worker container logs
docker-compose logs aphrodite-worker

# Restart with more resources if needed
docker-compose up aphrodite-worker --force-recreate
```

### Solution 2: Redis Connection Issues

**Symptoms:** Redis connection errors in logs

**Fix:**
```bash
# Check if Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis

# Wait for Redis to be healthy
docker-compose up --wait
```

### Solution 3: Task Registration Problems

**Symptoms:** Task not found in registered tasks

**Fix:**
```bash
# Use the robust worker startup
docker-compose stop aphrodite-worker
docker-compose up aphrodite-worker
```

### Solution 4: Import or Path Issues

**Symptoms:** Module import errors in worker logs

**Fix:**
```bash
# Recreate worker container
docker-compose stop aphrodite-worker
docker-compose rm -f aphrodite-worker
docker-compose up aphrodite-worker
```

### Solution 5: Complete Reset

If all else fails:

```bash
# Stop all services
docker-compose down

# Pull latest image
docker-compose pull

# Start fresh
docker-compose up -d

# Wait for all services to be healthy
docker-compose ps
```

## Verification

After applying fixes, verify batch jobs are working:

1. Create a new batch job in the Poster Manager
2. Check job status - should change from "queued" to "processing"
3. Monitor progress in the job details
4. Confirm job completes successfully

## Getting Help

If issues persist:

1. Collect logs:
   ```bash
   docker-compose logs > aphrodite-logs.txt
   ```

2. Check system resources:
   ```bash
   docker stats > docker-stats.txt
   ```

3. Run full diagnostics:
   ```bash
   docker-compose exec aphrodite python celery_diagnostics.py > diagnostics.txt
   ```

4. Share these files when reporting the issue.

## Prevention

To prevent future issues:

1. **Monitor worker health:** Regularly check `docker-compose ps`
2. **Check disk space:** Ensure sufficient disk space for logs and data
3. **Monitor memory:** Watch for memory leaks in long-running jobs
4. **Update regularly:** Keep Aphrodite updated to latest version
5. **Backup configuration:** Keep your `.env` and docker-compose settings backed up
