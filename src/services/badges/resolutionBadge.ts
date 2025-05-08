import { ResolutionBadgeSettings } from '@/components/badges/types/ResolutionBadge';
import { createTempCanvas, drawRoundedRect } from './utils';

/**
 * Renders a resolution badge to a canvas
 * @param options The options for rendering the resolution badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderResolutionBadge = async (
  options: ResolutionBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  // Scale the size to a reasonable value relative to the poster
  const scaledSize = Math.min(options.size, 200);
  const canvas = createTempCanvas(scaledSize * 2, scaledSize);
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
    console.log(`Drawing resolution badge with border radius: ${options.borderRadius}`);
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

  // Draw resolution text
  const displayText = options.useCustomText && options.customText 
    ? options.customText 
    : options.resolutionType || '4K';
  
  ctx.globalAlpha = 1; // Reset alpha for text
  ctx.fillStyle = options.textColor || '#FFFFFF';
  ctx.font = `${options.fontSize || options.size / 2}px ${options.fontFamily || 'Arial'}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(displayText, canvas.width / 2, canvas.height / 2);

  return canvas;
};