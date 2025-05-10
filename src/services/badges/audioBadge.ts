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
          // Get original image dimensions
          const originalWidth = img.width;
          const originalHeight = img.height;
          
          // Calculate the scaling factor based on the size option
          // Use size to determine the target width of the image
          const targetImageWidth = options.size || 100;
          const scaleFactor = targetImageWidth / originalWidth;
          
          // Scale image dimensions
          const imageWidth = Math.round(originalWidth * scaleFactor);
          const imageHeight = Math.round(originalHeight * scaleFactor);
          
          // Set border radius (if any)
          // Scale border radius proportionally with the size
          const borderRadius = options.borderRadius ? options.borderRadius * scaleFactor : 0;
          
          // Set GENEROUS padding - minimum 15% of scaled image dimensions, but scale with image size
          const minPadding = Math.round(Math.max(imageWidth * 0.05, 5));
          const horizontalPadding = Math.max(Math.round(imageWidth * 0.15), minPadding);
          const verticalPadding = Math.max(Math.round(imageHeight * 0.15), minPadding);
          
          // Calculate badge dimensions including proper padding
          const badgeWidth = imageWidth + (horizontalPadding * 2);
          const badgeHeight = imageHeight + (verticalPadding * 2);
          
          // Calculate shadow padding
          let shadowPaddingLeft = 0;
          let shadowPaddingTop = 0;
          let shadowPaddingRight = 0;
          let shadowPaddingBottom = 0;
          
          if (options.shadowEnabled) {
            // Scale shadow parameters with the image size
            const shadowScaleFactor = Math.max(0.5, Math.min(1, scaleFactor));
            const shadowOffsetX = (options.shadowOffsetX || 2) * shadowScaleFactor;
            const shadowOffsetY = (options.shadowOffsetY || 2) * shadowScaleFactor;
            const shadowBlur = (options.shadowBlur || 5) * shadowScaleFactor;
            
            // Calculate shadow padding for each side
            shadowPaddingLeft = Math.max(0, -shadowOffsetX) + shadowBlur;
            shadowPaddingTop = Math.max(0, -shadowOffsetY) + shadowBlur;
            shadowPaddingRight = Math.max(0, shadowOffsetX) + shadowBlur;
            shadowPaddingBottom = Math.max(0, shadowOffsetY) + shadowBlur;
          }
          
          // Calculate final canvas size including badge and shadow
          const canvasWidth = badgeWidth + shadowPaddingLeft + shadowPaddingRight;
          const canvasHeight = badgeHeight + shadowPaddingTop + shadowPaddingBottom;
          
          // Resize canvas to fit badge with padding and shadow
          canvas.width = canvasWidth;
          canvas.height = canvasHeight;
          
          // Clear canvas before drawing
          ctx.clearRect(0, 0, canvasWidth, canvasHeight);
          
          // Calculate badge position within canvas (considering shadow)
          const badgeX = shadowPaddingLeft;
          const badgeY = shadowPaddingTop;
          
          // Apply shadow if enabled
          if (options.shadowEnabled) {
            const shadowScaleFactor = Math.max(0.5, Math.min(1, scaleFactor));
            ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = (options.shadowBlur || 5) * shadowScaleFactor;
            ctx.shadowOffsetX = (options.shadowOffsetX || 2) * shadowScaleFactor;
            ctx.shadowOffsetY = (options.shadowOffsetY || 2) * shadowScaleFactor;
          }
          
          // Apply background with or without rounded corners
          ctx.fillStyle = options.backgroundColor;
          ctx.globalAlpha = options.backgroundOpacity;
          
          if (borderRadius > 0) {
            // Draw rounded rectangle background
            drawRoundedRect(ctx, badgeX, badgeY, badgeWidth, badgeHeight, borderRadius);
            ctx.fill();
          } else {
            // Draw regular rectangle background
            ctx.fillRect(badgeX, badgeY, badgeWidth, badgeHeight);
          }
          
          // Reset shadow settings before drawing border
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
          
          // Calculate border width based on size
          const scaledBorderWidth = options.borderWidth ? options.borderWidth * Math.min(1, scaleFactor) : 0;
          
          // ONLY draw a border if it's explicitly requested AND has width > 0 AND opacity > 0
          if (scaledBorderWidth > 0 && 
              options.borderOpacity !== undefined && 
              options.borderOpacity > 0) {
            
            // Set border properties
            ctx.strokeStyle = options.borderColor || '#000000';
            ctx.globalAlpha = options.borderOpacity;
            ctx.lineWidth = scaledBorderWidth;
            
            if (borderRadius > 0) {
              // Draw rounded rectangle border
              const offset = scaledBorderWidth / 2;
              drawRoundedRect(
                ctx, 
                badgeX + offset, 
                badgeY + offset, 
                badgeWidth - scaledBorderWidth, 
                badgeHeight - scaledBorderWidth, 
                borderRadius - offset
              );
              ctx.stroke();
            } else {
              // Draw rectangle border
              ctx.strokeRect(
                badgeX + scaledBorderWidth / 2,
                badgeY + scaledBorderWidth / 2,
                badgeWidth - scaledBorderWidth,
                badgeHeight - scaledBorderWidth
              );
            }
          } else {
            // Explicitly ensure no border is drawn
            ctx.strokeStyle = 'transparent';
            ctx.lineWidth = 0;
          }
          
          // Reset alpha before drawing image
          ctx.globalAlpha = 1;
          
          // Calculate image position within badge with padding
          const imageX = badgeX + horizontalPadding;
          const imageY = badgeY + verticalPadding;
          
          // Draw image at the correct position with scaled dimensions
          ctx.drawImage(img, imageX, imageY, imageWidth, imageHeight);
          
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