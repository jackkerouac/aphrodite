import { createCanvas } from 'canvas';
import logger from '../lib/logger.js';

/**
 * Generates an audio badge image based on the provided settings
 * @param {Object} settings - The badge settings object
 * @returns {Buffer} - The generated image as a Buffer
 */
export const generateAudioBadge = async (settings) => {
  try {
    logger.info('Generating audio badge image');
    
    // Set up canvas for badge
    const canvasWidth = 200;
    const canvasHeight = 100;
    const canvas = createCanvas(canvasWidth, canvasHeight);
    const ctx = canvas.getContext('2d');
    
    // Clear canvas with transparent background
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Apply background
    const bgColor = settings.background_color || '#ffffff';
    const bgOpacity = settings.background_transparency !== undefined ? settings.background_transparency : 0.7;
    const borderRadius = settings.border_radius !== undefined ? settings.border_radius : 5;
    
    // Set background color with transparency
    ctx.fillStyle = hexToRgba(bgColor, bgOpacity);
    
    // Draw rounded rectangle for background
    roundRect(
      ctx, 
      0, 
      0, 
      canvasWidth, 
      canvasHeight, 
      borderRadius
    );
    ctx.fill();
    
    // Apply border if needed
    if (settings.border_width && settings.border_width > 0) {
      const borderColor = settings.border_color || '#000000';
      const borderOpacity = settings.border_transparency !== undefined ? settings.border_transparency : 0.9;
      const borderWidth = settings.border_width;
      
      ctx.strokeStyle = hexToRgba(borderColor, borderOpacity);
      ctx.lineWidth = borderWidth;
      
      // Draw rounded rectangle for border
      roundRect(
        ctx, 
        borderWidth / 2, 
        borderWidth / 2, 
        canvasWidth - borderWidth, 
        canvasHeight - borderWidth, 
        borderRadius - borderWidth / 2
      );
      ctx.stroke();
    }
    
    // Apply shadow if enabled
    if (settings.shadow_toggle) {
      const shadowColor = settings.shadow_color || '#000000';
      const shadowBlur = settings.shadow_blur_radius || 5;
      const shadowOffsetX = settings.shadow_offset_x || 0;
      const shadowOffsetY = settings.shadow_offset_y || 0;
      
      ctx.shadowColor = shadowColor;
      ctx.shadowBlur = shadowBlur;
      ctx.shadowOffsetX = shadowOffsetX;
      ctx.shadowOffsetY = shadowOffsetY;
    }
    
    // Draw audio codec text (centered)
    const codecType = settings.audio_codec_type || 'auto';
    ctx.shadowColor = 'transparent'; // Reset shadow for text
    ctx.fillStyle = '#000000'; // Text color
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(
      codecType.toUpperCase(), 
      canvasWidth / 2, 
      canvasHeight / 2
    );
    
    // Convert canvas to buffer
    const buffer = canvas.toBuffer('image/png');
    logger.info('Audio badge image generated successfully');
    return buffer;
  } catch (error) {
    logger.error(`Error generating audio badge: ${error.message}`);
    throw error;
  }
};

/**
 * Generates a resolution badge image based on the provided settings
 * @param {Object} settings - The badge settings object
 * @returns {Buffer} - The generated image as a Buffer
 */
export const generateResolutionBadge = async (settings) => {
  try {
    logger.info('Generating resolution badge image');
    
    // Implementation similar to generateAudioBadge but for resolution badge
    // ...
    
    // Placeholder for now
    const canvas = createCanvas(200, 100);
    return canvas.toBuffer('image/png');
  } catch (error) {
    logger.error(`Error generating resolution badge: ${error.message}`);
    throw error;
  }
};

/**
 * Generates a review badge image based on the provided settings
 * @param {Object} settings - The badge settings object
 * @returns {Buffer} - The generated image as a Buffer
 */
export const generateReviewBadge = async (settings) => {
  try {
    logger.info('Generating review badge image');
    
    // Implementation similar to generateAudioBadge but for review badge
    // ...
    
    // Placeholder for now
    const canvas = createCanvas(200, 100);
    return canvas.toBuffer('image/png');
  } catch (error) {
    logger.error(`Error generating review badge: ${error.message}`);
    throw error;
  }
};

/**
 * Helper function to draw a rounded rectangle
 */
function roundRect(ctx, x, y, width, height, radius) {
  if (width < 2 * radius) radius = width / 2;
  if (height < 2 * radius) radius = height / 2;
  
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + width, y, x + width, y + height, radius);
  ctx.arcTo(x + width, y + height, x, y + height, radius);
  ctx.arcTo(x, y + height, x, y, radius);
  ctx.arcTo(x, y, x + width, y, radius);
  ctx.closePath();
}

/**
 * Helper function to convert hex color to rgba
 */
function hexToRgba(hex, alpha = 1) {
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Convert 3-digit hex to 6-digit
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  
  // Extract RGB components
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export default {
  generateAudioBadge,
  generateResolutionBadge,
  generateReviewBadge
};