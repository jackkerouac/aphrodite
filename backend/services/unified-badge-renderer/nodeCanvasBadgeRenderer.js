import { createCanvas, loadImage } from 'canvas';
import path from 'path';
import fs from 'fs/promises';
import sharp from 'sharp';
import logger from '../../lib/logger.js';

// Constants for badge rendering
const AUDIO_CODEC_ICONS_DIR = path.join(process.cwd(), 'public', 'assets', 'audio_codec', 'compact');
const RESOLUTION_ICONS_DIR = path.join(process.cwd(), 'public', 'assets', 'resolution');
const REVIEW_SOURCE_ICONS_DIR = path.join(process.cwd(), 'public', 'assets', 'review_sources');

/**
 * Apply badges to a poster image
 * @param {Buffer} posterBuffer - The poster image buffer
 * @param {Array} badges - Array of badge settings
 * @returns {Promise<Buffer>} - Modified poster buffer
 */
export async function applyBadgesToPoster(posterBuffer, badges) {
  try {
    // Load the poster image
    const poster = await sharp(posterBuffer);
    const posterMetadata = await poster.metadata();
    
    // Create a canvas with the same dimensions as the poster
    const canvas = createCanvas(posterMetadata.width, posterMetadata.height);
    const ctx = canvas.getContext('2d');
    
    // Draw the poster onto the canvas
    const posterImage = await loadImage(posterBuffer);
    ctx.drawImage(posterImage, 0, 0, posterMetadata.width, posterMetadata.height);
    
    // Sort badges by stacking order to ensure they are rendered in the correct order
    const sortedBadges = [...badges].sort((a, b) => {
      const stackingOrderA = a.stacking_order || 0;
      const stackingOrderB = b.stacking_order || 0;
      return stackingOrderA - stackingOrderB;
    });
    
    // Apply each badge
    for (const badge of sortedBadges) {
      logger.info(`Rendering badge: ${badge.badge_type}`);
      await renderBadge(ctx, badge, posterMetadata.width, posterMetadata.height);
    }
    
    // Convert canvas to buffer
    const modifiedPosterBuffer = canvas.toBuffer('image/png');
    
    return modifiedPosterBuffer;
  } catch (error) {
    logger.error(`Error applying badges to poster: ${error.message}`);
    throw error;
  }
}

/**
 * Render a badge on the canvas
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} badge - Badge settings
 * @param {number} posterWidth - Poster width
 * @param {number} posterHeight - Poster height
 * @returns {Promise<void>}
 */
async function renderBadge(ctx, badge, posterWidth, posterHeight) {
  try {
    // Create a temporary canvas for the badge
    const badgeCanvas = createCanvas(300, 300); // Start with a reasonable size
    const badgeCtx = badgeCanvas.getContext('2d');
    
    // Draw the badge based on type
    switch (badge.badge_type) {
      case 'audio':
        await drawAudioBadge(badgeCtx, badge);
        break;
      case 'resolution':
        await drawResolutionBadge(badgeCtx, badge);
        break;
      case 'review':
        await drawReviewBadge(badgeCtx, badge);
        break;
      default:
        logger.warn(`Unknown badge type: ${badge.badge_type}`);
        return;
    }
    
    // Calculate position on the poster
    const position = calculateBadgePosition(
      badge.badge_position,
      badgeCanvas.width,
      badgeCanvas.height,
      posterWidth,
      posterHeight,
      badge.edge_padding || 20
    );
    
    // Draw the badge onto the main canvas
    ctx.drawImage(badgeCanvas, position.x, position.y);
    
    logger.info(`Badge rendered at position (${position.x}, ${position.y})`);
  } catch (error) {
    logger.error(`Error rendering badge: ${error.message}`);
  }
}

/**
 * Draw an audio badge
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} badge - Badge settings
 * @returns {Promise<void>}
 */
