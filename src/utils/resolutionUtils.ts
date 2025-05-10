// src/utils/resolutionUtils.ts
import { resolutionOptions, resolutionImages } from '@/pages/settings/resolution-badge/constants';
import { ResolutionBadgeSettings as SettingsHookFormat } from '@/pages/settings/resolution-badge/hooks/useResolutionBadgeSettings';
import { ResolutionBadgeSettings as ComponentFormat } from '@/components/badges/types/ResolutionBadge';

// Dynamically import resolution badge images for production build compatibility
const getResolutionImageImport = (resolutionType: string): Promise<string> => {
  // Default to 1080 if none is provided
  if (!resolutionType) resolutionType = '1080';
  
  // Convert legacy values if needed
  const legacyMapping: Record<string, string> = {
    '4K': '4k',
    'UHD': '4k',
    'HD': '1080',
    'SD': '480',
    'HDR': 'hdr',
    'DV': 'dv',
    'Dolby Vision': 'dv'
  };
  
  const resolvedType = legacyMapping[resolutionType] || resolutionType;
  
  // Return a Promise that resolves to the actual image URL
  return new Promise<string>(resolve => {
    // Use a dynamic import() for the image based on the type
    import(`@/assets/resolution/${resolvedType}.png`)
      .then(module => {
        console.log(`Loaded image for resolution type ${resolvedType}:`, module.default);
        resolve(module.default);
      })
      .catch(error => {
        console.error(`Error loading image for ${resolvedType}:`, error);
        // Fallback to 1080 if the specific resolution image doesn't exist
        import('@/assets/resolution/1080.png')
          .then(module => {
            console.log('Falling back to default 1080p image:', module.default);
            resolve(module.default);
          })
          .catch(fallbackError => {
            console.error('Could not even load fallback image:', fallbackError);
            resolve(''); // Return empty string as a last resort
          });
      });
  });
};

// Cache for resolution images
const imageCache: Record<string, string> = {};

// Preload common resolution images
export const preloadResolutionImages = async () => {
  const commonResolutions = ['1080', '1080p', '4k', '720p', '480p', 'hdr', 'dv'];
  
  for (const resType of commonResolutions) {
    try {
      const imageUrl = await getResolutionImageImport(resType);
      imageCache[resType] = imageUrl;
      console.log(`Preloaded image for ${resType}:`, imageUrl);
    } catch (error) {
      console.warn(`Failed to preload image for ${resType}:`, error);
    }
  }
  
  return imageCache;
};

// Add a function to check if a resolution image exists and get its URL
export const getSourceImageUrlForResolution = async (resolutionType: string): Promise<string> => {
  if (!resolutionType) resolutionType = '1080';
  
  // Check cache first
  if (imageCache[resolutionType]) {
    return imageCache[resolutionType];
  }
  
  try {
    // Use the dynamic import function to get the actual image URL
    const imageUrl = await getResolutionImageImport(resolutionType);
    
    // Save to cache
    imageCache[resolutionType] = imageUrl;
    
    return imageUrl;
  } catch (error) {
    console.error(`Error getting image for resolution type ${resolutionType}:`, error);
    
    // Fallback to a cached image or default
    if (imageCache['1080']) {
      return imageCache['1080'];
    }
    
    // Fallback to a static path if dynamic import fails
    return '/src/assets/resolution/1080.png';
  }
};

// Export the resolution options for reusability
export const getResolutionOptions = () => {
  return resolutionOptions.map(value => ({
    value,
    label: getResolutionDisplayName(value)
  }));
};

// Convert between settings formats
export const convertResolutionSettingsFormats = {
  // Convert from settings hook format to component format
  toComponentFormat: (settings: SettingsHookFormat): ComponentFormat => {
    return {
      size: settings.size,
      backgroundColor: settings.background_color,
      backgroundOpacity: settings.background_transparency,
      borderRadius: settings.border_radius,
      borderWidth: settings.border_width,
      borderColor: settings.border_color,
      borderOpacity: settings.border_transparency,
      shadowEnabled: settings.shadow_toggle,
      shadowColor: settings.shadow_color,
      shadowBlur: settings.shadow_blur_radius,
      shadowOffsetX: settings.shadow_offset_x,
      shadowOffsetY: settings.shadow_offset_y,
      textColor: '#FFFFFF', // Default text color if not in settings
      resolutionType: settings.resolution_type,
      position: {
        percentX: 5, // Default position if not specified
        percentY: 5
      }
    };
  },
  
  // Convert from component format to settings hook format
  toSettingsHookFormat: (component: ComponentFormat): SettingsHookFormat => {
    return {
      size: component.size,
      margin: 10, // Default margin
      position: 'top-left', // Default position
      resolution_type: component.resolutionType || '1080',
      background_color: component.backgroundColor,
      background_transparency: component.backgroundOpacity,
      border_radius: component.borderRadius || 0,
      border_width: component.borderWidth || 0,
      border_color: component.borderColor || '#FFFFFF',
      border_transparency: component.borderOpacity || 1,
      shadow_toggle: component.shadowEnabled || false,
      shadow_color: component.shadowColor || '#000000',
      shadow_blur_radius: component.shadowBlur || 0,
      shadow_offset_x: component.shadowOffsetX || 0,
      shadow_offset_y: component.shadowOffsetY || 0,
      z_index: 10 // Default z-index
    };
  }
};

