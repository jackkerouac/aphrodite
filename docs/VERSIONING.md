# Aphrodite Versioning System

## Overview

Aphrodite v2 implements a comprehensive versioning system that:
- Tracks the current application version from multiple sources
- Checks GitHub releases for updates 
- Compares versions using semantic versioning
- Displays version information and update availability in the About page

## Current Implementation Status

### ✅ **Implemented Components**

1. **VERSION File** (`/VERSION`)
   - Central source of truth for current version
   - Currently set to `2.0.0`

2. **VersionManager Class** (`/api/app/utils/version_manager.py`)
   - Handles version detection from multiple sources
   - Integrates with GitHub releases API
   - Compares versions using semantic versioning
   - Provides comprehensive error handling

3. **Updated API Endpoints** (`/api/app/routes/system.py`)
   - `/api/v1/system/info` - Returns current version information
   - `/api/v1/system/check-updates` - Checks GitHub for updates

4. **Frontend Integration** 
   - About page properly displays version information
   - "Check Updates" button triggers GitHub API calls
   - Update notifications shown when available

### ⚠️ **Current Limitations**

1. **GitHub Repository Status**
   - The repository `jackkerouac/aphrodite` may not have releases yet
   - API will return "no releases found" until first release is published

2. **Database Version Tracking**
   - No automatic database schema versioning yet
   - Manual tracking in `system_config` table possible but not automated

## Version Detection Hierarchy

The system checks for version information in this order:

1. **VERSION file** (`/VERSION`) - Primary source
2. **Environment variable** (`APHRODITE_VERSION`)
3. **Package metadata** (if installed via pip)
4. **Fallback** (`2.0.0-dev`)

## GitHub Integration

### API Endpoint
- **URL**: `https://api.github.com/repos/jackkerouac/aphrodite/releases/latest`
- **Rate Limit**: 60 requests/hour for unauthenticated requests
- **Timeout**: 10 seconds

### Version Comparison Logic
- Uses `packaging.version` for semantic versioning
- Handles development versions (`2.0.0-dev` → `2.0.0.dev0`)
- Strips `v` prefixes from tags
- Returns `False` if version parsing fails (safe fallback)

### Example API Response
```json
{
  "success": true,
  "update_available": true,
  "current_version": "2.0.0",
  "latest_version": "2.1.0", 
  "message": "Update available: v2.1.0",
  "release_notes_url": "https://github.com/jackkerouac/aphrodite/releases/tag/v2.1.0"
}
```

## Testing the System

### Prerequisites
```bash
# Install required dependencies
pip install requests packaging
```

### Run Test Script
```bash
cd /path/to/aphrodite
python test_versioning.py
```

### Manual Testing
1. Start the API server: `uvicorn app.main:app --reload`
2. Open the frontend: `npm run dev`
3. Navigate to `/about`
4. Click "Check Updates" button
5. Verify version information displays correctly

## Expected Behavior by Scenario

### Scenario 1: No GitHub Releases
- **Current**: `2.0.0`
- **Latest**: N/A
- **Message**: "No releases found in repository"
- **Update Available**: `false`

### Scenario 2: Up to Date
- **Current**: `2.1.0`
- **Latest**: `2.1.0`
- **Message**: "You are running the latest version!"
- **Update Available**: `false`

### Scenario 3: Update Available
- **Current**: `2.0.0`
- **Latest**: `2.1.0`
- **Message**: "Update available: v2.1.0"
- **Update Available**: `true`

### Scenario 4: Development Version
- **Current**: `2.0.0-dev`
- **Latest**: `2.0.0`
- **Message**: "Update available: v2.0.0"
- **Update Available**: `true`

### Scenario 5: GitHub API Error
- **Current**: `2.0.0`
- **Latest**: N/A
- **Message**: "Failed to check for updates: Cannot connect to GitHub"
- **Update Available**: `false`

## Database Integration (Future)

To add database version tracking:

```sql
-- Add to system_config table
INSERT INTO system_config (key, value) 
VALUES ('app_version', '{
  "version": "2.0.0",
  "updated_at": "2025-06-19T23:00:00Z",
  "update_method": "manual",
  "schema_version": "1.0.0"
}');
```

## File Structure

```
aphrodite/
├── VERSION                              # Version source file
├── api/
│   ├── app/
│   │   ├── utils/
│   │   │   └── version_manager.py      # Version management logic
│   │   └── routes/
│   │       └── system.py               # Updated API endpoints
│   └── requirements.txt                # Added packaging dependency
├── frontend/
│   ├── package.json                    # Updated to v2.0.0
│   └── src/components/about/           # Frontend About page components
└── test_versioning.py                  # Testing script
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'packaging'**
   ```bash
   pip install packaging
   ```

2. **GitHub API Rate Limit**
   - Wait 1 hour for rate limit reset
   - Consider adding GitHub token for higher limits

3. **Version Not Updating**
   - Check VERSION file exists and is readable
   - Verify APHRODITE_VERSION environment variable
   - Restart API server after changes

### Debug Information

The version manager logs detailed information:
- Version source detection
- GitHub API responses  
- Version comparison results
- Error conditions

Check logs for troubleshooting version-related issues.

## Future Enhancements

1. **Automatic Updates**
   - Download and install updates automatically
   - Backup current version before updates

2. **Release Channels**
   - Stable, beta, and development channels
   - User-configurable update preferences

3. **Database Schema Versioning**
   - Track database schema versions
   - Automatic migration on updates

4. **Update Notifications**
   - Email/webhook notifications for updates
   - Dashboard alerts for administrators

## Security Considerations

1. **GitHub API Rate Limits**
   - Implement caching for release information
   - Add exponential backoff for failed requests

2. **Update Verification**
   - Verify release signatures (future)
   - Checksum validation for downloads

3. **Fallback Behavior**
   - Graceful degradation when GitHub is unavailable
   - Safe defaults for version comparison failures
