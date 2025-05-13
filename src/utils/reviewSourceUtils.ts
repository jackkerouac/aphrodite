/**
 * Utility functions and constants for review source options
 */

export interface ReviewSourceOption {
  value: string;
  label: string;
  iconPath?: string;
}



// Available review source options
export const reviewSourceOptions: ReviewSourceOption[] = [
  { value: 'imdb', label: 'IMDb', iconPath: '/src/assets/rating/IMDb.png' },
  { value: 'rt_audience', label: 'Rotten Tomatoes Audience', iconPath: '/src/assets/rating/RT-Aud-Fresh.png' },
  { value: 'rt_critic', label: 'Rotten Tomatoes Critic', iconPath: '/src/assets/rating/RT-Crit-Fresh.png' },
  { value: 'metacritic', label: 'Metacritic', iconPath: '/src/assets/rating/metacritic_logo.png' },
  { value: 'letterboxd', label: 'Letterboxd', iconPath: '/src/assets/rating/Letterboxd.png' },
  { value: 'tmdb', label: 'TMDb', iconPath: '/src/assets/rating/TMDb.png' },
  { value: 'trakt', label: 'Trakt', iconPath: '/src/assets/rating/Trakt.png' },
  { value: 'anidb', label: 'AniDB', iconPath: '/src/assets/rating/AniDB.png' },
  { value: 'mal', label: 'MyAnimeList', iconPath: '/src/assets/rating/MAL.png' },
  { value: 'mdblist', label: 'MDBList', iconPath: '/src/assets/rating/MDBList.png' },
];

/**
 * Get the icon path for a given review source
 * @param sourceName The review source name
 * @returns The path to the source icon
 */
export const getReviewSourceIcon = async (sourceName: string): Promise<string> => {
  // Check if the source has different states (like RT Fresh/Rotten)
  if (sourceName === 'rt_audience') {
    // Default to fresh for now, the actual state can be determined by the score
    return '/src/assets/rating/RT-Aud-Fresh.png';
  } else if (sourceName === 'rt_critic') {
    // Default to fresh for now, the actual state can be determined by the score
    return '/src/assets/rating/RT-Crit-Fresh.png';
  }

  // Find the source from the options
  const source = reviewSourceOptions.find(option => option.value === sourceName);
  
  if (source && source.iconPath) {
    return source.iconPath;
  }
  
  // Return a default icon if the source is not found
  return '/src/assets/rating/IMDb.png';
};

/**
 * Get the appropriate Rotten Tomatoes icon based on score and type
 * @param type 'audience' or 'critic'
 * @param score Score value (0-100)
 * @returns Path to the appropriate RT icon
 */
export const getRTIconForScore = (type: 'audience' | 'critic', score: number): string => {
  // For audience:
  // Fresh: 60% or higher
  // Rotten: below 60%
  
  // For critics:
  // Certified Fresh: 75% or higher with minimum review count (not implemented here)
  // Fresh: 60-74%
  // Rotten: below 60%
  
  if (type === 'audience') {
    if (score >= 60) {
      return '/src/assets/rating/RT-Aud-Fresh.png';
    } else {
      return '/src/assets/rating/RT-Aud-Rotten.png';
    }
  } else {
    // Critic ratings
    if (score >= 75) {
      return '/src/assets/rating/RT-Crit-Top.png';
    } else if (score >= 60) {
      return '/src/assets/rating/RT-Crit-Fresh.png';
    } else {
      return '/src/assets/rating/RT-Crit-Rotten.png';
    }
  }
};

/**
 * Format a score value based on the source and score type
 * @param source Review source (imdb, rt_audience, etc.)
 * @param score Raw score value
 * @param scoreType Type of score (percentage, rating, etc.)
 * @returns Formatted score string
 */
export const formatScore = (source: string, score: number, scoreType: string = 'percentage'): string => {
  if (source === 'imdb') {
    // IMDb is on a 1-10 scale with one decimal place
    return score.toFixed(1);
  } else if (source.startsWith('rt_')) {
    // Rotten Tomatoes uses percentages
    return `${Math.round(score)}%`;
  } else if (source === 'metacritic') {
    // Metacritic uses a 0-100 scale
    return `${Math.round(score)}`;
  } else if (source === 'letterboxd') {
    // Letterboxd uses a 0-5 scale with half steps
    return (Math.round(score * 2) / 2).toFixed(1);
  } else if (source === 'tmdb') {
    // TMDb uses a 0-10 scale with one decimal place
    return score.toFixed(1);
  } else if (source === 'mal') {
    // MyAnimeList uses a 1-10 scale with two decimal places
    return score.toFixed(2);
  } else {
    // Default formatting based on score type
    if (scoreType === 'percentage') {
      return `${Math.round(score)}%`;
    } else if (scoreType === 'rating') {
      return score.toFixed(1);
    } else {
      return score.toString();
    }
  }
};

/**
 * Get the font color for a score based on source and value
 * @param source Review source
 * @param score Score value
 * @returns Hex color code for the score text
 */
export const getScoreColor = (source: string, score: number): string => {
  if (source === 'metacritic') {
    // Metacritic color coding
    if (score >= 75) return '#6c3'; // Green for good
    if (score >= 50) return '#fc3'; // Yellow for mixed
    return '#f00'; // Red for bad
  } else if (source.startsWith('rt_')) {
    // Rotten Tomatoes
    if (score >= 60) return '#fa320a'; // Rotten Tomatoes Fresh red
    return '#6b7280'; // Grey for rotten
  } else if (source === 'imdb') {
    return '#f5c518'; // IMDb yellow
  }
  
  // Default white
  return '#ffffff';
};

// Alias for backwards compatibility with the ReviewBadgeControls component
export const availableReviewSources = reviewSourceOptions;
