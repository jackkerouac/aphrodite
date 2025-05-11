import { loadImage } from 'canvas';
import { 
  applyBackground, 
  applyBorder, 
  getFontFamily, 
  getResolutionImagePath 
} from '../utils/canvasUtils.js';

/**
 * Renders a resolution badge
 * @param {Canvas} canvas - The canvas to render on
 * @param {Object} settings - The badge settings
 * @param {Object} metadata - The metadata for the badge
 * @param {string} [sourceImagePath] - Optional path to an image to use
 * @param {Map} fonts - Available fonts
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
export async function renderResolutionBadge(canvas, settings, metadata, sourceImagePath, fonts) {
  console.log('Rendering resolution badge with settings:', settings);
  
  // If we have a source image, render it with styling
  if (sourceImagePath) {
    return await renderImageBadge(canvas, settings, sourceImagePath);
  }
  
  // Apply brand colors if enabled and no background_color is set
  if (settings.use_brand_colors && !settings.background_color) {
    console.log('Using brand colors for resolution badge');
    // Resolution badges typically use red color
    settings.backgroundColor = '#FA320A'; // Red color for resolution badges
  } else {
    // Ensure backgroundColor (camelCase) is set from background_color (snake_case)
    if (settings.background_color && !settings.backgroundColor) {
      settings.backgroundColor = settings.background_color;
      console.log(`Using custom background color: ${settings.backgroundColor}`);
    }
  }
  
  return await renderTextBadge(canvas, settings, metadata.resolution || 'HD', fonts);
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
    
    // Calculate dimensions based on settings - use the actual settings.size
    const targetWidth = settings.size || 100;
    const scaleFactor = targetWidth / img.width;
    
    const imageWidth = Math.round(img.width * scaleFactor);
    const imageHeight = Math.round(img.height * scaleFactor);
    
    // Add padding from settings
    const padding = settings.padding || settings.margin || 10;
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
    return renderTextBadge(canvas, settings, 'N/A', fonts);
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