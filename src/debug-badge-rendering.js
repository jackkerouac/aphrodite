// Debug script to compare frontend and backend badge rendering
import { reviewSources } from './pages/settings/review-badge/constants';
import { RATING_LOGO_MAP, RATING_BG_COLOR_MAP } from './services/badges/utils/index';

// Export branding maps for inspection
export const frontendBrandingMaps = {
  RATING_LOGO_MAP,
  RATING_BG_COLOR_MAP,
  reviewSources
};

/**
 * Debug function to log frontend badge settings
 * @param {string} badgeType - Type of badge (audio, resolution, review)
 * @param {object} settings - Badge settings object
 */
export function logFrontendBadgeSettings(badgeType, settings) {
  console.group(`Frontend Badge Settings Debug: ${badgeType}`);
  console.log('Complete settings object:', settings);
  
  // Log key properties
  console.log('Size:', settings.size);
  console.log('Position:', settings.position);
  console.log('Background Color:', settings.backgroundColor);
  console.log('Background Opacity:', settings.backgroundOpacity);
  console.log('Border Radius:', settings.borderRadius);

  // Review badge specific settings
  if (badgeType === 'review') {
    console.log('Display Format:', settings.displayFormat);
    console.log('Max Sources to Show:', settings.maxSourcesToShow);
    console.log('Show Dividers:', settings.showDividers);
    console.log('Sources:', settings.sources);
    console.log('Use Brand Colors:', settings.useBrandColors !== false);
  }

  // Log branding maps
  console.log('Available Rating Logo Map:', RATING_LOGO_MAP);
  console.log('Available Rating BG Color Map:', RATING_BG_COLOR_MAP);
  
  console.groupEnd();
  
  return {
    type: badgeType,
    settings,
    brandMaps: {
      RATING_LOGO_MAP,
      RATING_BG_COLOR_MAP
    }
  };
}

/**
 * Debug utility to evaluate what color would be used for a rating source
 * @param {string} sourceName - The name of the rating source (IMDB, RT, etc.)
 * @param {object} settings - Badge settings
 * @returns {object} The resolved color information
 */
export function evaluateSourceColors(sourceName, settings = {}) {
  const normalizedName = sourceName.toUpperCase();
  const hasBrandColor = RATING_BG_COLOR_MAP[normalizedName] !== undefined;
  const brandColor = RATING_BG_COLOR_MAP[normalizedName];
  const useBrandColors = settings.useBrandColors !== false;
  
  const resolvedColor = {
    sourceName: normalizedName,
    hasBrandColor,
    brandColor,
    backgroundColor: settings.backgroundColor || '#000000',
    useBrandColors,
    // This is what should actually be used
    effectiveColor: (useBrandColors && hasBrandColor) ? brandColor : settings.backgroundColor || '#000000'
  };
  
  console.log(`Color resolution for ${sourceName}:`, resolvedColor);
  
  return resolvedColor;
}
