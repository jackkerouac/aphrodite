import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get the project root directory (go up from backend/services/badge-renderer/utils to root)
const projectRoot = path.resolve(__dirname, '../../../..');

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
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
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
  
  // Ensure backgroundColor (camelCase) is set from background_color (snake_case)
  if (settings.background_color && !settings.backgroundColor) {
    settings.backgroundColor = settings.background_color;
  }
  
  ctx.fillStyle = settings.backgroundColor || '#000000';
  ctx.globalAlpha = settings.transparency || settings.background_opacity || 1;
  
  if (settings.borderRadius > 0) {
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
  if (!settings.borderWidth || settings.borderWidth <= 0) return;
  
  ctx.strokeStyle = settings.borderColor || '#FFFFFF';
  ctx.lineWidth = settings.borderWidth;
  ctx.globalAlpha = settings.borderOpacity || 1;
  
  const offset = settings.borderWidth / 2;
  
  if (settings.borderRadius > 0) {
    drawRoundedRect(
      ctx, 
      offset, 
      offset, 
      width - settings.borderWidth, 
      height - settings.borderWidth, 
      settings.borderRadius - offset
    );
    ctx.stroke();
  } else {
    ctx.strokeRect(offset, offset, width - settings.borderWidth, height - settings.borderWidth);
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
  // Check if the requested font is registered
  if (requestedFont && availableFonts.has(requestedFont)) {
    return requestedFont;
  }
  
  // Try to find bold versions first for better consistency with preview
  const boldFallbacks = ['Roboto Bold', 'Inter Bold'];
  for (const font of boldFallbacks) {
    if (availableFonts.has(font)) {
      return font;
    }
  }
  
  // Fallback to available fonts
  const fallbacks = ['Roboto', 'Inter', 'DejaVu Sans', 'Arial', 'sans-serif'];
  for (const font of fallbacks) {
    if (availableFonts.has(font)) {
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
 * Map audio formats to asset paths
 * @param {string} audioFormat - The audio format
 * @returns {Promise<string|null>} The path to the audio format image, or null if not found
 */
export async function getAudioImagePath(audioFormat) {
  if (!audioFormat) return null;
  
  // Normalize the audio format string
  const normalized = audioFormat.toLowerCase()
    .replace(/[\s\:\/\\\-]+/g, '_')
    .replace('dolby_digital_plus', 'plus')
    .replace('dolby_digital_5_1', 'plus')
    .replace('dolby_digital_51', 'plus')
    .replace('dolby_digital', 'digital')
    .replace('dolby_plus', 'plus')
    .replace('dolby_truehd', 'truehd')
    .replace('dts_hd', 'dtses')
    .replace('dts_x', 'dtsx');
  
  // Try multiple variations and handle edge cases
  const variations = [
    normalized,
    normalized.replace(/_/g, ''),
    normalized.replace(/_/g, '-')
  ];
  
  // Add specific mappings for common formats
  if (normalized.includes('dolby') || normalized.includes('digital')) {
    variations.push('digital');
  }
  if (normalized.includes('plus')) {
    variations.push('plus');
  }
  if (normalized.includes('dts')) {
    variations.push('dts', 'dtses', 'dtsx');
  }
  if (normalized.includes('truehd')) {
    variations.push('truehd', 'truehd_atmos');
  }
  if (normalized.includes('atmos')) {
    variations.push('atmos', 'dolby_atmos', 'plus_atmos', 'truehd_atmos');
  }
  
  const formats = [...new Set(variations)]; // Remove duplicates
  
  // Try both standard and compact directories
  for (const format of formats) {
    const attempts = [
      path.join(projectRoot, 'src', 'assets', 'audio_codec', 'standard', `${format}.png`),
      path.join(projectRoot, 'src', 'assets', 'audio_codec', 'compact', `${format}.png`)
    ];
    
    for (const filePath of attempts) {
      try {
        await fs.access(filePath);
        console.log(`Found audio image at: ${filePath}`);
        return filePath;
      } catch {
        continue;
      }
    }
  }
  
  console.warn(`Audio format image not found for: ${audioFormat} (normalized: ${normalized}, tried variations: ${formats.join(', ')})`);
  return null;
}

export { projectRoot };