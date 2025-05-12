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
  { value: 'dolby_atmos', label: 'Dolby Atmos', iconPath: '/src/assets/audio_codec/compact/dolby_atmos.png' },
  { value: 'dolby_digital', label: 'Dolby Digital', iconPath: '/src/assets/audio_codec/compact/digital.png' },
  { value: 'dolby_digital_plus', label: 'Dolby Digital Plus', iconPath: '/src/assets/audio_codec/compact/plus.png' },
  { value: 'dolby_truehd', label: 'Dolby TrueHD', iconPath: '/src/assets/audio_codec/compact/truehd.png' },
  { value: 'dts', label: 'DTS', iconPath: '/src/assets/audio_codec/compact/dts.png' },
  { value: 'dts_hd', label: 'DTS-HD', iconPath: '/src/assets/audio_codec/compact/dtses.png' },
  { value: 'dts_hd_ma', label: 'DTS-HD Master Audio', iconPath: '/src/assets/audio_codec/compact/ma.png' },
  { value: 'dts_x', label: 'DTS:X', iconPath: '/src/assets/audio_codec/compact/dtsx.png' },
  { value: 'aac', label: 'AAC', iconPath: '/src/assets/audio_codec/compact/aac.png' },
  { value: 'flac', label: 'FLAC', iconPath: '/src/assets/audio_codec/compact/flac.png' },
  { value: 'mp3', label: 'MP3', iconPath: '/src/assets/audio_codec/compact/mp3.png' },
  { value: 'pcm', label: 'PCM', iconPath: '/src/assets/audio_codec/compact/pcm.png' },
  { value: 'opus', label: 'Opus', iconPath: '/src/assets/audio_codec/compact/opus.png' },
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
  return '/src/assets/audio_codec/compact/dolby_atmos.png';
};
