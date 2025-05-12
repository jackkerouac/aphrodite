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
  { value: '4k', label: '4K', iconPath: '/src/assets/resolution/4k.png' },
  { value: '1080p', label: '1080p', iconPath: '/src/assets/resolution/1080p.png' },
  { value: '720p', label: '720p', iconPath: '/src/assets/resolution/720p.png' },
  { value: '576p', label: '576p', iconPath: '/src/assets/resolution/576p.png' },
  { value: '480p', label: '480p', iconPath: '/src/assets/resolution/480p.png' },
  { value: 'hdr', label: 'HDR', iconPath: '/src/assets/resolution/hdr.png' },
  { value: '4khdr', label: '4K HDR', iconPath: '/src/assets/resolution/4khdr.png' },
  { value: '1080phdr', label: '1080p HDR', iconPath: '/src/assets/resolution/1080phdr.png' },
  { value: '720phdr', label: '720p HDR', iconPath: '/src/assets/resolution/720phdr.png' },
  { value: 'dolby_vision', label: 'Dolby Vision', iconPath: '/src/assets/resolution/dv.png' },
  { value: '4kdv', label: '4K Dolby Vision', iconPath: '/src/assets/resolution/4kdv.png' },
  { value: '1080pdv', label: '1080p Dolby Vision', iconPath: '/src/assets/resolution/1080pdv.png' },
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
  return '/src/assets/resolution/4k.png';
};
