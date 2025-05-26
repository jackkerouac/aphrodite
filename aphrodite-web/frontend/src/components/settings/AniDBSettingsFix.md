# Fix for AniDB Settings Not Loading

## Issue

The AniDB username, password, and client_name are not being loaded correctly from the settings.yaml file in the Settings page.

## Root Cause

The issue is in the `loadSettings` function in the `ApiSettings.vue` component. The code expects the AniDB settings to be in an array format (`config.api_keys.aniDB.length > 0`), but the backend might be returning it as a single object if it was already processed.

## Fix

Update the `loadSettings` function in `ApiSettings.vue` to handle both formats:

1. Check if `config.api_keys.aniDB` exists first (without checking length)
2. Examine if it's an array or object
3. Handle both formats appropriately

## Implementation

Replace the AniDB settings loading section with the code in `ApiSettings.loadSettings.fixed.js`.

The key difference is:

```javascript
// Old code - only handles array format
if (config.api_keys.aniDB && config.api_keys.aniDB.length > 0) {
  // ...
}

// New code - handles both array and object formats
if (config.api_keys.aniDB) {
  const anidbConfig = config.api_keys.aniDB;
  
  if (Array.isArray(anidbConfig)) {
    // Handle array format
    // ...
  } else if (typeof anidbConfig === 'object') {
    // Handle object format
    // ...
  }
}
```

After applying this fix, the AniDB settings (username, password, version, client_name) should load correctly in the Settings page.
