# Enhanced Batch Processing Debug Logging

This system provides comprehensive debugging capabilities for batch processing jobs that are experiencing failures, particularly with Jellyfin poster downloads.

## Overview

The Enhanced Batch Debug Logging Package helps diagnose issues with batch processing by providing:

- **Comprehensive session tracking** - Monitor HTTP session creation and reuse
- **Request/response analysis** - Log detailed information about each Jellyfin API call
- **Environment detection** - Identify Jellyfin server characteristics that affect batch processing
- **Performance metrics** - Track success rates, timing, and failure patterns
- **Actionable recommendations** - Generate specific suggestions based on observed patterns

## How It Works

### 1. Debug Logger Integration

The `BatchDebugLogger` class is integrated into:
- **Batch Worker** (`batch_worker.py`) - Tracks job-level metrics
- **Poster Processor** (`poster_processor.py`) - Logs individual poster processing
- **Jellyfin Service** (`jellyfin_service.py`) - Monitors HTTP requests and responses

### 2. Enable/Disable Control

Debug logging can be controlled via:
- **Environment Variable**: `APHRODITE_BATCH_DEBUG=true`
- **API Endpoints**: `/api/v1/batch-debug/enable` and `/api/v1/batch-debug/disable`
- **Frontend UI**: Diagnostics page → Batch Debug tab

### 3. Data Collection

When enabled, the system logs:
- Session state before each request
- Request attempt details (retry count, timing)
- HTTP response status codes and headers
- Error messages and response bodies
- Performance metrics (success rate, duration)

## Quick Start Guide

### Step 1: Enable Debug Mode

**Via Frontend UI:**
1. Go to `/diagnostics` in your browser
2. Click the "Batch Debug" tab
3. Set duration (e.g., 30 minutes)
4. Click "Enable Debug Mode"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/batch-debug/enable \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 30}'
```

**Via Environment Variable:**
```bash
export APHRODITE_BATCH_DEBUG=true
# Restart the application
```

### Step 2: Run Your Failing Batch Job

1. Go to Poster Manager
2. Select the problematic posters (start with a small batch, 5-10 items)
3. Create and run a batch job
4. Let it complete (even if it fails)

### Step 3: Review Debug Information

**Via Frontend UI:**
1. Return to Diagnostics → Batch Debug tab
2. Look for your job in "Recent Debug Sessions"
3. Click "View Summary" to see analysis
4. Click "Download Full Log" for detailed information

**Via API:**
```bash
# Get debug status and recent files
curl http://localhost:8000/api/v1/batch-debug/status

# Get summary for specific job
curl http://localhost:8000/api/v1/batch-debug/job/{JOB_ID}/summary

# Download full debug log
curl http://localhost:8000/api/v1/batch-debug/job/{JOB_ID}/full-log
```

## Understanding Debug Output

### Performance Metrics

- **Success Rate** - Percentage of successful poster downloads
- **Total Requests** - Number of HTTP requests made to Jellyfin
- **Failed Requests** - Number of failed requests
- **Duration** - Total time spent processing

### Status Code Breakdown

Common status codes and their meanings:
- **200** - Success
- **400** - Bad Request (invalid poster ID or corrupted data)
- **401** - Unauthorized (API key issues)
- **404** - Not Found (poster doesn't exist)
- **429** - Rate Limited (too many requests)
- **503** - Service Unavailable (server overloaded)

### Failure Patterns

The system identifies common failure patterns:
- Invalid poster IDs
- Authentication issues
- Server overload
- Network connectivity problems

### Recommendations

Based on the analysis, the system provides specific recommendations:
- "Use individual processing mode for better reliability"
- "Increase request interval to reduce server load"
- "Check Jellyfin server logs for potential issues"
- "Verify poster IDs are valid"

## Troubleshooting Common Issues

### High Failure Rate (>50% failures)

**Likely Causes:**
- Invalid poster IDs in the batch
- Jellyfin server issues
- Network connectivity problems

**Recommended Actions:**
1. Check the "Failure Patterns" section for specific error codes
2. Test individual poster IDs using the "Custom ID Test" tab
3. Verify Jellyfin server is responding normally
4. Consider using individual processing mode

### HTTP 400 Errors

**Likely Causes:**
- Corrupted or invalid Jellyfin item IDs
- Items deleted from Jellyfin after selection

**Recommended Actions:**
1. Use the "Custom ID Test" to verify specific failing IDs
2. Check if items still exist in Jellyfin
3. Re-scan library to refresh item list
4. Remove problematic items from batch

### HTTP 401/403 Errors

**Likely Causes:**
- Invalid API key
- Expired authentication
- Insufficient permissions

**Recommended Actions:**
1. Check Jellyfin settings in Configuration tab
2. Verify API key is correct and has required permissions
3. Test connection using the "Connection" tab

### Session Management Issues

**Symptoms:**
- High number of session creation events
- Intermittent failures with working poster IDs

**Recommended Actions:**
1. The system will automatically recommend session strategy changes
2. Consider enabling "per-request" session strategy for problematic environments
3. Increase request intervals to reduce server load

## File Locations

### Debug Files
- **Location**: `E:/programming/aphrodite/api/debug_logs/batch_jobs/`
- **Format**: `job_{JOB_ID}_{TIMESTAMP}.json`
- **Content**: Complete debug data including session history, request timings, and analysis

### Configuration
- **Debug Logger**: `app/services/diagnostics/batch_debug_logger.py`
- **API Routes**: `app/routes/batch_debug.py`
- **Frontend Component**: `frontend/src/components/diagnostics/batch-debug-tab.tsx`

## API Reference

### Enable Debug Mode
```
POST /api/v1/batch-debug/enable
Content-Type: application/json

