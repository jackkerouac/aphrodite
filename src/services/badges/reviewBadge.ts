import { ReviewBadgeSettings, ReviewSource } from '@/components/badges/types/ReviewBadge';
import { 
  createTempCanvas, 
  drawRoundedRect, 
  formatRating, 
  RATING_LOGO_MAP, 
  RATING_BG_COLOR_MAP, 
  loadImage 
} from './utils/index';

// Import debug utilities
import { logFrontendBadgeSettings, evaluateSourceColors } from '@/debug-badge-rendering';

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
  // Debug logging for frontend review badge settings
  logFrontendBadgeSettings('review', options);
  
  // Log opacity setting for debugging
  console.log(`Rendering review badge with opacity: ${options.backgroundOpacity}`);
  console.log(`Using brand colors? ${options.useBrandColors !== false}`);
  
  const isHorizontal = options.displayFormat !== 'vertical';
  const sources = options.sources || [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ];
  const maxSources = options.maxSourcesToShow || 2;
  const sourcesToShow = sources.slice(0, maxSources);
  
  // Use the base size for calculations - allow full range up to 500
  const baseSize = options.size || 100;
  
  // Constants for layout
  const padding = 10; // Padding around each badge
  const logoHeight = baseSize * 0.55; // 55% of badge size for logo (reduced slightly)
  const textHeight = baseSize * 0.3; // 30% of badge size for text
  const verticalSpacing = baseSize * 0.15; // 15% spacing between logo and text (increased)
  
  // Pre-load logo images for sizing calculations
  const logoPromises = sourcesToShow.map(async (source) => {
    try {
      // Try to get the logo from our map first
      const logoPath = RATING_LOGO_MAP[source.name.toUpperCase()] || 
                       RATING_LOGO_MAP[source.name] || 
                       null;
      if (!logoPath) {
        console.warn(`No logo found for rating source: ${source.name}`);
        return null;
      }
      
      return await loadImage(logoPath);
    } catch (error) {
      console.error(`Failed to load logo for ${source.name}:`, error);
      return null;
    }
  });
  
  let logos: (HTMLImageElement | null)[] = [];
  try {
    logos = await Promise.all(logoPromises);
    console.log(`Loaded ${logos.filter(Boolean).length} logos out of ${logoPromises.length} requested`);
  } catch (error) {
    console.error('Error loading logos:', error);
    // Continue with empty logos array - we'll use fallback text display
  }
  
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
  
  // Clear the canvas with transparent background
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw the main background if we're not using brand colors
  if (!options.useBrandColors) {
    ctx.fillStyle = options.backgroundColor;
    ctx.globalAlpha = options.backgroundOpacity;
    
    if (options.borderRadius && options.borderRadius > 0) {
      // Draw rounded rectangle background
      drawRoundedRect(ctx, 0, 0, canvas.width, canvas.height, options.borderRadius);
      ctx.fill();
    } else {
      // Draw rectangle background
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  }
  
  // Draw border if specified
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
  
  // Reset global alpha for subsequent drawing operations
  ctx.globalAlpha = 1;
  
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
  
  // Increase the font weight and size slightly for better visibility
  ctx.font = `bold ${options.fontSize || Math.floor(textHeight * 0.8)}px ${options.fontFamily || 'Arial, sans-serif'}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // Add slight stroke to text for better contrast
  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 0.5;
  
  // Apply a subtle text shadow for better readability regardless of background
  // This helps with text contrast on any background
  ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
  ctx.shadowBlur = 2;
  ctx.shadowOffsetX = 1;
  ctx.shadowOffsetY = 1;
  
  // Override with user shadow settings if shadow is enabled
  if (options.shadowEnabled) {
    ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = options.shadowBlur || 5;
    ctx.shadowOffsetX = options.shadowOffsetX || 2;
    ctx.shadowOffsetY = options.shadowOffsetY || 2;
  }
  
  // Draw badges with logos and text
  if (isHorizontal) {
    // Draw sources horizontally
    let currentX = 0;
    
    sourcesToShow.forEach((source, index) => {
      const badgeWidth = badgeWidths[index];
      const logo = logos[index];
      
      // Define position for this source (with unique variable names)
      const horLogoX = currentX + (badgeWidth / 2);
      const horLogoY = padding + (logoHeight / 2);
      
      // If no logo was loaded, draw a text fallback instead
      if (!logo) {
        // Reset alpha for text
        ctx.globalAlpha = 1;
        // Draw the source name as fallback
        ctx.fillStyle = options.textColor || '#FFFFFF';
        ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${options.fontFamily || 'Arial, sans-serif'}`;
        ctx.fillText(source.name, horLogoX, horLogoY);
        
        // Format the rating
        let ratingText = formatRating(source);
        
        // Draw rating text below
        const textY = padding + logoHeight + verticalSpacing + (textHeight / 2);
        ctx.fillText(ratingText, horLogoX, textY);
        
        // Move to next position
        currentX += badgeWidth;
        // Skip to next iteration
        return;
      }
      
      // Apply source-specific background color if available
      const sourceName = source.name.toUpperCase();
      
      // Debug color resolution for this source
      evaluateSourceColors(sourceName, options);
      
      // Set the opacity for individual badge backgrounds
      ctx.globalAlpha = options.backgroundOpacity;
      
      if (options.useBrandColors && RATING_BG_COLOR_MAP[sourceName]) {
        // If using brand colors, use the color from the map
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
      } else if (options.useBrandColors) {
        // If using brand colors but no matching color in the map
        ctx.fillStyle = options.backgroundColor || '#000000';
      } else {
        // If we already drew the main background and not using brand colors,
        // we don't need to draw individual backgrounds again
        ctx.fillStyle = 'transparent';
        ctx.globalAlpha = 0;
      }
      
      // Draw individual badge background
      if (options.borderRadius && options.borderRadius > 0) {
        drawRoundedRect(ctx, currentX, 0, badgeWidth, canvasHeight, options.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(currentX, 0, badgeWidth, canvasHeight);
      }
      
      // Calculate logo dimensions preserving aspect ratio
      const logoAspect = logo.width / logo.height;
      const logoDrawWidth = Math.min(logoHeight * logoAspect, badgeWidth - (padding * 2));
      const logoDrawHeight = logoDrawWidth / logoAspect;
      
      // Reset global alpha for logo rendering
      ctx.globalAlpha = 1;
      
      // Draw logo centered
      ctx.drawImage(
        logo,
        horLogoX - (logoDrawWidth / 2),
        horLogoY - (logoDrawHeight / 2),
        logoDrawWidth,
        logoDrawHeight
      );
      
      // Format the rating score
      let ratingText = formatRating(source);
      
      // Draw rating text below the logo
      const textY = padding + logoHeight + verticalSpacing + (textHeight / 2);
      
      // Reset global alpha for text rendering to ensure full opacity
      ctx.globalAlpha = 1;
      // Ensure text color is set
      ctx.fillStyle = options.textColor || '#FFFFFF';
      
      // Draw text with outline for better visibility
      ctx.lineWidth = 2;
      ctx.strokeText(ratingText, horLogoX, textY);
      ctx.fillText(ratingText, horLogoX, textY);
      
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
      
      // Define position for this source (with unique variable names)
      const vertLogoX = canvasWidth / 2;
      const vertLogoY = currentY + padding + (logoHeight / 2);
      
      // If no logo was loaded, draw a text fallback instead
      if (!logo) {
        // Reset alpha for text
        ctx.globalAlpha = 1;
        // Draw the source name as fallback
        ctx.fillStyle = options.textColor || '#FFFFFF';
        ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${options.fontFamily || 'Arial, sans-serif'}`;
        ctx.fillText(source.name, vertLogoX, vertLogoY);
        
        // Format the rating
        let ratingText = formatRating(source);
        
        // Draw rating text below
        const textY = currentY + padding + logoHeight + verticalSpacing + (textHeight / 2);
        ctx.fillText(ratingText, vertLogoX, textY);
        
        // Move to next position
        currentY += badgeHeight;
        // Skip to next iteration
        return;
      }
      
      // Apply source-specific background color if available
      const sourceName = source.name.toUpperCase();
      
      // Set the opacity for individual badge backgrounds
      ctx.globalAlpha = options.backgroundOpacity;
      
      if (options.useBrandColors && RATING_BG_COLOR_MAP[sourceName]) {
        // If using brand colors, use the color from the map
        ctx.fillStyle = RATING_BG_COLOR_MAP[sourceName];
      } else if (options.useBrandColors) {
        // If using brand colors but no matching color in the map
        ctx.fillStyle = options.backgroundColor || '#000000';
      } else {
        // If we already drew the main background and not using brand colors,
        // we don't need to draw individual backgrounds again
        ctx.fillStyle = 'transparent';
        ctx.globalAlpha = 0;
      }
      
      // Draw individual badge background
      if (options.borderRadius && options.borderRadius > 0) {
        drawRoundedRect(ctx, 0, currentY, canvasWidth, badgeHeight, options.borderRadius);
        ctx.fill();
      } else {
        ctx.fillRect(0, currentY, canvasWidth, badgeHeight);
      }
      
      // Calculate logo dimensions preserving aspect ratio
      const logoAspect = logo.width / logo.height;
      const logoDrawWidth = Math.min(logoHeight * logoAspect, canvasWidth - (padding * 2));
      const logoDrawHeight = logoDrawWidth / logoAspect;
      
      // Reset global alpha for logo rendering
      ctx.globalAlpha = 1;
      
      // Draw logo centered
      ctx.drawImage(
        logo,
        vertLogoX - (logoDrawWidth / 2),
        vertLogoY - (logoDrawHeight / 2),
        logoDrawWidth,
        logoDrawHeight
      );
      
      // Format the rating score
      let ratingText = formatRating(source);
      
      // Draw rating text below the logo
      const textY = currentY + padding + logoHeight + verticalSpacing + (textHeight / 2);
      
      // Reset global alpha for text rendering to ensure full opacity
      ctx.globalAlpha = 1;
      // Ensure text color is set
      ctx.fillStyle = options.textColor || '#FFFFFF';
      
      // Draw text with outline for better visibility
      ctx.lineWidth = 2;
      ctx.strokeText(ratingText, vertLogoX, textY);
      ctx.fillText(ratingText, vertLogoX, textY);
      
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