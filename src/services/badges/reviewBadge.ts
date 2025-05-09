import { ReviewBadgeSettings } from '@/components/badges/types/ReviewBadge';
import { createTempCanvas, drawRoundedRect } from './utils';

// Import logos directly to ensure Vite bundles them correctly
import IMDbLogo from '@/assets/rating/IMDb.png';
import RTLogo from '@/assets/rating/RT-Crit-Fresh.png';
import MALLogo from '@/assets/rating/MAL.png';
import TMDbLogo from '@/assets/rating/TMDb.png';
import MetacriticLogo from '@/assets/rating/metacritic_logo.png';
import LetterboxdLogo from '@/assets/rating/Letterboxd.png';
import TraktLogo from '@/assets/rating/Trakt.png';
import AniDBLogo from '@/assets/rating/AniDB.png';

// Map of rating source names to logo paths
const RATING_LOGO_MAP: Record<string, string> = {
  'IMDB': IMDbLogo,
  'RT': RTLogo,
  'MAL': MALLogo,
  'TMDB': TMDbLogo,
  'Metacritic': MetacriticLogo,
  'Letterboxd': LetterboxdLogo,
  'Trakt': TraktLogo,
  'AniDB': AniDBLogo
};

// Map of rating source names to their standard background colors
const RATING_BG_COLOR_MAP: Record<string, string> = {
  'IMDB': '#F5C518',      // IMDb yellow
  'RT': '#FA320A',       // Rotten Tomatoes red
  'MAL': '#2E51A2',      // MyAnimeList blue
  'TMDB': '#0D253F',     // TMDb dark blue
  'Metacritic': '#000000', // Metacritic black
  'Letterboxd': '#00E054', // Letterboxd green
  'Trakt': '#ED2224',    // Trakt red
  'AniDB': '#3A3744'     // AniDB purple
};

/**
 * Load an image from a URL
 * @param url The URL of the image to load
 * @returns Promise resolving to an HTMLImageElement
 */
async function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    img.src = url;
  });
}

