# Badge Image Storage Implementation

This document explains how badge images are stored and managed in the Aphrodite UI application.

## Overview

The implementation stores badge images (for audio, resolution, and review badges) as BLOB data in the PostgreSQL database. This approach has several advantages:

- Eliminates issues with re-generating badges consistently
- Improves performance by avoiding on-the-fly badge generation on the preview page
- Ensures badges look exactly the same across different parts of the application

## Database Changes

The implementation adds the following fields to badge settings tables:
- `badge_image`: BYTEA field to store the actual badge image as binary data
- `last_generated_at`: Timestamp to track when the badge was last regenerated

These fields are added to the following tables:
- `audio_badge_settings`
- `resolution_badge_settings`
- `review_badge_settings`

## Setup Instructions

Follow these steps to set up the badge image storage functionality:

1. **Install required dependencies**:
   ```bash
   npm run install-badge-deps
   ```
   This installs the `canvas` and `multer` packages needed for badge generation and image handling.

2. **Run the database migration**:
   ```bash
   npm run run-migration
   ```
   This adds the necessary fields to the database tables.

3. **Test the badge storage**:
   ```bash
   npm run test-badge-storage
   ```
   This verifies that badge images can be stored in and retrieved from the database.

## How It Works

1. When a user saves badge settings, the backend:
   - Takes all badge settings parameters from the client
   - Generates a badge image using the canvas library
   - Saves both the settings and the generated image to the database

2. When the preview page needs to display a badge:
   - The client requests the badge image from a dedicated endpoint
   - The backend retrieves the stored image from the database
   - If no image exists, one is generated on the fly and stored for future use

3. The badge image URL includes a timestamp to prevent browsers from caching outdated images.

## API Endpoints

- `GET /api/audio-badge-settings/:userId/image` - Retrieves the audio badge image
- `GET /api/resolution-badge-settings/:userId/image` - Retrieves the resolution badge image (not yet implemented)
- `GET /api/review-badge-settings/:userId/image` - Retrieves the review badge image (not yet implemented)

## Frontend Implementation

The frontend uses these endpoints to display badges in the preview panel:

```jsx
<img
  src={apiClient.audioBadge.getBadgeImage()}
  alt="Audio badge from server"
  style={getBadgeImageStyle()}
/>
```

## Troubleshooting

If you encounter issues with badge image generation or display:

1. Check the server logs for error messages
2. Verify that the canvas package is installed correctly
3. Run the `test-badge-storage.mjs` script to verify database connectivity
4. Ensure your database user has permissions to write BYTEA data
