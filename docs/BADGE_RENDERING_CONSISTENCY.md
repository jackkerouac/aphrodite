# Badge Rendering Consistency Implementation

## Overview

This document describes the implementation of consistent badge rendering between the frontend Preview page and the backend Run Aphrodite processing.

## Problem Statement

Previously, badges rendered differently in two scenarios:
- **Frontend Preview**: Used HTML5 Canvas API to create beautifully styled badges with images, gradients, and shadows
- **Backend Processing**: Created simple SVG badges that looked completely different

This inconsistency caused confusion for users who would see one style in the preview but get different results when actually applying badges to their media library.

## Solution Implemented

We implemented Option 2: Server-side canvas rendering using the `node-canvas` library to replicate the exact same logic as the frontend.

### Key Components

1. **CanvasBadgeRenderer** (`backend/services/badge-renderer/canvasBadgeRenderer.js`)
   - Server-side implementation using node-canvas
   - Replicates the frontend badge rendering logic
   - Supports resolution, audio, and review badges
   - Handles image loading and text rendering
   - Applies all styling options (colors, borders, shadows, etc.)

2. **Updated PosterProcessor** (`backend/services/badge-renderer/posterProcessor.js`)
   - Added `applyBadgesWithCanvas` method
   - Uses `USE_CANVAS_RENDERER` environment variable to enable/disable canvas rendering
   - Falls back to SVG rendering if canvas is disabled

3. **Badge Image Asset Mapping**
   - Maps resolution values (4K, 1080p, etc.) to image assets
   - Maps audio formats (DTS, Dolby, etc.) to appropriate codec images
   - Handles file existence checks and fallbacks

### Configuration

Add to your `.env` file:
```
USE_CANVAS_RENDERER=true
```

Setting this to `false` will revert to the old SVG rendering method.

### Dependencies

The implementation requires the `canvas` package:
```json
"canvas": "^2.11.2"
```

This package provides a Cairo-backed Canvas implementation for Node.js.

## Testing

A test script is provided at `backend/test-badge-renderer.js` to verify badge rendering:

```bash
cd backend
node test-badge-renderer.js
```

This will generate test badges for resolution, audio, and review types.

## Benefits

1. **Visual Consistency**: Badges look identical in preview and final output
2. **Reused Logic**: No duplication of rendering code
3. **Better Styling**: Canvas allows for more sophisticated visual effects
4. **Image Support**: Properly renders badge images (resolution, audio codec icons)
5. **Future-Proof**: Easy to add new badge types or styling options

## Migration Notes

- The old SVG rendering is still available as a fallback
- No database schema changes were required
- All existing badge settings are compatible
- The implementation is backward compatible

## Performance Considerations

- Canvas rendering is slightly more CPU-intensive than SVG
- Image loading is cached where possible
- Batch processing remains efficient with proper concurrency control

## Future Enhancements

1. Add font caching for better performance
2. Implement badge template system for easier customization
3. Add support for custom badge types
4. Optimize image loading with sprite sheets
