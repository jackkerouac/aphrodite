/**
 * Get the appropriate background color based on settings
 * @param {Object} settings - The badge settings
 * @returns {string} The selected background color
 */
function determineBadgeBackgroundColor(settings) {
  // Default black fallback
  let bgColor = '#000000';
  
  // First check if brand colors should be used
  if (settings.use_brand_colors === true) {
    // Apply brand colors based on badge type
    switch (settings.type) {
      case 'audio':
        bgColor = '#2E51A2'; // Blue for audio badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      case 'resolution':
        bgColor = '#FA320A'; // Red for resolution badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      case 'review':
        bgColor = '#000000'; // Black for review badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      default:
        // If specific type has no brand color, check for explicit color settings
        if (settings.backgroundColor) {
          bgColor = settings.backgroundColor;
          console.log(`Using explicit backgroundColor: ${bgColor}`);
        } else if (settings.background_color) {
          bgColor = settings.background_color;
          console.log(`Using background_color: ${bgColor}`);
        }
    }
  }
  // If brand colors not enabled, check for explicit color settings
  else if (settings.backgroundColor) {
    bgColor = settings.backgroundColor;
    console.log(`Using explicit backgroundColor: ${bgColor}`);
  } else if (settings.background_color) {
    bgColor = settings.background_color;
    console.log(`Using background_color: ${bgColor}`);
  }
  
  return bgColor;
}import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get the project root directory (go up from backend/services/badge-renderer/utils to root)
const projectRoot = path.resolve(__dirname, '../../../..');

/**
 * Get the appropriate background color based on settings
 * @param {Object} settings - The badge settings
 * @returns {string} The selected background color
 */
function determineBadgeBackgroundColor(settings) {
  // Default black fallback
  let bgColor = '#000000';
  
  // First check if brand colors should be used
  if (settings.use_brand_colors === true) {
    // Apply brand colors based on badge type
    switch (settings.type) {
      case 'audio':
        bgColor = '#2E51A2'; // Blue for audio badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      case 'resolution':
        bgColor = '#FA320A'; // Red for resolution badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      case 'review':
        bgColor = '#000000'; // Black for review badges
        console.log(`Using brand color for ${settings.type}: ${bgColor}`);
        break;
      default:
        // If specific type has no brand color, check for explicit color settings
        if (settings.backgroundColor) {
          bgColor = settings.backgroundColor;
          console.log(`Using explicit backgroundColor: ${bgColor}`);
        } else if (settings.background_color) {
          bgColor = settings.background_color;
          console.log(`Using background_color: ${bgColor}`);
        }
    }
  }
  // If brand colors not enabled, check for explicit color settings
  else if (settings.backgroundColor) {
    bgColor = settings.backgroundColor;
    console.log(`Using explicit backgroundColor: ${bgColor}`);
  } else if (settings.background_color) {
    bgColor = settings.background_color;
    console.log(`Using background_color: ${bgColor}`);
  }
  
  return bgColor;
}

/**
 * Draw a rounded rectangle on a canvas context
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {number} x - The x position
 * @param {number} y - The y position
 * @param {number} width - The width of the rectangle
 * @param {number} height - The height of the rectangle
 * @param {number} radius - The corner radius
 */
export function drawRoundedRect(ctx, x, y, width, height, radius) {
  // Validate inputs to prevent errors
  if (width <= 0 || height <= 0) {
    throw new Error(`Invalid rectangle dimensions: ${width}x${height}`);
  }
  
  // Ensure radius isn't too large for the rectangle
  const safeRadius = Math.min(radius, width / 2, height / 2);
  
  ctx.beginPath();
  ctx.moveTo(x + safeRadius, y);
  ctx.lineTo(x + width - safeRadius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + safeRadius);
  ctx.lineTo(x + width, y + height - safeRadius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - safeRadius, y + height);
  ctx.lineTo(x + safeRadius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - safeRadius);
  ctx.lineTo(x, y + safeRadius);
  ctx.quadraticCurveTo(x, y, x + safeRadius, y);
  ctx.closePath();
}

/**
 * Apply background to a badge
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {number} width - The width of the badge
 * @param {number} height - The height of the badge
 * @param {Object} settings - The badge settings
 */
