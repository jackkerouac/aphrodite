// Audio codec options
export const audioCodecOptions = [
  'dolby_atmos', 'dts', 'dtses', 'dtsx', 'flac', 'hra', 'ma', 'mp3', 'opus', 
  'pcm', 'plus_atmos', 'plus', 'truehd_atmos', 'truehd', 'aac', 'atmos', 'digital'
];

// Define a mapping between audio codec types and their corresponding image paths
export const audioCodecImages: Record<string, string> = {
  'dolby_atmos': '/src/assets/audio_codec/standard/dolby_atmos.png',
  'dts': '/src/assets/audio_codec/standard/dts.png',
  'dtses': '/src/assets/audio_codec/standard/dtses.png',
  'dtsx': '/src/assets/audio_codec/standard/dtsx.png',
  'flac': '/src/assets/audio_codec/standard/flac.png',
  'hra': '/src/assets/audio_codec/standard/hra.png',
  'ma': '/src/assets/audio_codec/standard/ma.png',
  'mp3': '/src/assets/audio_codec/standard/mp3.png',
  'opus': '/src/assets/audio_codec/standard/opus.png',
  'pcm': '/src/assets/audio_codec/standard/pcm.png',
  'plus_atmos': '/src/assets/audio_codec/standard/plus_atmos.png',
  'plus': '/src/assets/audio_codec/standard/plus.png',
  'truehd_atmos': '/src/assets/audio_codec/standard/truehd_atmos.png',
  'truehd': '/src/assets/audio_codec/standard/truehd.png',
  'aac': '/src/assets/audio_codec/standard/aac.png',
  'atmos': '/src/assets/audio_codec/standard/atmos.png',
  'digital': '/src/assets/audio_codec/standard/digital.png',
};