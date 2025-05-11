import { loadImage } from 'canvas';
import path from 'path';
import { 
  applyBackground, 
  applyBorder, 
  getFontFamily, 
  drawRoundedRect,
  projectRoot 
} from '../utils/canvasUtils.js';
import { RATING_LOGO_MAP, RATING_BG_COLOR_MAP } from '../utils/logoMapping.js';

/**
 * Renders a review badge
 * @param {Canvas} canvas - The canvas to render on
 * @param {Object} settings - The badge settings
 * @param {Object} metadata - The metadata for the badge
 * @param {Map} fonts - Available fonts
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
export async function renderReviewBadge(canvas, settings, metadata, fonts) {
  console.log('renderReviewBadge called with settings:', settings);
  console.log('and metadata:', metadata);
  
  // Either use the sources from settings directly (preferred) or from metadata
  const sources = settings.sources || metadata.rating || [];
  const isHorizontal = settings.displayFormat !== 'vertical';
  const maxSources = settings.maxSourcesToShow || sources.length;
  
  console.log(`Review badge renderer using maxSources=${maxSources}, displayFormat=${settings.displayFormat}`);
  console.log('sources before slicing:', sources);
  
  // Ensure we're getting a proper array and sort it if needed
  const sourcesToShow = Array.isArray(sources) ? sources.slice(0, maxSources) : [];
  console.log('sources after slicing to maxSources:', sourcesToShow);
  
  if (sourcesToShow.length === 0) {
    // No review data available - return empty badge
    return await renderTextBadge(canvas, settings, 'No Rating', fonts);
  }
  
  // Convert all ratings to 0-100 scale
  const normalizedSources = sourcesToShow.map(source => {
    let normalizedRating = source.rating;
    
    // Convert based on the outOf value
    if (source.outOf && source.outOf !== 100) {
      normalizedRating = Math.round((source.rating / source.outOf) * 100);
    }
    
    return {
      ...source,
      rating: normalizedRating,
      outOf: 100
    };
  });
  
  // Use the full size from settings, without any constraint
  const baseSize = settings.size || 80;
  
  // Use padding from settings instead of hardcoded value
  const padding = settings.padding || 8;
  const logoHeight = baseSize * 0.4; // Reduced from 0.5 to 0.4 for better spacing
  const textHeight = baseSize * 0.25; // 25% of badge size for text
  const verticalSpacing = baseSize * 0.08; // Reduced from 0.1 to 0.08 for tighter spacing
  
  // Pre-load logo images for sizing calculations
  const logoPromises = normalizedSources.map(async (source) => {
    try {
      const logoPath = RATING_LOGO_MAP[source.name.toUpperCase()] || 
                       RATING_LOGO_MAP[source.name] || 
                       null;
      if (!logoPath) {
        console.warn(`No logo found for rating source: ${source.name}`);
        return null;
      }
      
      const fullPath = path.join(projectRoot, 'src', 'assets', logoPath);
      console.log(`Loading logo for ${source.name} from: ${fullPath}`);
      return await loadImage(fullPath);
    } catch (error) {
      console.error(`Failed to load logo for ${source.name}:`, error);
      return null;
    }
  });
  
  let logos = [];
  try {
    logos = await Promise.all(logoPromises);
    console.log(`Loaded ${logos.filter(Boolean).length} logos out of ${logoPromises.length} requested`);
  } catch (error) {
    console.error('Error loading logos:', error);
  }
  
  // Calculate dimensions based on loaded logos
  let badgeWidths = [];
  
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
  
  // Create canvas with calculated dimensions
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  const ctx = canvas.getContext('2d');
  
  // Clear the canvas with transparent background
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw badges with logos and text
  if (isHorizontal) {
    // Draw sources horizontally
    let currentX = 0;
    
    sourcesToShow.forEach((source, index) => {
      const normalizedSource = normalizedSources[index];
      const badgeWidth = badgeWidths[index];
      const logo = logos[index];
      
      // Define position for this source
      const horLogoX = currentX + (badgeWidth / 2);
      const horLogoY = padding + (logoHeight / 2);
      
      // Apply source-specific background color if available
      const sourceName = source.name.toUpperCase();
      
      // Draw badge background with source-specific color if using brand colors
      if (settings.use_brand_colors && RATING_BG_COLOR_MAP[sourceName] && !settings.background_color) {
        console.log(`Using brand color for ${sourceName}: ${RATING_BG_COLOR_MAP[sourceName]}`);
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
      } else {
        // Ensure backgroundColor (camelCase) is set from background_color (snake_case)
        if (settings.background_color && !settings.backgroundColor) {
          settings.backgroundColor = settings.background_color;
        }
        ctx.fillStyle = settings.backgroundColor || '#000000';
      }
      
      ctx.globalAlpha = settings.transparency || settings.background_opacity || 1;
      
      // Draw badge background
      if (settings.borderRadius && settings.borderRadius > 0) {
        drawRoundedRect(ctx, currentX, 0, badgeWidth, canvasHeight, settings.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(currentX, 0, badgeWidth, canvasHeight);
      }
      
      // Add borders if needed
      if (settings.borderWidth && settings.borderWidth > 0) {
        ctx.strokeStyle = settings.borderColor || '#FFFFFF';
        ctx.lineWidth = settings.borderWidth;
        ctx.globalAlpha = settings.borderOpacity || 1;
        
        if (settings.borderRadius && settings.borderRadius > 0) {
          // Account for border width in rounded rect
          const offset = settings.borderWidth / 2;
          drawRoundedRect(
            ctx, 
            currentX + offset, 
            offset, 
            badgeWidth - settings.borderWidth, 
            canvasHeight - settings.borderWidth, 
            settings.borderRadius - offset
          );
          ctx.stroke();
        } else {
          // Draw simple rect border
          ctx.strokeRect(
            currentX + settings.borderWidth / 2,
            settings.borderWidth / 2,
            badgeWidth - settings.borderWidth,
            canvasHeight - settings.borderWidth
          );
        }
      }
      
      if (logo) {
        const logoAspect = logo.width / logo.height;
        const logoDrawWidth = Math.min(logoHeight * logoAspect, badgeWidth - (padding * 2));
        const logoDrawHeight = logoDrawWidth / logoAspect;
        
        ctx.globalAlpha = 1;
        ctx.drawImage(
          logo,
          horLogoX - (logoDrawWidth / 2),
          horLogoY - (logoDrawHeight / 2),
          logoDrawWidth,
          logoDrawHeight
        );
      } else {
        // Text fallback
        ctx.globalAlpha = 1;
        ctx.fillStyle = settings.textColor || '#FFFFFF';
        const fontFamily = getFontFamily(settings.fontFamily, fonts);
        ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${fontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(source.name, horLogoX, horLogoY);
      }
      
      // Draw rating text
      const textY = padding + logoHeight + verticalSpacing + (textHeight / 2);
      ctx.fillStyle = settings.textColor || '#FFFFFF';
      const fontFamily = getFontFamily(settings.fontFamily, fonts);
      ctx.font = `bold ${settings.fontSize || Math.floor(textHeight * 0.8)}px ${fontFamily}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const ratingText = `${normalizedSource.rating}%`;
      ctx.fillText(ratingText, horLogoX, textY);
      
      // Add a visual divider between sources (except for the last one)
      if (index < sourcesToShow.length - 1) {
        ctx.strokeStyle = settings.textColor || '#FFFFFF';
        ctx.globalAlpha = 0.5;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(currentX + badgeWidth, padding);
        ctx.lineTo(currentX + badgeWidth, canvasHeight - padding);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
      
      currentX += badgeWidth;
    });
  } else {
    // Draw sources vertically
    let currentY = 0;
    
    sourcesToShow.forEach((source, index) => {
      const normalizedSource = normalizedSources[index];
      const badgeHeight = logoHeight + textHeight + verticalSpacing + (padding * 2);
      const logo = logos[index];
      
      // Define position for this source
      const vertLogoX = canvasWidth / 2;
      const vertLogoY = currentY + padding + (logoHeight / 2);
      
      // Apply source-specific background color if using brand colors
      const sourceName = source.name.toUpperCase();
      
      if (settings.use_brand_colors && RATING_BG_COLOR_MAP[sourceName] && !settings.background_color) {
        console.log(`Using brand color for ${sourceName}: ${RATING_BG_COLOR_MAP[sourceName]}`);
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
      } else {
        // Ensure backgroundColor (camelCase) is set from background_color (snake_case)
        if (settings.background_color && !settings.backgroundColor) {
          settings.backgroundColor = settings.background_color;
        }
        ctx.fillStyle = settings.backgroundColor || '#000000';
      }
      
      ctx.globalAlpha = settings.transparency || settings.background_opacity || 1;
      
      // Draw badge background
      if (settings.borderRadius && settings.borderRadius > 0) {
        drawRoundedRect(ctx, 0, currentY, canvasWidth, badgeHeight, settings.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(0, currentY, canvasWidth, badgeHeight);
      }
      
      // Add borders if needed
      if (settings.borderWidth && settings.borderWidth > 0) {
        ctx.strokeStyle = settings.borderColor || '#FFFFFF';
        ctx.lineWidth = settings.borderWidth;
        ctx.globalAlpha = settings.borderOpacity || 1;
        
        if (settings.borderRadius && settings.borderRadius > 0) {
          // Account for border width in rounded rect
          const offset = settings.borderWidth / 2;
          drawRoundedRect(
            ctx, 
            offset, 
            currentY + offset, 
            canvasWidth - settings.borderWidth, 
            badgeHeight - settings.borderWidth, 
            settings.borderRadius - offset
          );
          ctx.stroke();
        } else {
          // Draw simple rect border
          ctx.strokeRect(
            settings.borderWidth / 2,
            currentY + settings.borderWidth / 2,
            canvasWidth - settings.borderWidth,
            badgeHeight - settings.borderWidth
          );
        }
      }
      
      // Draw logo or text fallback
      if (logo) {
        const logoAspect = logo.width / logo.height;
        const logoDrawWidth = Math.min(logoHeight * logoAspect, canvasWidth - (padding * 2));
        const logoDrawHeight = logoDrawWidth / logoAspect;
        
        ctx.globalAlpha = 1;
        ctx.drawImage(
          logo,
          vertLogoX - (logoDrawWidth / 2),
          vertLogoY - (logoDrawHeight / 2),
          logoDrawWidth,
          logoDrawHeight
        );
      } else {
        // Text fallback
        ctx.globalAlpha = 1;
        ctx.fillStyle = settings.textColor || '#FFFFFF';
        const fontFamily = getFontFamily(settings.fontFamily, fonts);
        ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${fontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(source.name, vertLogoX, vertLogoY);
      }
      
      // Draw rating text
      const textY = currentY + padding + logoHeight + verticalSpacing + (textHeight / 2);
      ctx.fillStyle = settings.textColor || '#FFFFFF';
      const fontFamily = getFontFamily(settings.fontFamily, fonts);
      const calculatedFontSize = settings.fontSize || Math.floor(textHeight * 0.8);
      // Ensure we're always using bold font weight
      ctx.font = `bold ${calculatedFontSize}px ${fontFamily}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const ratingText = `${normalizedSource.rating}%`;
      ctx.fillText(ratingText, vertLogoX, textY);
      
      // Add a visual divider between sources (except for the last one)
      if (index < sourcesToShow.length - 1) {
        ctx.strokeStyle = settings.textColor || '#FFFFFF';
        ctx.globalAlpha = 0.5;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, currentY + badgeHeight);
        ctx.lineTo(canvasWidth - padding, currentY + badgeHeight);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
      
      currentY += badgeHeight;
    });
  }
  
  return canvas.toBuffer('image/png');
}

/**
 * Renders a badge with text
 * @param {Canvas} canvas - The canvas to render on
 * @param {Object} settings - The badge settings
 * @param {string} text - The text to display
 * @param {Map} fonts - Available fonts
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
async function renderTextBadge(canvas, settings, text, fonts) {
  const size = settings.size || 100;
  // Create canvas with proportional dimensions based on size
  const width = size * 2;
  const height = size;
  
  // Resize canvas
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Apply background
  applyBackground(ctx, canvas.width, canvas.height, settings);

  // Apply border if specified
  if (settings.borderWidth > 0) {
    applyBorder(ctx, canvas.width, canvas.height, settings);
  }

  // Draw text
  ctx.fillStyle = settings.textColor || '#FFFFFF';
  const fontSize = settings.fontSize || size / 3;
  
  // Use a font that's available, fallback to system fonts
  const fontFamily = getFontFamily(settings.fontFamily, fonts);
  // Always use bold font weight for consistency with preview
  ctx.font = `bold ${fontSize}px ${fontFamily}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, width / 2, height / 2);

  return canvas.toBuffer('image/png');
}