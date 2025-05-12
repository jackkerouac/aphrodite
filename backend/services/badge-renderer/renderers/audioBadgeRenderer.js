import { loadImage } from 'canvas';
import { 
  applyBackground, 
  applyBorder, 
  getFontFamily, 
  getAudioImagePath 
} from '../utils/canvasUtils.js';

/**
 * Renders an audio badge
 * @param {Canvas} canvas - The canvas to render on
 * @param {Object} settings - The badge settings
 * @param {Object} metadata - The metadata for the badge
 * @param {string} [sourceImagePath] - Optional path to an image to use
 * @param {Map} fonts - Available fonts
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
export async function renderAudioBadge(canvas, settings, metadata, sourceImagePath, fonts) {
  console.log('Rendering audio badge with settings:', settings);
  
  try {
    // Validate and normalize the size setting
    if (settings.size !== undefined) {
      // Ensure size is positive and within reasonable bounds
      settings.size = Math.max(10, Math.min(Math.abs(settings.size), 500));
    } else {
      // Default size if not specified
      settings.size = 100;
    }
    
    // If we have a source image, render it with styling
    if (sourceImagePath) {
      return await renderImageBadge(canvas, settings, sourceImagePath);
    }
    
    // Note: Brand colors are now handled centrally in canvasUtils.js 
    // Let background color flow through as-is, all background color logic is in applyBackground
    
    // Otherwise render text-based badge
    return await renderTextBadge(canvas, settings, metadata.audioFormat || 'Audio', fonts);
  } catch (error) {
    console.error(`Error rendering audio badge: ${error.message}`);
    // Create a simple fallback badge
    return createFallbackBadge(canvas, 'Audio Error');
  }
}

/**
 * Renders a badge with an image
 * @param {Canvas} canvas - The canvas to render on
 * @param {Object} settings - The badge settings
 * @param {string} imagePath - Path to the image
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
async function renderImageBadge(canvas, settings, imagePath) {
  try {
    // Load the image
    const img = await loadImage(imagePath);
    
    // Handle null dimensions gracefully
    if (!img.width || !img.height) {
      throw new Error('Invalid image dimensions');
    }
    
    // Calculate dimensions based on settings - use the actual settings.size
    // Ensure targetWidth is positive and reasonable
    const targetWidth = Math.max(20, Math.min(settings.size || 100, 500));
    const scaleFactor = targetWidth / img.width;
    
    const imageWidth = Math.round(img.width * scaleFactor);
    const imageHeight = Math.round(img.height * scaleFactor);
    
    // Ensure we have positive dimensions
    if (imageWidth <= 0 || imageHeight <= 0) {
      throw new Error(`Invalid calculated dimensions: ${imageWidth}x${imageHeight}`);
    }
    
    // Add padding from settings with fallbacks
    const padding = Math.max(0, settings.padding || settings.margin || 10);
    const badgeWidth = imageWidth + (padding * 2);
    const badgeHeight = imageHeight + (padding * 2);
    
    // Resize canvas to fit
    canvas.width = badgeWidth;
    canvas.height = badgeHeight;
    const ctx = canvas.getContext('2d');
    
    // Apply background
    applyBackground(ctx, badgeWidth, badgeHeight, settings);
    
    // Draw the image
    ctx.drawImage(img, padding, padding, imageWidth, imageHeight);
    
    // Apply border if specified
    if (settings.borderWidth > 0) {
      applyBorder(ctx, badgeWidth, badgeHeight, settings);
    }
    
    return canvas.toBuffer('image/png');
  } catch (error) {
    console.error('Error rendering image badge:', error);
    // Fall back to text rendering
    try {
      return await renderTextBadge(canvas, settings, settings.value || 'Audio');
    } catch (textError) {
      console.error('Fallback text rendering also failed:', textError);
      return createFallbackBadge(canvas, 'Audio');
    }
  }
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
  try {
    // Ensure size is positive and within reasonable bounds
    const size = Math.max(20, Math.min(settings.size || 100, 500));
    
    // Create canvas with proportional dimensions based on size
    const width = size * 2;
    const height = size;
    
    // Guard against zero dimensions
    if (width <= 0 || height <= 0) {
      throw new Error(`Invalid badge dimensions: ${width}x${height}`);
    }
    
    // Resize canvas
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');

    // Apply background
    applyBackground(ctx, canvas.width, canvas.height, settings);

    // Apply border if specified and borderWidth is valid
    if (settings.borderWidth && settings.borderWidth > 0) {
      applyBorder(ctx, canvas.width, canvas.height, settings);
    }

    // Draw text
    ctx.fillStyle = settings.textColor || '#FFFFFF';
    const fontSize = Math.max(10, settings.fontSize || size / 3);
    
    // Use a font that's available, fallback to system fonts
    const fontFamily = getFontFamily(settings.fontFamily, fonts);
    // Always use bold font weight for consistency with preview
    ctx.font = `bold ${fontSize}px ${fontFamily}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Limit text length to prevent overflow
    const maxLength = Math.floor(width / (fontSize * 0.6));
    const displayText = text.length > maxLength ? text.substring(0, maxLength - 3) + '...' : text;
    
    ctx.fillText(displayText, width / 2, height / 2);

    return canvas.toBuffer('image/png');
  } catch (error) {
    console.error(`Error in renderTextBadge: ${error.message}`);
    return createFallbackBadge(canvas, text || 'Audio');
  }
}

/**
 * Create a simple fallback badge when all else fails
 * @param {Canvas} canvas - The canvas to render on
 * @param {string} text - Text to display
 * @returns {Buffer} The rendered badge as a PNG buffer
 */
export function createFallbackBadge(canvas, text) {
  // Use a fixed size for fallback badges
  canvas.width = 150;
  canvas.height = 75;
  const ctx = canvas.getContext('2d');
  
  // Fill with dark background
  ctx.fillStyle = '#333333';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw text
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 18px Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text || 'Error', canvas.width / 2, canvas.height / 2);
  
  return canvas.toBuffer('image/png');
}