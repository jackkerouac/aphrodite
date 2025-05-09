// Re-export all utility functions from their respective files
export { formatRating } from './formatRating';
export { RATING_LOGO_MAP, RATING_BG_COLOR_MAP } from './logoMapping';
export { loadImage } from './imageLoading';

// Also re-export utilities from the parent utils.ts file
export { createTempCanvas, drawRoundedRect, extractBadgeWithTransparency } from '../utils';