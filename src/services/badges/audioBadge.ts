import { AudioBadgeSettings } from '@/components/badges/types/AudioBadge';
import { getAudioCodecImagePath } from '@/utils/audioCodecUtils';
import { createTempCanvas, drawRoundedRect } from './utils';

/**
 * Renders an audio badge to a canvas
 * @param options The options for rendering the audio badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderAudioBadge = async (
  options: AudioBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  // Start with a default size canvas, but we'll resize it based on the image dimensions
  // We'll use a temporary size that will be replaced once the image loads
  const initialSize = 200;
  
  // Create canvas with initial dimensions
  const canvas = createTempCanvas(initialSize, initialSize);
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

  // Apply background to the initial canvas
  ctx.fillStyle = options.backgroundColor;
  ctx.globalAlpha = options.backgroundOpacity;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw codec image if specified
  if (options.codecType) {
    try {
      // Reset alpha for image
      ctx.globalAlpha = 1;
      
      // Load the codec image
      const imagePath = getAudioCodecImagePath(options.codecType);
      const img = new Image();
      
      await new Promise<void>((resolve, reject) => {
        img.onload = () => {
          // Increase padding to ensure proper spacing between image and badge borders
          // Now using 5% of image width with a minimum of 12px for better visual appearance
          const baseImagePadding = Math.max(Math.round(img.width * 0.05), 12);
          
          // Calculate scale factor based on the size option
          const scaleFactor = options.size / Math.max(img.width, img.height);
          
          // Scale the image dimensions
          const imageWidth = img.width * scaleFactor;
          const imageHeight = img.height * scaleFactor;
          
          // Add extra padding for border radius (if specified)
          // This ensures we have enough space for the rounded corners
          const borderRadius = options.borderRadius || 0;
          let totalPadding = Math.max(baseImagePadding, borderRadius / 2);
          
          // Calculate dimensions for the canvas, including extra space for shadow if enabled
          let canvasWidth = imageWidth + (totalPadding * 2);
          let canvasHeight = imageHeight + (totalPadding * 2);
          
          // Add extra padding for shadow if enabled
          if (options.shadowEnabled) {
            const shadowOffsetX = options.shadowOffsetX || 2;
            const shadowOffsetY = options.shadowOffsetY || 2;
            const shadowBlur = options.shadowBlur || 5;
            
            // Add space for shadow to extend beyond the badge
            // For right and bottom, we add offset + blur
            // For left and top, we add extra space only if offset is negative
            const shadowPaddingLeft = Math.max(0, -shadowOffsetX) + shadowBlur;
            const shadowPaddingTop = Math.max(0, -shadowOffsetY) + shadowBlur;
            const shadowPaddingRight = Math.max(0, shadowOffsetX) + shadowBlur;
            const shadowPaddingBottom = Math.max(0, shadowOffsetY) + shadowBlur;
            
            canvasWidth += shadowPaddingLeft + shadowPaddingRight;
            canvasHeight += shadowPaddingTop + shadowPaddingBottom;
            
            // Adjust totalPadding to center the badge within the shadow space
            totalPadding = Math.max(totalPadding, Math.max(shadowPaddingLeft, shadowPaddingTop));
          }
          
          // Resize the canvas
          canvas.width = canvasWidth;
          canvas.height = canvasHeight;
          
          // Clear canvas
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          // Calculate the actual badge position within the canvas (considering shadow space)
          // For backgrounds, borders, and other elements that make up the badge
          let badgeX = totalPadding;
          let badgeY = totalPadding;
          const badgeWidth = imageWidth;
          const badgeHeight = imageHeight;
          
          // Apply shadow if enabled - moved here to affect the entire badge
          if (options.shadowEnabled) {
            ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = options.shadowBlur || 5;
            ctx.shadowOffsetX = options.shadowOffsetX || 2;
            ctx.shadowOffsetY = options.shadowOffsetY || 2;
          }
          
          // Apply background with or without rounded corners
          ctx.fillStyle = options.backgroundColor;
          ctx.globalAlpha = options.backgroundOpacity;
          
          if (borderRadius > 0) {
            // Draw rounded rectangle background
            console.log(`Drawing audio badge with border radius: ${borderRadius}`);
            drawRoundedRect(ctx, badgeX, badgeY, badgeWidth, badgeHeight, borderRadius);
            ctx.fill();
          } else {
            // Draw regular rectangle background
            ctx.fillRect(badgeX, badgeY, badgeWidth, badgeHeight);
          }
          
          // Reset shadow for border to avoid doubling the effect
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
          
          // Apply border if specified
          if (options.borderWidth && options.borderWidth > 0) {
            // Ensure border color is properly specified or use black as default
            ctx.strokeStyle = options.borderColor || '#000000';
            // Ensure appropriate border opacity is applied (using explicit check to avoid 0 being treated as falsy)
            ctx.globalAlpha = options.borderOpacity !== undefined ? options.borderOpacity : 1;
            // Set correct line width
            ctx.lineWidth = options.borderWidth;
            
            if (borderRadius > 0) {
              // Draw rounded rectangle border
              const offset = options.borderWidth / 2;
              drawRoundedRect(
                ctx, 
                badgeX + offset, 
                badgeY + offset, 
                badgeWidth - options.borderWidth, 
                badgeHeight - options.borderWidth, 
                borderRadius - offset
              );
              ctx.stroke();
            } else {
              // Draw rectangle border
              ctx.strokeRect(
                badgeX + options.borderWidth / 2,
                badgeY + options.borderWidth / 2,
                badgeWidth - options.borderWidth,
                badgeHeight - options.borderWidth
              );
            }
          }
          
          // Reset alpha and shadow for image
          ctx.globalAlpha = 1;
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
          
          // Center the image within the canvas with proper padding on all sides
          // Add internal padding to ensure the image doesn't touch the badge borders
          const internalPadding = Math.max(baseImagePadding, 12);
          const x = totalPadding + internalPadding;
          const y = totalPadding + internalPadding;
          
          // Calculate available space after padding is applied
          const availableWidth = imageWidth - (internalPadding * 2);
          const availableHeight = imageHeight - (internalPadding * 2);
          
          // Scale image to fit within available space while maintaining aspect ratio
          const scale = Math.min(
            availableWidth / img.width,
            availableHeight / img.height
          );
          
          // Calculate final dimensions that preserve aspect ratio
          const adjustedWidth = img.width * scale;
          const adjustedHeight = img.height * scale;
          
          // Recalculate position to ensure image is centered in available space
          const centeredX = totalPadding + (imageWidth - adjustedWidth) / 2;
          const centeredY = totalPadding + (imageHeight - adjustedHeight) / 2;
          ctx.drawImage(img, centeredX, centeredY, adjustedWidth, adjustedHeight);
          resolve();
        };
        
        img.onerror = () => {
          console.error(`Failed to load codec image: ${imagePath}`);
          // Fallback to text if image fails to load
          ctx.fillStyle = options.textColor || '#FFFFFF';
          ctx.font = `${options.fontSize || 20}px ${options.fontFamily || 'Arial'}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(options.codecType || '', canvas.width / 2, canvas.height / 2);
          resolve();
        };
        
        img.src = imagePath;
      });
    } catch (error) {
      console.error('Error rendering codec image:', error);
      // Fallback to text if there's an error
      ctx.fillStyle = options.textColor || '#FFFFFF';
      ctx.font = `${options.fontSize || 20}px ${options.fontFamily || 'Arial'}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(options.codecType || 'Audio', canvas.width / 2, canvas.height / 2);
    }
  }

  return canvas;
};