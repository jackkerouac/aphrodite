/**
 * Utility functions and constants for review source options
 */

export interface ReviewSourceOption {
  value: string;
  label: string;
  iconPath?: string;
}

// Available review source options
export const availableReviewSources: ReviewSourceOption[] = [
  { value: 'imdb', label: 'IMDb', iconPath: '/assets/images/review/imdb.png' },
  { value: 'rotten_tomatoes', label: 'Rotten Tomatoes', iconPath: '/assets/images/review/rotten_tomatoes.png' },
  { value: 'metacritic', label: 'Metacritic', iconPath: '/assets/images/review/metacritic.png' },
  { value: 'letterboxd', label: 'Letterboxd', iconPath: '/assets/images/review/letterboxd.png' },
  { value: 'tmdb', label: 'TMDB', iconPath: '/assets/images/review/tmdb.png' },
  { value: 'mal', label: 'MyAnimeList', iconPath: '/assets/images/review/mal.png' },
  { value: 'anidb', label: 'AniDB', iconPath: '/assets/images/review/anidb.png' },
  { value: 'tvdb', label: 'TVDB', iconPath: '/assets/images/review/tvdb.png' },
];

/**
 * Get the icon path for a given review source
 * @param sourceName The review source name
 * @returns The path to the source icon
 */
export const getReviewSourceIcon = async (sourceName: string): Promise<string> => {
  const source = availableReviewSources.find(option => option.value === sourceName);
  
  if (source && source.iconPath) {
    return source.iconPath;
  }
  
  // Return a default icon if the source is not found
  return '/assets/images/review/imdb.png';
};
