# Aphrodite Badge Rendering Fixes

## Summary of Issues and Fixes

This document outlines the issues identified and fixed in the Aphrodite badge rendering system, particularly in the backend processing where badges are applied to media posters.

### Issues Fixed

1. **Missing RATING_LOGO_MAP Reference**
   - **Problem**: The backend `canvasBadgeRenderer.js` referenced `RATING_LOGO_MAP` and `RATING_BG_COLOR_MAP` which were not defined
   - **Fix**: Created `/backend/services/badge-renderer/utils/logoMapping.js` with proper mappings
   - **Impact**: Rating badges now correctly display logos and brand colors

2. **Case Sensitivity in Rating Names**
   - **Problem**: Rating source names had case sensitivity issues (e.g., "IMDb" vs "IMDB")
   - **Fix**: Added both case variations to the mapping files
   - **Impact**: Logos now load correctly regardless of case variations

3. **Audio Format Image Path Resolution**
   - **Problem**: Audio format "Dolby Digital" was failing to find the corresponding "digital.png" file
   - **Fix**: Improved normalization logic in `getAudioImagePath()` to handle various format names
   - **Impact**: Audio badges now correctly display images for various audio formats

4. **Badge Size Validation**
   - **Problem**: Badges could exceed poster dimensions causing "Image to composite must have same dimensions or smaller" errors
   - **Fix**: Added size validation before compositing badges onto posters
   - **Impact**: Badges are now safely skipped if they would exceed poster dimensions

5. **Font Fallback Handling**
   - **Problem**: Inter font not available in node-canvas environment caused warnings
   - **Fix**: Added `getFontFamily()` method with proper fallback chain
   - **Impact**: Text rendering now gracefully falls back to available fonts

6. **Resolution Case Sensitivity**
   - **Problem**: Resolution values like "4K" vs "4k" caused image loading failures
   - **Fix**: Added lowercase fallback mapping in `getResolutionImagePath()`
   - **Impact**: Resolution badges now work with various case formats

### File Changes

#### Created Files:
1. `/backend/services/badge-renderer/utils/logoMapping.js` - Constants for logo and color mappings
2. `/test-badge-rendering.js` - Test script to verify badge rendering
3. `/check-badge-settings.sql` - SQL to verify database badge settings
4. `/BADGE_RENDERING_FIXES.md` - This documentation

#### Modified Files:
1. `/backend/services/badge-renderer/canvasBadgeRenderer.js` - Main badge renderer fixes
2. `/backend/services/badge-renderer/posterProcessor.js` - Badge size validation and proper margin handling

### Key Improvements

1. **Better Error Handling**: More descriptive error messages for debugging
2. **Improved Path Resolution**: Enhanced algorithms for finding image assets
3. **Size Constraints**: Badges now respect poster dimensions to prevent errors
4. **Font Management**: Proper font loading and fallback system
5. **Logging**: Added detailed console logging for troubleshooting

### Testing

Run the test script to verify all fixes:

```bash
node test-badge-rendering.js
```

This will create test badges for each type and verify the rendering works correctly.

### Database Considerations

Check badge settings in the database:

```sql
\i check-badge-settings.sql
```

Ensure that:
- Badge sizes are reasonable (typically 50-200 pixels)
- Positions are valid (top-left, top-right, bottom-left, bottom-right)
- Transparency values are between 0 and 1
- Margins are set appropriately

### Future Improvements

1. Consider caching loaded images for better performance
2. Add support for more audio formats and their corresponding images
3. Implement adaptive sizing based on poster dimensions
4. Add support for custom fonts upload
5. Create a badge preview API endpoint

### Troubleshooting

If badges are still not rendering correctly:

1. Check the console logs for specific error messages
2. Verify that all image assets exist in the correct directories
3. Ensure database settings have valid values
4. Run the test script to isolate issues
5. Check that the poster dimensions are reasonable
6. Verify that badge sizes don't exceed poster dimensions
