# Unified Badge Rendering Refactor

## Overview
This refactor completely replaces the Run Aphrodite workflow for badge rendering with a simpler, more reliable implementation that uses the same rendering approach as the Preview page.

## Key Changes

1. **Created a simplified renderer service:**
   - Removed the complex badge transformations and normalizations
   - Created a badge rendering system that takes settings directly from the database
   - Implemented a simple, clear workflow: fetch settings → render badges → apply to poster

2. **Improved architecture:**
   - Main processor file (unifiedPosterProcessor.js) outlines the whole workflow
   - Node Canvas renderer (nodeCanvasBadgeRenderer.js) handles the actual badge drawing
   - Job controller (jobController.js) manages the job state and progress

3. **Frontend improvements:**
   - Created a dedicated API for unified badge rendering (/api/unified-badge-render/*)
   - Updated the Run Aphrodite page to use the new API
   - Implemented a custom hook (useUnifiedJobStatus.js) for job status monitoring

## New Badge Rendering Workflow

1. **Database Storage**
   - Badge settings are stored in the `unified_badge_settings` table

2. **Job Creation**
   - User selects libraries and items to process
   - Backend creates a job with selected items
   - No preprocessing or transformation of badge settings

3. **Badge Rendering**
   - For each item:
     - Pull badge settings directly from the database
     - Download poster from Jellyfin
     - Standardize poster to 1000px width
     - Draw badges on the poster using Node Canvas
     - Upload modified poster back to Jellyfin

4. **Benefits**
   - Consistent rendering between Preview and Run Aphrodite
   - Simplified code with fewer transformations
   - Clearer logging and error handling
   - More reliable badge application

## Files Created/Modified

### Backend
- `services/unified-badge-renderer/unifiedPosterProcessor.js` - Main processor service
- `services/unified-badge-renderer/nodeCanvasBadgeRenderer.js` - Badge rendering implementation
- `services/unified-badge-renderer/jobController.js` - Job management service
- `routes/unified-badge-render.js` - API endpoints for the new service
- `server.js` - Added new route to the server

### Frontend
- `hooks/useUnifiedJobStatus.js` - Custom hook for job status monitoring
- `components/run-aphrodite/RunAphroditeContext.tsx` - Updated to use new API
- `components/run-aphrodite/ProcessingStep.tsx` - Updated to use new status hook

## Next Steps

1. Test the implementation with various poster sizes and badge settings
2. Validate badge rendering matches exactly with the Preview page
3. Ensure proper error handling and recovery
4. Add additional logging for troubleshooting
5. Consider adding unit and integration tests for the new components