export function applyBackground(ctx, width, height, settings) {
  // Apply shadow first if enabled
  if (settings.shadowEnabled) {
    ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = settings.shadowBlur || 5;
    ctx.shadowOffsetX = settings.shadowOffsetX || 2;
    ctx.shadowOffsetY = settings.shadowOffsetY || 2;
  }
  
  // Handle background color with proper priority order
  let bgColor = determineBadgeBackgroundColor(settings);
  
  // Ensure backgroundColor is set for consistency
  settings.backgroundColor = bgColor;
  
  ctx.fillStyle = bgColor;
  
  // Handle transparency/opacity with consistent naming
  // Priority: transparency > background_opacity > backgroundOpacity > default (1.0)
  let opacity = 1.0;
  if (typeof settings.transparency === 'number') {
    opacity = Math.max(0, Math.min(1, settings.transparency));
  } else if (typeof settings.background_opacity === 'number') {
    opacity = Math.max(0, Math.min(1, settings.background_opacity));
  } else if (typeof settings.backgroundOpacity === 'number') {
    opacity = Math.max(0, Math.min(1, settings.backgroundOpacity));
  }
  
  ctx.globalAlpha = opacity;
  
  // Apply rounded corners if borderRadius is set
  if (settings.borderRadius && settings.borderRadius > 0) {
    drawRoundedRect(ctx, 0, 0, width, height, settings.borderRadius);
    ctx.fill();
  } else {
    ctx.fillRect(0, 0, width, height);
  }
  
  // Reset shadow after background
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;
  ctx.globalAlpha = 1; // Reset alpha
}

/**
 * Apply border to a badge
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {number} width - The width of the badge
 * @param {number} height - The height of the badge
 * @param {Object} settings - The badge settings
 */
export function applyBorder(ctx, width, height, settings) {
  // Guard against invalid border width
  const borderWidth = settings.borderWidth || 0;
  if (borderWidth <= 0) return;
  
  // Use provided border color or default to white
  ctx.strokeStyle = settings.borderColor || '#FFFFFF';
  ctx.lineWidth = borderWidth;
  
  // Handle border opacity with safeguards
  let opacity = 1.0;
  if (typeof settings.borderOpacity === 'number') {
    opacity = Math.max(0, Math.min(1, settings.borderOpacity));
  } else if (typeof settings.border_opacity === 'number') {
    opacity = Math.max(0, Math.min(1, settings.border_opacity));
  }
  ctx.globalAlpha = opacity;
  
  const offset = borderWidth / 2;
  
  // Apply rounded corners if borderRadius is set
  if (settings.borderRadius && settings.borderRadius > 0) {
    try {
      // Ensure we don't have negative radius after adjusting for border
      const adjustedRadius = Math.max(1, settings.borderRadius - offset);
      
      drawRoundedRect(
        ctx, 
        offset, 
        offset, 
        width - borderWidth, 
        height - borderWidth, 
        adjustedRadius
      );
      ctx.stroke();
    } catch (error) {
      console.warn(`Border rendering error: ${error.message}. Falling back to rectangular border.`);
      ctx.strokeRect(offset, offset, width - borderWidth, height - borderWidth);
    }
  } else {
    ctx.strokeRect(offset, offset, width - borderWidth, height - borderWidth);
  }
  
  ctx.globalAlpha = 1; // Reset alpha
}

/**
 * Get a suitable font family from available options
 * @param {string} requestedFont - The requested font family
 * @param {Map} availableFonts - Map of available fonts
 * @returns {string} The font family to use
 */
export function getFontFamily(requestedFont, availableFonts) {
  // Handle null/undefined availableFonts
  const fonts = availableFonts || new Map();
  
  // Check if the requested font is registered
  if (requestedFont && fonts.has(requestedFont)) {
    return requestedFont;
  }
  
  // If the requested font contains 'bold' (case insensitive), prioritize bold fonts
  if (requestedFont && requestedFont.toLowerCase().includes('bold')) {
    // Try to find bold versions first for better consistency with preview
    const boldFallbacks = ['Roboto Bold', 'Inter Bold', 'Arial Bold', 'DejaVu Sans Bold'];
    for (const font of boldFallbacks) {
      if (fonts.has(font)) {
        return font;
      }
    }
  }
  
  // Fallback to available fonts
  const fallbacks = ['Roboto Bold', 'Inter Bold', 'Roboto', 'Inter', 'DejaVu Sans', 'Arial', 'sans-serif'];
  for (const font of fallbacks) {
    if (fonts.has(font)) {
      return font;
    }
  }
  
  // Final fallback to generic sans-serif
  return 'Arial, sans-serif';
}

/**
 * Map resolution values to asset paths
 * @param {string} resolution - The resolution value
 * @returns {Promise<string|null>} The path to the resolution image, or null if not found
 */
