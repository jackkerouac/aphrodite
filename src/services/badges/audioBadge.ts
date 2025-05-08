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
          // Calculate minimal padding (2.5% of image width or 10px, whichever is smaller)
          const baseImagePadding = Math.min(Math.round(img.width * 0.025), 10);
          
          // Calculate scale factor based on the size option
          const scaleFactor = options.size / Math.max(img.width, img.height);
          
          // Scale the image dimensions
          const imageWidth = img.width * scaleFactor;
          const imageHeight = img.height * scaleFactor;
          
          // Add extra padding for border radius (if specified)
          // This ensures we have enough space for the rounded corners
          const borderRadius = options.borderRadius || 0;
          const totalPadding = Math.max(baseImagePadding, borderRadius / 2);
          
          // Set canvas dimensions to accommodate the image plus padding
          const canvasWidth = imageWidth + (totalPadding * 2);
          const canvasHeight = imageHeight + (totalPadding * 2);
          
          // Resize the canvas
          canvas.width = canvasWidth;
          canvas.height = canvasHeight;
          
          // Clear canvas
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          // Apply background with or without rounded corners
          ctx.fillStyle = options.backgroundColor;
          ctx.globalAlpha = options.backgroundOpacity;
          
          if (borderRadius > 0) {
            // Draw rounded rectangle background
            console.log(`Drawing audio badge with border radius: ${borderRadius}`);
            drawRoundedRect(ctx, 0, 0, canvasWidth, canvasHeight, borderRadius);
            ctx.fill();
          } else {
            // Draw regular rectangle background
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
          }
          
          // Apply border if specified
          if (options.borderWidth && options.borderWidth > 0) {
            ctx.strokeStyle = options.borderColor || '#000000';
            ctx.globalAlpha = options.borderOpacity || 1;
            ctx.lineWidth = options.borderWidth;
            
            if (borderRadius > 0) {
              // Draw rounded rectangle border
              const offset = options.borderWidth / 2;
              drawRoundedRect(
                ctx, 
                offset, 
                offset, 
                canvasWidth - options.borderWidth, 
                canvasHeight - options.borderWidth, 
                borderRadius - offset
              );
              ctx.stroke();
            } else {
              // Draw rectangle border
              ctx.strokeRect(
                options.borderWidth / 2,
                options.borderWidth / 2,
                canvasWidth - options.borderWidth,
                canvasHeight - options.borderWidth
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
          
          // Reset alpha for image
          ctx.globalAlpha = 1;
          
          // Center the image within the canvas
          const x = (canvasWidth - imageWidth) / 2;
          const y = (canvasHeight - imageHeight) / 2;
          
          // Draw the image
          ctx.drawImage(img, x, y, imageWidth, imageHeight);
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