# API Settings Module - Testing Guide

This document provides instructions for testing the API Settings module in Aphrodite UI.

## Prerequisites

1. PostgreSQL database is running
2. Database tables have been created (using `npm run setup-db`)
3. Backend server is running (using `npm run server`)
4. Frontend dev server is running (using `npm run dev`)

## Test Flow - Current Implementation

### Jellyfin Connection

1. Navigate to Settings > API Settings
2. In the Jellyfin Connection card:
   - Enter a Jellyfin URL (e.g., http://jellyfin.local:8096)
   - Enter a Jellyfin API key
   - Enter a Jellyfin user ID
3. Click "Save Settings" - you should see a success toast
4. Click "Test Connection" - if successful, you'll see a success toast with server info

## Testing Error Handling

To test error handling:

1. Enter an invalid API key or URL
2. Click "Test Connection"
3. You should see an error toast with details about the failure

## Database Verification

You can verify that settings are being saved correctly by checking the database:

```sql
-- Connect to the database
\c aphrodite

-- Check Jellyfin settings
SELECT * FROM jellyfin_settings;
```

## UI Features to Verify

- API key visibility toggling (show/hide)
- Visual feedback during save/test operations
- Responsive layout (test on different screen sizes)
- Error handling for invalid inputs
- Data persistence (settings should load when returning to the page)

## Future Implementations

The following API integrations are planned for future updates:

1. **OMDB API**
2. **TMDB API**
3. **TVDB API**

Currently, these APIs have placeholder cards in the UI indicating they will be available in future updates.

## Database Setup Verification

To verify that the database setup script works correctly:

1. Run the setup script:
```bash
npm run setup-db
```

2. Connect to your PostgreSQL database:
```bash
psql -U your_username -d aphrodite
```

3. Verify the tables exist:
```sql
\dt
```

You should see the following tables:
- users
- jellyfin_settings
- omdb_settings (will be used in future updates)
- tmdb_settings (will be used in future updates)
- tvdb_settings (will be used in future updates)

## Known Issues

- The placeholder API cards don't actually connect to any database tables yet
