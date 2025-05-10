// src/utils/audioCodecUtils.ts

// Define audio codec options
export const audioCodecOptions = [
  { value: 'aac', label: 'AAC' },
  { value: 'atmos', label: 'Atmos' },
  { value: 'digital', label: 'Digital' },
  { value: 'dolby_atmos', label: 'Dolby Atmos' },
  { value: 'dts', label: 'DTS' },
  { value: 'dtses', label: 'DTS-ES' },
  { value: 'dtsx', label: 'DTS:X' },
  { value: 'flac', label: 'FLAC' },
  { value: 'hra', label: 'HRA' },
  { value: 'ma', label: 'MA' },
  { value: 'mp3', label: 'MP3' },
  { value: 'opus', label: 'OPUS' },
  { value: 'pcm', label: 'PCM' },
  { value: 'plus', label: 'Plus' },
  { value: 'plus_atmos', label: 'Plus Atmos' },
  { value: 'truehd', label: 'TrueHD' },
  { value: 'truehd_atmos', label: 'TrueHD Atmos' }
];

// Get image path from codec type
export const getAudioCodecImagePath = (codecType: string): string => {
  // Default to dolby_atmos if none is provided
  if (!codecType) return '/src/assets/audio_codec/compact/dolby_atmos.png';
  
  // Handle legacy codec type values (from before this update)
  // These are the full text labels that were previously used
  const legacyMapping: Record<string, string> = {
    'Dolby Atmos': 'dolby_atmos',
    'Dolby Digital': 'digital',
    'DTS-HD': 'dts',
    'DTS:X': 'dtsx',
    'AAC': 'aac',
    'PCM': 'pcm',
    'FLAC': 'flac'
  };
  
  // Convert legacy values if needed
  const codecValue = legacyMapping[codecType] || codecType;
  
  // Return the path to the image
  return `/src/assets/audio_codec/compact/${codecValue}.png`;
};
