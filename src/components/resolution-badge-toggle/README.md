# Resolution Badge Toggle Component

## Overview
The `ResolutionBadgeToggle` component provides a simple interface for toggling the visibility of resolution badges in the Aphrodite UI. This component integrates with the existing resolution badge system, using the same settings hook for consistency.

## Usage

```tsx
import ResolutionBadgeToggle from '@/components/resolution-badge-toggle/ResolutionBadgeToggle';

// Basic usage
<ResolutionBadgeToggle 
  onChange={(isEnabled) => console.log('Resolution badge is now:', isEnabled ? 'visible' : 'hidden')} 
/>

// With custom styling
<ResolutionBadgeToggle 
  className="my-custom-class" 
  onChange={handleToggle}
  initialEnabled={false}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onChange` | `(isEnabled: boolean) => void` | undefined | Callback function called when the toggle state changes |
| `className` | `string` | `''` | Additional CSS classes to apply to the component |
| `initialEnabled` | `boolean` | `true` | Initial state of the toggle |

## Integration Notes

This component integrates with the existing resolution badge system by:

1. Using the `useResolutionBadgeSettings` hook to fetch badge settings
2. Providing a consistent UI for toggling badge visibility
3. Working with the utility functions in `resolutionUtils.ts` for format conversion

The integration allows for a smooth transition between different parts of the application while maintaining a consistent user experience.

## Format Conversion

The system uses two different formats for resolution badge settings:

1. **Hook Format** - Used by the settings form and API calls
2. **Component Format** - Used by the rendering components

The `convertResolutionSettingsFormats` utility functions in `resolutionUtils.ts` handle conversions between these formats.