/**
 * Renders a review badge to a canvas
 * @param options The options for rendering the review badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderReviewBadge = async (
  options: ReviewBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  const isHorizontal = options.displayFormat !== 'vertical';
  const sources = options.sources || [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ];
  const maxSources = options.maxSourcesToShow || 2;
  const sourcesToShow = sources.slice(0, maxSources);
  
  // Use the base size for calculations
  const baseSize = Math.min(options.size, 200);
  
  // Constants for layout
  const padding = 10; // Padding around each badge
  const logoHeight = baseSize * 0.6; // 60% of badge size for logo
  const textHeight = baseSize * 0.3; // 30% of badge size for text
  const verticalSpacing = baseSize * 0.1; // 10% spacing between logo and text
  
  // Pre-load logo images for sizing calculations
  const logoPromises = sourcesToShow.map(async (source) => {
    // Try to get the logo from our map first
    const logoPath = RATING_LOGO_MAP[source.name.toUpperCase()] || 
                     RATING_LOGO_MAP[source.name] || 
                     null;
    if (!logoPath) {
      console.warn(`No logo found for rating source: ${source.name}`);
      return null;
    }
    
    try {
      return await loadImage(logoPath);
    } catch (error) {
      console.error(`Failed to load logo for ${source.name}:`, error);
      return null;
    }
  });
  
  const logos = await Promise.all(logoPromises);
  
  // Calculate dimensions based on loaded logos
  let badgeWidths: number[] = [];
  
  // Calculate each badge width based on its logo's aspect ratio
  logos.forEach((logo, index) => {
    if (logo) {
      // Use logo's aspect ratio to determine width while keeping height fixed
      const aspect = logo.width / logo.height;
      const badgeWidth = Math.max(logoHeight * aspect, baseSize * 0.5) + (padding * 2);
      badgeWidths[index] = badgeWidth;
    } else {
      // Fallback if logo couldn't be loaded
      badgeWidths[index] = baseSize + (padding * 2);
    }
  });
  
  // Calculate total canvas dimensions
  let canvasWidth, canvasHeight;
  if (isHorizontal) {
    // For horizontal layout, sum all badge widths
    canvasWidth = badgeWidths.reduce((sum, width) => sum + width, 0);
    canvasHeight = logoHeight + textHeight + verticalSpacing + (padding * 2);
  } else {
    // For vertical layout, use maximum badge width and stack heights
    canvasWidth = Math.max(...badgeWidths, baseSize);
    canvasHeight = (logoHeight + textHeight + verticalSpacing + (padding * 2)) * sourcesToShow.length;
  }
  
  // Create the canvas
  const canvas = createTempCanvas(canvasWidth, canvasHeight);
  const ctx = canvas.getContext('2d');
  
  if (!ctx) {
    throw new Error("Could not get canvas context");
  }
  
  // If we have a source image, load and draw it
  if (sourceImageUrl) {
    await new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve();
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${sourceImageUrl}`));
      img.src = sourceImageUrl;
    });
    return canvas;
  }
  
  // Apply background
  ctx.fillStyle = options.backgroundColor;
  ctx.globalAlpha = options.backgroundOpacity;
  
  if (options.borderRadius && options.borderRadius > 0) {
    // Draw rounded rectangle background
    console.log(`Drawing review badge with border radius: ${options.borderRadius}`);
    drawRoundedRect(ctx, 0, 0, canvas.width, canvas.height, options.borderRadius);
    ctx.fill();
  } else {
    // Draw rectangle background
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  
  // Apply border if specified
  if (options.borderWidth && options.borderWidth > 0) {
    ctx.strokeStyle = options.borderColor || '#000000';
    ctx.globalAlpha = options.borderOpacity || 1;
    ctx.lineWidth = options.borderWidth;
    
    if (options.borderRadius && options.borderRadius > 0) {
      // Draw rounded rectangle border
      const offset = options.borderWidth / 2;
      drawRoundedRect(
        ctx, 
        offset, 
        offset, 
        canvas.width - options.borderWidth, 
        canvas.height - options.borderWidth, 
        options.borderRadius - offset
      );
      ctx.stroke();
    } else {
      // Draw rectangle border
      ctx.strokeRect(
        options.borderWidth / 2,
        options.borderWidth / 2,
        canvas.width - options.borderWidth,
        canvas.height - options.borderWidth
      );
    }
  }
  
  // Apply shadow if enabled
  if (options.shadowEnabled) {
    ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = options.shadowBlur || 5;
    ctx.shadowOffsetX = options.shadowOffsetX || 2;
    ctx.shadowOffsetY = options.shadowOffsetY || 2;
  }
  
  // Text style setup
  ctx.globalAlpha = 1; // Reset alpha for text
  ctx.fillStyle = options.textColor || '#FFFFFF';
  ctx.font = `bold ${options.fontSize || Math.floor(textHeight * 0.7)}px ${options.fontFamily || 'Arial'}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // Draw badges with logos and text
  if (isHorizontal) {
    // Draw sources horizontally
    let currentX = 0;
    
    sourcesToShow.forEach((source, index) => {
      const badgeWidth = badgeWidths[index];
      const logo = logos[index];
      
      // Skip if no logo was loaded
      if (!logo) {
        currentX += badgeWidth;
        return;
      }
      
      // Apply source-specific background color if available
      const sourceName = source.name.toUpperCase();
      if (RATING_BG_COLOR_MAP[sourceName] && options.useBrandColors) {
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
        // Keep the global alpha the same as set for the general background
      } else {
        ctx.fillStyle = options.backgroundColor || '#000000';
      }
      
      // Draw individual badge background
      if (options.borderRadius && options.borderRadius > 0) {
        drawRoundedRect(ctx, currentX, 0, badgeWidth, canvasHeight, options.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(currentX, 0, badgeWidth, canvasHeight);
      }
      
      // Logo positioning
      const logoX = currentX + (badgeWidth / 2);
      const logoY = padding + (logoHeight / 2);
      
      // Calculate logo dimensions preserving aspect ratio
      const logoAspect = logo.width / logo.height;
      const logoDrawWidth = Math.min(logoHeight * logoAspect, badgeWidth - (padding * 2));
      const logoDrawHeight = logoDrawWidth / logoAspect;
      
      // Draw logo centered
      ctx.drawImage(
        logo,
        logoX - (logoDrawWidth / 2),
        logoY - (logoDrawHeight / 2),
        logoDrawWidth,
        logoDrawHeight
      );
      
      // Format the rating score
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
      
      // Draw rating text below the logo
      const textY = padding + logoHeight + verticalSpacing + (textHeight / 2);
      ctx.fillText(ratingText, logoX, textY);
      
      // Draw divider if needed
      if (options.showDividers && index < sourcesToShow.length - 1) {
        ctx.beginPath();
        ctx.moveTo(currentX + badgeWidth, padding);
        ctx.lineTo(currentX + badgeWidth, canvasHeight - padding);
        ctx.strokeStyle = options.dividerColor || options.textColor || '#FFFFFF';
        ctx.globalAlpha = 0.5; // Lighter divider
        ctx.stroke();
        ctx.globalAlpha = 1; // Reset alpha
      }
      
      // Move to next badge position
      currentX += badgeWidth;
    });
    
  } else {
    // Draw sources vertically
    let currentY = 0;
    
    sourcesToShow.forEach((source, index) => {
      const badgeHeight = logoHeight + textHeight + verticalSpacing + (padding * 2);
      const logo = logos[index];
      
      // Skip if no logo was loaded
      if (!logo) {
        currentY += badgeHeight;
        return;
      }
      
      // Apply source-specific background color if available
      const sourceName = source.name.toUpperCase();
      if (RATING_BG_COLOR_MAP[sourceName] && options.useBrandColors) {
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
        // Keep the global alpha the same as set for the general background
      } else {
        ctx.fillStyle = options.backgroundColor || '#000000';
      }
      
      // Draw individual badge background
      if (options.borderRadius && options.borderRadius > 0) {
        drawRoundedRect(ctx, 0, currentY, canvasWidth, badgeHeight, options.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(0, currentY, canvasWidth, badgeHeight);
      }
      
      // Logo positioning
      const logoX = canvasWidth / 2;
      const logoY = currentY + padding + (logoHeight / 2);
      
      // Calculate logo dimensions preserving aspect ratio
      const logoAspect = logo.width / logo.height;
      const logoDrawWidth = Math.min(logoHeight * logoAspect, canvasWidth - (padding * 2));
      const logoDrawHeight = logoDrawWidth / logoAspect;
      
      // Draw logo centered
      ctx.drawImage(
        logo,
        logoX - (logoDrawWidth / 2),
        logoY - (logoDrawHeight / 2),
        logoDrawWidth,
        logoDrawHeight
      );
      
      // Format the rating score
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
      
      // Draw rating text below the logo
      const textY = currentY + padding + logoHeight + verticalSpacing + (textHeight / 2);
      ctx.fillText(ratingText, logoX, textY);
      
      // Draw divider if needed
      if (options.showDividers && index < sourcesToShow.length - 1) {
        ctx.beginPath();
        ctx.moveTo(padding, currentY + badgeHeight);
        ctx.lineTo(canvasWidth - padding, currentY + badgeHeight);
        ctx.strokeStyle = options.dividerColor || options.textColor || '#FFFFFF';
        ctx.globalAlpha = 0.5; // Lighter divider
        ctx.stroke();
        ctx.globalAlpha = 1; // Reset alpha
      }
      
      // Move to next badge position
      currentY += badgeHeight;
    });
  }

  return canvas;
};