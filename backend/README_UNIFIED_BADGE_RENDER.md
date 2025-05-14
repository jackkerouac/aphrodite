# Unified Badge Rendering System

This system provides a completely refactored implementation of the badge rendering process for the Run Aphrodite page. It uses the same approach as the Preview page, ensuring consistent results and simpler code.

## Installation

1. Install the required dependencies:
   ```bash
   node install-badge-dependencies.js
   ```

2. Copy badge assets from the frontend to the backend:
   ```bash
   node copy-badge-assets.js
   ```

3. Restart the backend server:
   ```bash
   npm run dev
   ```

## Testing

You can test the unified badge renderer using the provided test script:

```bash
node test-unified-badge-renderer.js
```

This script will:
1. Create a test job in the database
2. Process a single item using the unified badge renderer
3. Report the results
4. Clean up the test data

## Workflow

The unified badge rendering system follows this workflow:

1. **Job Creation**
   - Create a job with the selected items
   - No preprocessing or transformation of badge settings

2. **Badge Rendering** (for each item)
   - Pull badge settings directly from the database
   - Download poster from Jellyfin
   - Standardize poster to 1000px width
   - Draw badges on the poster using Node Canvas
   - Upload modified poster back to Jellyfin

3. **Job Monitoring**
   - Progress is tracked and reported to the frontend
   - Detailed logs are available for troubleshooting

## File Structure

- `services/unified-badge-renderer/unifiedPosterProcessor.js` - Main processor service
- `services/unified-badge-renderer/nodeCanvasBadgeRenderer.js` - Badge rendering implementation
- `services/unified-badge-renderer/jobController.js` - Job management service
- `routes/unified-badge-render.js` - API endpoints for the new service

## API Endpoints

- `POST /api/unified-badge-render/jobs` - Create a new job
- `GET /api/unified-badge-render/jobs/:id` - Get job status
- `DELETE /api/unified-badge-render/jobs/:id` - Cancel a job
- `GET /api/unified-badge-render/jobs` - Get all jobs for the user

## Troubleshooting

If you encounter any issues:

1. Check the logs in the backend console
2. Ensure the badge assets were properly copied
3. Verify that the dependencies were installed correctly
4. Check the database for unified badge settings

If the backend is having trouble finding the badge images, you may need to adjust the paths in the `nodeCanvasBadgeRenderer.js` file.
