# Badge Renderer Module

This module is responsible for rendering badge overlays for media items in Aphrodite.

## Changes Made

### 1. Fixed Color Consistency Issue
The original issue was that badge background colors set in the Preview page were not being applied properly when badges were rendered in the backend. 

The specific problems fixed:
- Added proper handling of both `backgroundColor` (camelCase from frontend) and `background_color` (snake_case from database)
- Added logic to prioritize custom colors over brand colors when both are present
- Made sure the background color property is checked consistently across all badge types
- Added appropriate debugging logs to track color source and application

### 2. Error Handling and Resilience
The module now has comprehensive error handling to ensure badge generation continues even if some badges fail:

- Improved validation of input parameters (size, dimensions, etc.)
- Added graceful fallback for missing resources (missing fonts, images, etc.)
- Created a consistent fallback badge system when rendering fails
- Enhanced error message clarity and specificity
- Implemented badge stacking safeguards to prevent errors from one badge affecting others

### 3. Code Refactoring and API Compatibility
The original `canvasBadgeRenderer.js` file was getting too large, so it was refactored into a more modular structure:

```
badge-renderer/
├── canvasBadgeRenderer.js     # Main entry point that delegates to specialized renderers
├── README.md                  # This documentation
├── renderers/                 # Specialized renderers for each badge type
│   ├── audioBadgeRenderer.js  # Handles audio badge rendering
│   ├── resolutionBadgeRenderer.js  # Handles resolution badge rendering
│   └── reviewBadgeRenderer.js # Handles review badge rendering
└── utils/                     # Shared utility functions
    ├── canvasUtils.js         # Common canvas operations (backgrounds, borders, etc.)
    └── logoMapping.js         # Maps rating sources to logos and colors
```

Benefits of this refactoring:
- Improved readability: Each badge type has its own dedicated file
- Better maintainability: Common functionality extracted to utilities
- Easier debugging: Clearer separation of concerns
- Reduced duplication: Shared functions are defined once and reused
- Backward compatibility: Core utility methods are still accessible through the main CanvasBadgeRenderer class for other modules that depend on them

## Error Resilience Features

1. **Input Validation**
   - Negative or invalid sizes are normalized to reasonable defaults
   - Empty metadata values are handled gracefully
   - Missing required parameters trigger appropriate fallbacks

2. **Resource Handling**
   - Missing images for audio formats fallback to text displays
   - Font loading errors have multiple fallback options
   - Sensible defaults for all critical settings

3. **Fallback System**
   - Each renderer has a multi-tiered fallback system:
     - Try primary render method (e.g., image-based badge)
     - If it fails, try text-based badge
     - If that fails, use a simple generic badge
   - This ensures that even if a badge cannot be rendered properly, the overall process will continue

4. **Position Safeguards**
   - Improved position calculation to never exceed poster boundaries
   - Automatic adjustment of badge positions to avoid edge clipping
   - Sensible default positions when specified position is invalid

## Usage

The main renderer interface remains unchanged, but internally it now delegates to specialized renderers with improved error handling:

```javascript
const renderer = new CanvasBadgeRenderer();
const badge = await renderer.renderBadge('audio', settings, metadata);
```

## Testing

A test script (`test-badge-resilience.js` in the backend root) verifies the resilience features:
1. Tests badge rendering with both valid and invalid configurations
2. Ensures the process continues even when some badges fail
3. Verifies color handling consistency
4. Tests the entire badge application workflow with error conditions

## Specific Technical Improvements

### Canvas Utilities (canvasUtils.js)
- Added proper error handling for the `drawRoundedRect` function to prevent errors from invalid dimensions
- Improved color handling with clear priority rules for different naming conventions
- Enhanced font selection logic to better handle missing fonts and prefer bold variants when needed
- Added more comprehensive audio format recognition with better normalization

### Badge Renderers
- Now validate size values and convert negative sizes to positive ones
- Added guardrails around canvas dimension calculations to prevent overflow errors
- Improved text overflow handling with intelligent text truncation
- Added a centralized fallback system with the `createFallbackBadge` function

### Main Renderer (canvasBadgeRenderer.js)
- Added comprehensive error handling around the `renderBadge` method
- Improved input validation with descriptive error messages
- Added safeguards to prevent modifications to the original settings object
- Implemented a multi-tier fallback system for rendering failures

## API Compatibility Notes

When refactoring, we moved utility functions like `getAudioImagePath` and `getResolutionImagePath` from the main class to the utility files. However, we maintained backward compatibility by re-exposing these methods in the main `CanvasBadgeRenderer` class, which now delegates to the utility functions. This ensures that existing code that depends on these methods will continue to work without modification.

## Further Improvements

Potential future improvements:
- Add unit tests for each renderer type
- Create TypeScript interfaces for the settings objects
- Add validation schema for settings to ensure required properties are present
- Consider caching commonly used logos and images for better performance
- Implement a more structured logging system for easier debugging
- Add support for additional badge types (e.g., award badges, custom badges)
- Enhance the fallback badge system with more configurable options