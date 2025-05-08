// src/utils/resolutionUtils.ts
import { resolutionOptions, resolutionImages } from '@/pages/settings/resolution-badge/constants';

// Export the resolution options for reusability
export const getResolutionOptions = () => {
  return resolutionOptions.map(value => ({
    value,
    label: value.toUpperCase()
  }));
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
    '1080': '1080p',
    '1080p': '1080p',
    '1080pdv': '1080p DV',
    '1080pdvhdr': '1080p DV HDR',
    '1080pdvhdrplus': '1080p DV HDR+',
    '1080phdr': '1080p HDR',
    '1080pplus': '1080p+',
    '720': '720p',
    '720p': '720p',
    '720pdv': '720p DV',
    '720pdvhdr': '720p DV HDR',
    '720pdvhdrplus': '720p DV HDR+',
    '720phdr': '720p HDR',
    '720pplus': '720p+',
    '576p': '576p',
    '576pdv': '576p DV',
    '576pdvhdr': '576p DV HDR',
    '576pdvhdrplus': '576p DV HDR+',
    '576phdr': '576p HDR',
    '576pplus': '576p+',
    '480': '480p',
    '480p': '480p',
    '480pdv': '480p DV',
    '480pdvhdr': '480p DV HDR',
    '480pdvhdrplus': '480p DV HDR+',
    '480phdr': '480p HDR',
    '480pplus': '480p+',
    '2160': '2160p',
    'dv': 'Dolby Vision',
    'dvhdr': 'DV HDR',
    'dvhdrplus': 'DV HDR+',
    'hdr': 'HDR'
  };
  
  return displayMap[resolutionType] || resolutionType.toUpperCase();
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