export async function getResolutionImagePath(resolution) {
  const resolutionMap = {
    '8K': 'resolution/8k.png',
    '4K': 'resolution/4k.png',
    '1440p': 'resolution/1440p.png',
    '1080p': 'resolution/1080p.png',
    '720p': 'resolution/720p.png',
    '480p': 'resolution/480p.png',
    'SD': 'resolution/sd.png'
  };
  
  let filename = resolutionMap[resolution];
  if (!filename) {
    // Check for lowercase versions as fallback
    const lowerResolution = resolution.toLowerCase();
    const resolutionMapLower = {
      '8k': 'resolution/8k.png',
      '4k': 'resolution/4k.png',
      '1440p': 'resolution/1440p.png',
      '1080p': 'resolution/1080p.png',
      '720p': 'resolution/720p.png',
      '480p': 'resolution/480p.png',
      'sd': 'resolution/sd.png'
    };
    filename = resolutionMapLower[lowerResolution];
  }
  
  if (!filename) return null;
  
  // Check if the file exists before returning the path
  const filePath = path.join(projectRoot, 'src', 'assets', filename);
  try {
    await fs.access(filePath);
    return filePath;
  } catch {
    console.warn(`Resolution image not found: ${filePath}`);
  }
  return null;
}

/**
 * Map audio formats to asset paths with improved normalization and fallbacks
 * @param {string} audioFormat - The audio format
 * @returns {Promise<string|null>} The path to the audio format image, or null if not found
 */
export async function getAudioImagePath(audioFormat) {
  if (!audioFormat) return null;
  
  try {
    // Normalize the audio format string with improved handling
    const normalized = audioFormat.toLowerCase()
      .replace(/[\s\:\/\\\-\.\(\)\[\]]+/g, '_') // Handle more special characters
      .replace(/^_+|_+$/g, '') // Trim underscores at start/end
      // Special format mappings
      .replace('dolby_digital_plus', 'plus')
      .replace('dolby_digital_5_1', 'plus')
      .replace('dolby_digital_51', 'plus')
      .replace('dolby_digital', 'digital')
      .replace('dolby_plus', 'plus')
      .replace('dolby_truehd', 'truehd')
      .replace('dts_hd', 'dtses')
      .replace('dts_x', 'dtsx')
      .replace('ac_3', 'ac3')
      .replace('ac_4', 'ac4');
    
    // Generate variations in priority order
    const variations = [
      normalized,                     // Original normalized
      normalized.replace(/_/g, ''),   // No underscores
      normalized.replace(/_/g, '-')   // Dashes instead of underscores
    ];
    
    // Add common format mapping variations
    const formatMappings = {
      dolby: ['digital'],
      digital: ['digital'],
      plus: ['plus', 'dolby_plus'],
      dts: ['dts', 'dtses', 'dtsx'],
      truehd: ['truehd', 'truehd_atmos'],
      atmos: ['atmos', 'dolby_atmos', 'plus_atmos', 'truehd_atmos'],
      aac: ['aac'],
      flac: ['flac'],
      mp3: ['mp3'],
      ac3: ['ac3'],
      eac3: ['eac3'],
      opus: ['opus'],
      pcm: ['pcm']
    };
    
    // Add specific mappings for common formats
    Object.keys(formatMappings).forEach(key => {
      if (normalized.includes(key)) {
        variations.push(...formatMappings[key]);
      }
    });
    
    // Remove duplicates and empty values
    const formats = [...new Set(variations.filter(Boolean))]; 
    
    // Try both standard and compact directories
    for (const format of formats) {
      const attempts = [
        path.join(projectRoot, 'src', 'assets', 'audio_codec', 'standard', `${format}.png`),
        path.join(projectRoot, 'src', 'assets', 'audio_codec', 'compact', `${format}.png`),
        // Fallback to older directory structure if present
        path.join(projectRoot, 'src', 'assets', 'audioformats', `${format}.png`)
      ];
      
      for (const filePath of attempts) {
        try {
          await fs.access(filePath);
          console.log(`Found audio image at: ${filePath}`);
          return filePath;
        } catch {
          // Continue to next attempt
        }
      }
    }
    
    console.warn(`Audio format image not found for: ${audioFormat} (normalized: ${normalized}, tried variations: ${formats.join(', ')})`);
  } catch (error) {
    console.error(`Error finding audio format image for ${audioFormat}:`, error);
  }
  
  return null;
}

export { projectRoot, determineBadgeBackgroundColor };