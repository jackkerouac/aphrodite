/**
 * Utility functions and constants for audio codec options
 */

export interface AudioCodecOption {
  value: string;
  label: string;
  iconPath?: string;
}

// Available audio codec options
export const audioCodecOptions: AudioCodecOption[] = [
  { value: 'dolby_atmos', label: 'Dolby Atmos', iconPath: '/assets/images/audio/dolby_atmos.png' },
  { value: 'dolby_digital', label: 'Dolby Digital', iconPath: '/assets/images/audio/dolby_digital.png' },
  { value: 'dolby_digital_plus', label: 'Dolby Digital Plus', iconPath: '/assets/images/audio/dolby_digital_plus.png' },
  { value: 'dolby_truehd', label: 'Dolby TrueHD', iconPath: '/assets/images/audio/dolby_truehd.png' },
  { value: 'dts', label: 'DTS', iconPath: '/assets/images/audio/dts.png' },
  { value: 'dts_hd', label: 'DTS-HD', iconPath: '/assets/images/audio/dts_hd.png' },
  { value: 'dts_hd_ma', label: 'DTS-HD Master Audio', iconPath: '/assets/images/audio/dts_hd_ma.png' },
  { value: 'dts_x', label: 'DTS:X', iconPath: '/assets/images/audio/dts_x.png' },
  { value: 'auro_3d', label: 'Auro 3D', iconPath: '/assets/images/audio/auro_3d.png' },
  { value: 'imax_enhanced', label: 'IMAX Enhanced', iconPath: '/assets/images/audio/imax_enhanced.png' },
  { value: 'thx', label: 'THX', iconPath: '/assets/images/audio/thx.png' },
];

/**
 * Get the icon path for a given audio codec
 * @param codecType The audio codec type
 * @returns The path to the codec icon
 */
export const getAudioCodecIcon = async (codecType: string): Promise<string> => {
  const codec = audioCodecOptions.find(option => option.value === codecType);
  
  if (codec && codec.iconPath) {
    return codec.iconPath;
  }
  
  // Return a default icon if the codec is not found
  return '/assets/images/audio/dolby_atmos.png';
};