// Get image path from resolution type
export const getResolutionImagePath = (resolutionType: string): string => {
  // Default to 1080 if none is provided
  if (!resolutionType) return '/src/assets/resolution/1080.png';
  
  // Handle legacy resolution type values (if any existed before this update)
  const legacyMapping: Record<string, string> = {
    // Add any legacy mappings here if needed
    '4K': '4k',
    'UHD': '4k',
    'HD': '1080',
    'SD': '480',
    'HDR': 'hdr',
    'DV': 'dv',
    'Dolby Vision': 'dv'
  };
  
  // Convert legacy values if needed
  const resolvedType = legacyMapping[resolutionType] || resolutionType;
  
  // Check if the resolved type exists in our images mapping
  if (resolutionImages[resolvedType]) {
    return resolutionImages[resolvedType];
  }
  
  // If not found, fallback to a default resolution image
  console.warn(`Resolution type "${resolutionType}" not found, using default.`);
  return '/src/assets/resolution/1080.png';
};

// Helper function to get resolution type display name
export const getResolutionDisplayName = (resolutionType: string): string => {
  if (!resolutionType) return '1080';
  
  // Format the resolution type for display
  // This can be customized based on your naming conventions
  const displayMap: Record<string, string> = {
    '4k': '4K',
    '4kdv': '4K DV',
    '4kdvhdr': '4K DV HDR',
    '4kdvhdrplus': '4K DV HDR+',
    '4khdr': '4K HDR',
    '4kplus': '4K+',
    '480': '480p',
    '480p': '480p',
    '480pdv': '480p DV',
    '480pdvhdr': '480p DV HDR',
    '480pdvhdrplus': '480p DV HDR+',
    '480phdr': '480p HDR',
    '480pplus': '480p+',
    '576p': '576p',
    '576pdv': '576p DV',
    '576pdvhdr': '576p DV HDR',
    '576pdvhdrplus': '576p DV HDR+',
    '576phdr': '576p HDR',
    '576pplus': '576p+',
    '720': '720p',
    '720p': '720p',
    '720pdv': '720p DV',
    '720pdvhdr': '720p DV HDR',
    '720pdvhdrplus': '720p DV HDR+',
    '720phdr': '720p HDR',
    '720pplus': '720p+',
    '1080': '1080p',
    '1080p': '1080p',
    '1080pdv': '1080p DV',
    '1080pdvhdr': '1080p DV HDR',
    '1080pdvhdrplus': '1080p DV HDR+',
    '1080phdr': '1080p HDR',
    '1080pplus': '1080p+',
    '2160': '2160p',
    'dv': 'Dolby Vision',
    'dvhdr': 'DV HDR',
    'dvhdrplus': 'DV HDR+',
    'hdr': 'HDR',
    'plus': 'Plus'
  };
  
  return displayMap[resolutionType.toLowerCase()] || resolutionType.toUpperCase();
};

// Function to categorize resolutions
export const categorizeResolutions = () => {
  return {
    standard: ['480', '480p', '576p', '720', '720p', '1080', '1080p', '2160', '4k'],
    hdr: ['480phdr', '576phdr', '720phdr', '1080phdr', '4khdr', 'hdr'],
    dolbyVision: ['480pdv', '576pdv', '720pdv', '1080pdv', '4kdv', 'dv'],
    advanced: [
      '480pdvhdr', '480pdvhdrplus', '480pplus',
      '576pdvhdr', '576pdvhdrplus', '576pplus',
      '720pdvhdr', '720pdvhdrplus', '720pplus',
      '1080pdvhdr', '1080pdvhdrplus', '1080pplus',
      '4kdvhdr', '4kdvhdrplus', '4kplus',
      'dvhdr', 'dvhdrplus'
    ]
  };
};