async function drawAudioBadge(ctx, badgeSettings) {
  try {
    const properties = badgeSettings.properties || {};
    const codecType = properties.codec_type || 'dolby_atmos';
    
    // Load the codec icon
    const iconPath = await getAudioCodecIconPath(codecType);
    const image = await loadImage(iconPath);
    
    // Resize the canvas to match the badge size
    resizeCanvasForImage(ctx.canvas, image, badgeSettings.badge_size);
    
    // Draw background
    drawBadgeBackground(ctx, badgeSettings);
    
    // Draw the image with proper scaling
    const padding = 10;
    const drawWidth = ctx.canvas.width - (padding * 2);
    const drawHeight = ctx.canvas.height - (padding * 2);
    
    ctx.drawImage(image, padding, padding, drawWidth, drawHeight);
    
    logger.info(`Audio badge drawn: ${codecType}, size: ${badgeSettings.badge_size}`);
  } catch (error) {
    logger.error(`Error drawing audio badge: ${error.message}`);
    // Draw fallback text
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '20px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('AUDIO', ctx.canvas.width / 2, ctx.canvas.height / 2);
  }
}

/**
 * Draw a resolution badge
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} badge - Badge settings
 * @returns {Promise<void>}
 */
async function drawResolutionBadge(ctx, badgeSettings) {
  try {
    const properties = badgeSettings.properties || {};
    const resolutionType = properties.resolution_type || '4k';
    
    // Load the resolution icon
    const iconPath = await getResolutionIconPath(resolutionType);
    const image = await loadImage(iconPath);
    
    // Resize the canvas to match the badge size
    resizeCanvasForImage(ctx.canvas, image, badgeSettings.badge_size);
    
    // Draw background
    drawBadgeBackground(ctx, badgeSettings);
    
    // Draw the image with proper scaling
    const padding = 10;
    const drawWidth = ctx.canvas.width - (padding * 2);
    const drawHeight = ctx.canvas.height - (padding * 2);
    
    ctx.drawImage(image, padding, padding, drawWidth, drawHeight);
    
    logger.info(`Resolution badge drawn: ${resolutionType}, size: ${badgeSettings.badge_size}`);
  } catch (error) {
    logger.error(`Error drawing resolution badge: ${error.message}`);
    // Draw fallback text
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '20px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('4K', ctx.canvas.width / 2, ctx.canvas.height / 2);
  }
}

/**
 * Draw a review badge
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} badge - Badge settings
 * @returns {Promise<void>}
 */
async function drawReviewBadge(ctx, badgeSettings) {
  try {
    const properties = badgeSettings.properties || {};
    const reviewSources = properties.review_sources || ['imdb'];
    const displayFormat = badgeSettings.display_format || 'vertical';
    const reviewScores = badgeSettings.reviewScores || [
      { source: 'imdb', rating: 7.5, outOf: 10 }
    ];
    
    // Size and padding settings
    const badgeSize = badgeSettings.badge_size || 100;
    const padding = Math.max(10, badgeSize * 0.05);
    
    // Calculate dimensions based on display format and number of sources
    let totalWidth, totalHeight;
    
    if (displayFormat === 'horizontal') {
      // Horizontal layout
      const iconHeight = badgeSize * 0.4;
      const iconSpacing = badgeSize * 0.15;
      const scoreFontSize = Math.max(badgeSize * 0.3, 14);
      
      // Calculate total width
      let currentX = padding;
      for (let i = 0; i < reviewSources.length; i++) {
        const iconWidth = iconHeight * 1.5; // Estimated aspect ratio
        
        // Add spacing between sources
        if (i > 0) {
          currentX += iconSpacing;
        }
        
        currentX += iconWidth + (padding * 2);
      }
      
      totalWidth = currentX;
      totalHeight = iconHeight + (scoreFontSize * 1.2) + (padding * 2);
    } else {
      // Vertical layout
      const logoHeight = badgeSize * 0.3;
      const scoreHeight = badgeSize * 0.3;
      const sourceSpacing = badgeSize * 0.15;
      const logoScoreSpacing = badgeSize * 0.12;
      const logoWidth = badgeSize * 0.55;
      
      totalWidth = logoWidth + (padding * 2);
      totalHeight = padding + 
        (reviewSources.length * (logoHeight + logoScoreSpacing + scoreHeight + sourceSpacing)) - 
        sourceSpacing + 
        padding;
    }
    
    // Resize canvas
    ctx.canvas.width = totalWidth;
    ctx.canvas.height = totalHeight;
    
    // Draw background
    drawBadgeBackground(ctx, badgeSettings);
    
    // Draw review sources
    const iconPromises = reviewSources.map(async (source) => {
      try {
        const iconPath = await getReviewSourceIconPath(source);
        return { source, image: await loadImage(iconPath) };
      } catch (error) {
        logger.error(`Failed to load icon for ${source}: ${error.message}`);
        return { source, image: null };
      }
    });
    
    const sourceIcons = await Promise.all(iconPromises);
    
    // Draw the content based on layout
    if (displayFormat === 'horizontal') {
      // Horizontal layout rendering
      await renderHorizontalReviewBadge(ctx, sourceIcons, reviewScores, badgeSettings);
    } else {
      // Vertical layout rendering
      await renderVerticalReviewBadge(ctx, sourceIcons, reviewScores, badgeSettings);
    }
    
    logger.info(`Review badge drawn: ${reviewSources.join(', ')}, format: ${displayFormat}`);
  } catch (error) {
    logger.error(`Error drawing review badge: ${error.message}`);
    // Draw fallback text
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '20px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('7.5/10', ctx.canvas.width / 2, ctx.canvas.height / 2);
  }
}

