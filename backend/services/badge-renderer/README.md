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

### 2. Code Refactoring and API Compatibility
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

## Testing

A test script (`test-badge-color.js` in the backend root) has been provided to verify that the background color handling is working correctly. It tests:
1. Custom colors using snake_case property (`background_color`)
2. Custom colors using camelCase property (`backgroundColor`)
3. Brand colors when enabled
4. Priority handling when both custom and brand colors are specified

## Usage

The main renderer interface remains unchanged, but internally it now delegates to specialized renderers:

```javascript
const renderer = new CanvasBadgeRenderer();
const badge = await renderer.renderBadge('audio', settings, metadata);
```

## Further Improvements

Potential future improvements:
- Add unit tests for each renderer type
- Create TypeScript interfaces for the settings objects
- Add validation for settings to ensure required properties are present
- Consider caching commonly used logos and images for better performance

## API Compatibility Notes

When refactoring, we moved utility functions like `getAudioImagePath` and `getResolutionImagePath` from the main class to the utility files. However, we discovered that the `posterProcessor.js` file directly called these methods. Rather than modifying that file, we maintained backward compatibility by re-exposing these methods in the main `CanvasBadgeRenderer` class, which now delegates to the utility functions.

In the future, when updating external code, it would be good to have them use the utility functions directly rather than through the main renderer class.