{
  "duration_minutes": 30
}
```

### Disable Debug Mode
```
POST /api/v1/batch-debug/disable
```

### Get Debug Status
```
GET /api/v1/batch-debug/status
```

### Get Job Debug Summary
```
GET /api/v1/batch-debug/job/{job_id}/summary
```

### Download Full Debug Log
```
GET /api/v1/batch-debug/job/{job_id}/full-log
```

### Cleanup Old Debug Files
```
DELETE /api/v1/batch-debug/cleanup?days=7
```

## Testing

### Run API Tests
```bash
cd /path/to/aphrodite/api
python test_batch_debug.py
```

This will test all debug API endpoints and verify the system is working correctly.

### Manual Testing
1. Enable debug mode
2. Create a small batch job (5-10 items)
3. Review the debug summary
4. Download and examine the full debug log

## Performance Impact

### When Debug Mode is Disabled
- **Zero overhead** - No performance impact when disabled
- **Minimal memory usage** - Debug logger objects are lightweight

### When Debug Mode is Enabled
- **Minor performance impact** - Additional logging adds ~5-10ms per request
- **Memory usage** - Stores debug data in memory during job execution
- **Disk usage** - Debug files are typically 10-100KB per job

### Automatic Cleanup
- Debug mode automatically disables after specified duration
- Old debug files can be cleaned up via API or UI
- Recommended to clean files older than 7 days regularly

## Advanced Configuration

### Environment Variables
- `APHRODITE_BATCH_DEBUG` - Enable/disable debug mode globally
- Debug duration and other settings controlled via API

### Database Settings
Future enhancement: Store user debug preferences in database for persistent settings.

### Custom Debug Levels
Currently supports on/off. Future versions may include different debug levels (basic, detailed, verbose).

## Integration with Other Diagnostics

This debug logging system works alongside:
- **Jellyfin Diagnostics** - Connection and configuration testing
- **Infrastructure Diagnostics** - Redis, Celery, and database testing
- **Media Tests** - Individual item testing
- **Batch Job Analysis** - Failed job investigation

Use these tools together for comprehensive troubleshooting of batch processing issues.

## Support

If you're still experiencing issues after using the debug logging:

1. **Collect Debug Information**:
   - Enable debug mode
   - Run a small test batch (5-10 items)
   - Download the full debug log
   - Note any specific error patterns

2. **Check System Components**:
   - Use Infrastructure Diagnostics to verify Redis, Celery, and database
   - Use Jellyfin Diagnostics to test connection and configuration
   - Use Media Tests to verify individual item processing

3. **Review Recommendations**:
   - Follow the specific recommendations generated by the debug analysis
   - Try suggested session strategies or request intervals
   - Consider using individual processing for problematic items

The enhanced debug logging system transforms batch processing issues from "it doesn't work" to "here's exactly what's wrong and how to fix it" by providing detailed, actionable diagnostic information.