/**
 * Render review badge in horizontal layout
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Array} sourceIcons - Array of loaded icons
 * @param {Array} reviewScores - Array of review scores
 * @param {Object} badgeSettings - Badge settings
 * @returns {Promise<void>}
 */
async function renderHorizontalReviewBadge(ctx, sourceIcons, reviewScores, badgeSettings) {
  const badgeSize = badgeSettings.badge_size || 100;
  const padding = Math.max(10, badgeSize * 0.05);
  const iconHeight = badgeSize * 0.4;
  const iconSpacing = badgeSize * 0.15;
  const scoreFontSize = Math.max(badgeSize * 0.3, 14);
  
  let currentX = padding;
  
  sourceIcons.forEach((sourceIcon, index) => {
    const source = sourceIcon.source;
    const score = reviewScores.find(s => s.source === source) || { rating: 7.5, outOf: 10 };
    
    // Add spacing between sources
    if (index > 0) {
      currentX += iconSpacing;
    }
    
    // Draw source icon
    if (sourceIcon.image) {
      const aspectRatio = sourceIcon.image.width / sourceIcon.image.height;
      const iconWidth = iconHeight * aspectRatio;
      
      ctx.drawImage(
        sourceIcon.image,
        currentX,
        padding,
        iconWidth,
        iconHeight
      );
      
      // Move to next position based on icon width
      currentX += iconWidth + padding;
    } else {
      // Fallback if icon not available
      const iconWidth = scoreFontSize * 3;
      
      ctx.font = `bold ${scoreFontSize * 0.6}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(
        source.toUpperCase(),
        currentX + (iconWidth / 2),
        padding + (iconHeight / 2)
      );
      
      // Move to next position
      currentX += iconWidth + padding;
    }
    
    // Draw score below icon
    ctx.font = `bold ${scoreFontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#FFFFFF';
    
    // Format score
    let scoreText;
    if (source === 'imdb' || source.startsWith('letterboxd') || source === 'tmdb' || source === 'mal') {
      scoreText = `${score.rating.toFixed(1)}`;
    } else {
      // For percentage-based sources like RT and Metacritic
      scoreText = `${Math.round(score.rating)}%`;
    }
    
    ctx.fillText(
      scoreText,
      currentX - (padding + scoreFontSize),
      padding + iconHeight + (padding * 0.5)
    );
  });
}

/**
 * Render review badge in vertical layout
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Array} sourceIcons - Array of loaded icons
 * @param {Array} reviewScores - Array of review scores
 * @param {Object} badgeSettings - Badge settings
 * @returns {Promise<void>}
 */
async function renderVerticalReviewBadge(ctx, sourceIcons, reviewScores, badgeSettings) {
  const badgeSize = badgeSettings.badge_size || 100;
  const padding = Math.max(10, badgeSize * 0.05);
  const logoWidth = badgeSize * 0.55;
  const logoHeight = badgeSize * 0.3;
  const scoreHeight = badgeSize * 0.3;
  const sourceSpacing = badgeSize * 0.15;
  const logoScoreSpacing = badgeSize * 0.12;
  
  let currentY = padding;
  
  sourceIcons.forEach((sourceIcon, index) => {
    const source = sourceIcon.source;
    const score = reviewScores.find(s => s.source === source) || { rating: 7.5, outOf: 10 };
    
    // Center position for this source
    const centerX = ctx.canvas.width / 2;
    
    // Draw source icon on top
    if (sourceIcon.image) {
      const aspectRatio = sourceIcon.image.width / sourceIcon.image.height;
      const iconWidth = logoHeight * aspectRatio;
      
      ctx.drawImage(
        sourceIcon.image,
        centerX - (iconWidth / 2),
        currentY,
        iconWidth,
        logoHeight
      );
    } else {
      // Fallback if icon not available
      ctx.font = `bold ${badgeSize * 0.18}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(
        source.toUpperCase(),
        centerX,
        currentY + (logoHeight / 2)
      );
    }
    
    // Draw score below icon
    const scoreFontSize = Math.max(badgeSize * 0.3, 14);
    ctx.font = `bold ${scoreFontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#FFFFFF';
    
    // Format score
    let scoreText;
    if (source === 'imdb' || source.startsWith('letterboxd') || source === 'tmdb' || source === 'mal') {
      scoreText = `${score.rating.toFixed(1)}`;
    } else {
      // For percentage-based sources like RT and Metacritic
      scoreText = `${Math.round(score.rating)}%`;
    }
    
    ctx.fillText(
      scoreText,
      centerX,
      currentY + logoHeight + logoScoreSpacing + (scoreHeight / 2)
    );
    
    // Move to next position
    currentY += logoHeight + logoScoreSpacing + scoreHeight + sourceSpacing;
  });
}

/**
 * Draw the background for a badge
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} settings - Badge settings
 * @returns {void}
 */
function drawBadgeBackground(ctx, settings) {
  // Clear the canvas
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  
  // Set up shadow if enabled
  if (settings.shadow_enabled) {
    ctx.shadowColor = settings.shadow_color || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = settings.shadow_blur || 5;
    ctx.shadowOffsetX = settings.shadow_offset_x || 2;
    ctx.shadowOffsetY = settings.shadow_offset_y || 2;
  }
  
  // Draw rounded rectangle for background
  const borderRadius = settings.border_radius || 5;
  
  ctx.beginPath();
  ctx.moveTo(borderRadius, 0);
  ctx.lineTo(ctx.canvas.width - borderRadius, 0);
  ctx.quadraticCurveTo(ctx.canvas.width, 0, ctx.canvas.width, borderRadius);
  ctx.lineTo(ctx.canvas.width, ctx.canvas.height - borderRadius);
  ctx.quadraticCurveTo(ctx.canvas.width, ctx.canvas.height, ctx.canvas.width - borderRadius, ctx.canvas.height);
  ctx.lineTo(borderRadius, ctx.canvas.height);
  ctx.quadraticCurveTo(0, ctx.canvas.height, 0, ctx.canvas.height - borderRadius);
  ctx.lineTo(0, borderRadius);
  ctx.quadraticCurveTo(0, 0, borderRadius, 0);
  ctx.closePath();
  
  // Background fill with opacity
  const bgColor = settings.background_color || '#000000';
  // Convert percentage opacity to decimal
  let bgOpacity = settings.background_opacity;
  if (bgOpacity > 1 && bgOpacity <= 100) {
    bgOpacity = bgOpacity / 100;
  } else if (bgOpacity > 100) {
    // Handle extended percentage format (8000 = 80%)
    bgOpacity = bgOpacity / 10000;
  }
  const backgroundColor = hexToRgba(bgColor, bgOpacity);
  
  ctx.fillStyle = backgroundColor;
  ctx.fill();
  
  // Border
  if (settings.border_size && settings.border_size > 0) {
    ctx.strokeStyle = settings.border_color || '#FFFFFF';
    ctx.lineWidth = settings.border_size;
    ctx.stroke();
  }
  
  // Reset shadow
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;
}

/**
 * Calculate badge position on the poster
 * @param {string} position - Badge position
 * @param {number} badgeWidth - Badge width
 * @param {number} badgeHeight - Badge height
 * @param {number} posterWidth - Poster width
 * @param {number} posterHeight - Poster height
 * @param {number} padding - Padding from edge
 * @returns {Object} - Position coordinates
 */
function calculateBadgePosition(position, badgeWidth, badgeHeight, posterWidth, posterHeight, padding = 20) {
  let x = 0, y = 0;
  
  switch (position) {
    case 'top-left':
      x = padding;
      y = padding;
      break;
    case 'top-center':
      x = (posterWidth - badgeWidth) / 2;
      y = padding;
      break;
    case 'top-right':
      x = posterWidth - badgeWidth - padding;
      y = padding;
      break;
    case 'center-left':
    case 'middle-left':
      x = padding;
      y = (posterHeight - badgeHeight) / 2;
      break;
    case 'center':
      x = (posterWidth - badgeWidth) / 2;
      y = (posterHeight - badgeHeight) / 2;
      break;
    case 'center-right':
    case 'middle-right':
      x = posterWidth - badgeWidth - padding;
      y = (posterHeight - badgeHeight) / 2;
      break;
    case 'bottom-left':
      x = padding;
      y = posterHeight - badgeHeight - padding;
      break;
    case 'bottom-center':
      x = (posterWidth - badgeWidth) / 2;
      y = posterHeight - badgeHeight - padding;
      break;
    case 'bottom-right':
      x = posterWidth - badgeWidth - padding;
      y = posterHeight - badgeHeight - padding;
      break;
    default:
      // Default to top-left
      x = padding;
      y = padding;
  }
  
  // Ensure badge is within bounds
  x = Math.max(0, Math.min(x, posterWidth - badgeWidth));
  y = Math.max(0, Math.min(y, posterHeight - badgeHeight));
  
  return { x, y };
}

/**
 * Resize canvas to fit the badge based on the source image and desired size
 * @param {Canvas} canvas - Canvas element
 * @param {Image} image - Source image
 * @param {number} badgeSize - Badge size setting
 * @returns {void}
 */
function resizeCanvasForImage(canvas, image, badgeSize) {
  // Calculate scale based on badge size (100 is the default size)
  const scale = badgeSize / 100;
  
  // Calculate new dimensions
  const drawWidth = Math.round(image.width * scale);
  const drawHeight = Math.round(image.height * scale);
  
  // Add padding
  const padding = 10;
  canvas.width = drawWidth + (padding * 2);
  canvas.height = drawHeight + (padding * 2);
}

/**
 * Convert a hex color to rgba
 * @param {string} hex - Hex color string
 * @param {number} alpha - Alpha value (0-1)
 * @returns {string} - RGBA color string
 */
function hexToRgba(hex, alpha = 1) {
  let r, g, b;
  
  // Default to black if hex is invalid
  if (!hex || typeof hex !== 'string') {
    return `rgba(0, 0, 0, ${alpha})`;
  }
  
  // Remove the # if present
  hex = hex.replace('#', '');
  
  // Handle shorthand hex
  if (hex.length === 3) {
    r = parseInt(hex.charAt(0) + hex.charAt(0), 16);
    g = parseInt(hex.charAt(1) + hex.charAt(1), 16);
    b = parseInt(hex.charAt(2) + hex.charAt(2), 16);
  } else {
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }
  
  // Handle NaN values
  r = isNaN(r) ? 0 : r;
  g = isNaN(g) ? 0 : g;
  b = isNaN(b) ? 0 : b;
  
  // Ensure alpha is in range 0-1
  alpha = Math.max(0, Math.min(1, alpha));
  
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Get the path to an audio codec icon
 * @param {string} codecType - Audio codec type
 * @returns {Promise<string>} - Path to the icon
 */
async function getAudioCodecIconPath(codecType) {
  try {
    // Check if the icon exists
    const iconPath = path.join(AUDIO_CODEC_ICONS_DIR, `${codecType}.png`);
    
    try {
      await fs.access(iconPath);
      return iconPath;
    } catch {
      // Try lowercase version
      const lowerIconPath = path.join(AUDIO_CODEC_ICONS_DIR, `${codecType.toLowerCase()}.png`);
      try {
        await fs.access(lowerIconPath);
        return lowerIconPath;
      } catch {
        // Return default icon
        return path.join(AUDIO_CODEC_ICONS_DIR, 'dolby_atmos.png');
      }
    }
  } catch (error) {
    logger.error(`Error getting audio codec icon: ${error.message}`);
    return path.join(AUDIO_CODEC_ICONS_DIR, 'dolby_atmos.png');
  }
}

/**
 * Get the path to a resolution icon
 * @param {string} resolutionType - Resolution type
 * @returns {Promise<string>} - Path to the icon
 */
async function getResolutionIconPath(resolutionType) {
  try {
    // Check if the icon exists
    const iconPath = path.join(RESOLUTION_ICONS_DIR, `${resolutionType}.png`);
    
    try {
      await fs.access(iconPath);
      return iconPath;
    } catch {
      // Try lowercase version
      const lowerIconPath = path.join(RESOLUTION_ICONS_DIR, `${resolutionType.toLowerCase()}.png`);
      try {
        await fs.access(lowerIconPath);
        return lowerIconPath;
      } catch {
        // Return default icon
        return path.join(RESOLUTION_ICONS_DIR, '4k.png');
      }
    }
  } catch (error) {
    logger.error(`Error getting resolution icon: ${error.message}`);
    return path.join(RESOLUTION_ICONS_DIR, '4k.png');
  }
}

/**
 * Get the path to a review source icon
 * @param {string} source - Review source
 * @returns {Promise<string>} - Path to the icon
 */
async function getReviewSourceIconPath(source) {
  try {
    const sourceLower = source.toLowerCase();
    
    // Define all possible locations for this icon
    const possiblePaths = [
      // Primary location
      path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}.png`),
      
      // Try with original case
      path.join(REVIEW_SOURCE_ICONS_DIR, `${source}.png`),
      
      // Check for icons with _logo suffix
      path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}_logo.png`),
      
      // Check source frontend assets
      path.join(process.cwd(), '..', 'src', 'assets', `${sourceLower}.png`),
      path.join(process.cwd(), '..', 'src', 'assets', `${sourceLower}_logo.png`),
      
      // Special cases
      ...(sourceLower === 'rt_critics' ? [path.join(REVIEW_SOURCE_ICONS_DIR, 'rt.png')] : []),
      ...(sourceLower === 'imdb' ? [path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb_logo.png')] : [])
    ];
    
    // Try each path in order
    for (const iconPath of possiblePaths) {
      try {
        await fs.access(iconPath);
        logger.info(`Found icon for ${source} at ${iconPath}`);
        return iconPath;
      } catch {
        // Path doesn't exist, continue to next one
        continue;
      }
    }
    
    // If we reach here, all paths failed - create placeholder
    const placeholderPath = path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}.png`);
    
    // If the directory doesn't exist, create it
    try {
      await fs.mkdir(path.dirname(placeholderPath), { recursive: true });
    } catch (error) {
      // Ignore directory already exists error
    }
    
    logger.warn(`No icon found for ${source}, using IMDB fallback`);
    
    // Return the IMDB icon as fallback
    const imdbPath = path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb.png');
    try {
      await fs.access(imdbPath);
      return imdbPath;
    } catch {
      // Even IMDB icon is missing, log the error
      throw new Error(`Missing icon for ${source} and fallback IMDB icon`);
    }
  } catch (error) {
    logger.error(`Error getting review source icon: ${error.message}`);
    
    // Last resort - create an empty path that will trigger the text fallback
    return path.join(REVIEW_SOURCE_ICONS_DIR, 'missing.png');
  }
}
