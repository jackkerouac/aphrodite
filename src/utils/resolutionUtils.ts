/**
 * Utility functions and constants for resolution options
 */

export interface ResolutionOption {
  value: string;
  label: string;
  iconPath?: string;
}

// Available resolution options
export const resolutionOptions: ResolutionOption[] = [
  { value: '4k', label: '4K', iconPath: '/assets/images/resolution/4k.png' },
  { value: '1080p', label: '1080p', iconPath: '/assets/images/resolution/1080p.png' },
  { value: '720p', label: '720p', iconPath: '/assets/images/resolution/720p.png' },
  { value: '8k', label: '8K', iconPath: '/assets/images/resolution/8k.png' },
  { value: 'hdr', label: 'HDR', iconPath: '/assets/images/resolution/hdr.png' },
  { value: 'hdr10', label: 'HDR10', iconPath: '/assets/images/resolution/hdr10.png' },
  { value: 'hdr10_plus', label: 'HDR10+', iconPath: '/assets/images/resolution/hdr10_plus.png' },
  { value: 'dolby_vision', label: 'Dolby Vision', iconPath: '/assets/images/resolution/dolby_vision.png' },
  { value: 'hlg', label: 'HLG', iconPath: '/assets/images/resolution/hlg.png' },
  { value: 'imax', label: 'IMAX', iconPath: '/assets/images/resolution/imax.png' },
];

/**
 * Get the icon path for a given resolution
 * @param resolutionType The resolution type
 * @returns The path to the resolution icon
 */
export const getSourceImageUrlForResolution = async (resolutionType: string): Promise<string> => {
  const resolution = resolutionOptions.find(option => option.value === resolutionType);
  
  if (resolution && resolution.iconPath) {
    return resolution.iconPath;
  }
  
  // Return a default icon if the resolution is not found
  return '/assets/images/resolution/4k.png';
};
