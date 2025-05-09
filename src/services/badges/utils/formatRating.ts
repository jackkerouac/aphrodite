import { ReviewSource } from '@/components/badges/types/ReviewBadge';

/**
 * Format a rating value based on the source
 * @param source The review source with rating information
 * @returns Formatted rating string
 */
export function formatRating(source: ReviewSource): string {
  const outOf = source.outOf || 10;
  let ratingText = '';
  
  // Format based on the rating source
  switch(source.name.toUpperCase()) {
    case 'IMDB':
      // IMDb uses 10-point scale with 1 decimal place
      ratingText = source.rating.toFixed(1);
      break;
    case 'RT':
      // Rotten Tomatoes uses percentage
      ratingText = Math.round(source.rating) + '%';
      break;
    case 'METACRITIC':
      // Metacritic uses 0-100 scale
      ratingText = Math.round(source.rating).toString();
      break;
    case 'TMDB':
      // TMDb uses 10-point scale with 1 decimal place
      ratingText = source.rating.toFixed(1);
      break;
    case 'MAL':
      // MyAnimeList uses 10-point scale with 2 decimal places
      ratingText = source.rating.toFixed(2);
      break;
    case 'LETTERBOXD':
      // Letterboxd uses 5-star scale with half stars
      const stars = Math.round(source.rating * 2) / 2; // Round to nearest 0.5
      ratingText = stars.toFixed(1);
      break;
    case 'TRAKT':
      // Trakt uses 10-point scale with 1 decimal
      ratingText = source.rating.toFixed(1);
      break;
    case 'ANIDB':
      // AniDB uses 10-point scale with 2 decimals
      ratingText = source.rating.toFixed(2);
      break;
    default:
      // Generic formatting based on outOf value
      if (outOf === 10) {
        ratingText = source.rating.toFixed(1);
      } else if (outOf === 100) {
        ratingText = Math.round(source.rating) + '%';
      } else {
        ratingText = `${source.rating}/${outOf}`;
      }
      break;
  }
  
  return ratingText;
}