import React, { useEffect, useRef } from 'react';
import { getAudioCodecImagePath } from '@/utils/audioCodecUtils';

export interface AudioBadgeSettings {
  size: number;
  backgroundColor: string;
  backgroundOpacity: number;
  borderRadius?: number;
  borderWidth?: number;
  borderColor?: string;
  borderOpacity?: number;
  shadowEnabled?: boolean;
  shadowColor?: string;
  shadowBlur?: number;
  shadowOffsetX?: number;
  shadowOffsetY?: number;
  textColor?: string;
  fontFamily?: string;
  fontSize?: number;
  position?: {
    percentX: number;
    percentY: number;
  };
  codecType?: string;
}

interface AudioBadgeProps {
  settings: AudioBadgeSettings;
  onRender?: (canvas: HTMLCanvasElement) => void;
}

const AudioBadge: React.FC<AudioBadgeProps> = ({ settings, onRender }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Log when size settings change explicitly
  useEffect(() => {
    console.log('AudioBadge: Size setting changed to:', settings.size);
  }, [settings.size]);

  useEffect(() => {
    const renderBadge = async () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // We'll start with a temporary size, but adjust based on image dimensions later
      // Initialize with a placeholder size that will be replaced with actual image dimensions
      const initialSize = 200; // Temporary size before we know the image dimensions
      
      console.log(`AudioBadge: Setting initial canvas size to ${initialSize}x${initialSize}`);
      canvas.width = initialSize;
      canvas.height = initialSize;

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Apply background
      ctx.fillStyle = settings.backgroundColor;
      ctx.globalAlpha = settings.backgroundOpacity;
      
      if (settings.borderRadius) {
        // Draw rounded rectangle background
        const radius = settings.borderRadius;
        ctx.beginPath();
        ctx.moveTo(radius, 0);
        ctx.lineTo(canvas.width - radius, 0);
        ctx.quadraticCurveTo(canvas.width, 0, canvas.width, radius);
        ctx.lineTo(canvas.width, canvas.height - radius);
        ctx.quadraticCurveTo(canvas.width, canvas.height, canvas.width - radius, canvas.height);
        ctx.lineTo(radius, canvas.height);
        ctx.quadraticCurveTo(0, canvas.height, 0, canvas.height - radius);
        ctx.lineTo(0, radius);
        ctx.quadraticCurveTo(0, 0, radius, 0);
        ctx.closePath();
        ctx.fill();
      } else {
        // Draw rectangle background
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      // Apply border if specified
      if (settings.borderWidth && settings.borderWidth > 0) {
        ctx.strokeStyle = settings.borderColor || '#000000';
        ctx.globalAlpha = settings.borderOpacity || 1;
        ctx.lineWidth = settings.borderWidth;
        
        if (settings.borderRadius) {
          // Draw rounded rectangle border
          const radius = settings.borderRadius;
          const offset = settings.borderWidth / 2; // Adjust for line width
          ctx.beginPath();
          ctx.moveTo(radius, offset);
          ctx.lineTo(canvas.width - radius, offset);
          ctx.quadraticCurveTo(canvas.width - offset, offset, canvas.width - offset, radius);
          ctx.lineTo(canvas.width - offset, canvas.height - radius);
          ctx.quadraticCurveTo(canvas.width - offset, canvas.height - offset, canvas.width - radius, canvas.height - offset);
          ctx.lineTo(radius, canvas.height - offset);
          ctx.quadraticCurveTo(offset, canvas.height - offset, offset, canvas.height - radius);
          ctx.lineTo(offset, radius);
          ctx.quadraticCurveTo(offset, offset, radius, offset);
          ctx.closePath();
          ctx.stroke();
        } else {
          // Draw rectangle border
          ctx.strokeRect(
            settings.borderWidth / 2,
            settings.borderWidth / 2,
            canvas.width - settings.borderWidth,
            canvas.height - settings.borderWidth
          );
        }
      }

      // Apply shadow if enabled
      if (settings.shadowEnabled) {
        ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
        ctx.shadowBlur = settings.shadowBlur || 5;
        ctx.shadowOffsetX = settings.shadowOffsetX || 2;
        ctx.shadowOffsetY = settings.shadowOffsetY || 2;
      }

      // Draw codec image if specified
      if (settings.codecType) {
        try {
          // Reset alpha for image
          ctx.globalAlpha = 1;
          
          // Load the codec image
          const imagePath = getAudioCodecImagePath(settings.codecType);
          const img = new Image();
          
          await new Promise<void>((resolve, reject) => {
            img.onload = () => {
              // Instead of fitting image into a fixed-size badge, size the badge to fit the image
              const aspectRatio = img.width / img.height;
              
              // Define a minimal padding (2.5% of image width or 10px, whichever is smaller)
              const padding = Math.min(Math.round(img.width * 0.025), 10);
              
              // Set the badge size based on the image size plus padding
              const imageWidth = img.width;
              const imageHeight = img.height;
              
              // Resize canvas to exactly fit the image plus padding
              const canvasWidth = imageWidth + (padding * 2);
              const canvasHeight = imageHeight + (padding * 2);
              
              // Resize the canvas to match the image dimensions plus padding
              canvas.width = canvasWidth;
              canvas.height = canvasHeight;
              
              console.log(`AudioBadge: Resized canvas to ${canvasWidth}x${canvasHeight} based on image size`);
              
              // Clear canvas with the new dimensions and redraw background/border
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              
              // Redraw background with new dimensions
              ctx.fillStyle = settings.backgroundColor;
              ctx.globalAlpha = settings.backgroundOpacity;
              
              if (settings.borderRadius) {
                // Draw rounded rectangle background
                const radius = Math.min(settings.borderRadius, canvasWidth/4, canvasHeight/4); // Ensure radius isn't too large
                ctx.beginPath();
                ctx.moveTo(radius, 0);
                ctx.lineTo(canvas.width - radius, 0);
                ctx.quadraticCurveTo(canvas.width, 0, canvas.width, radius);
                ctx.lineTo(canvas.width, canvas.height - radius);
                ctx.quadraticCurveTo(canvas.width, canvas.height, canvas.width - radius, canvas.height);
                ctx.lineTo(radius, canvas.height);
                ctx.quadraticCurveTo(0, canvas.height, 0, canvas.height - radius);
                ctx.lineTo(0, radius);
                ctx.quadraticCurveTo(0, 0, radius, 0);
                ctx.closePath();
                ctx.fill();
              } else {
                // Draw rectangle background
                ctx.fillRect(0, 0, canvas.width, canvas.height);
              }
              
              // Redraw border if needed
              if (settings.borderWidth && settings.borderWidth > 0) {
                ctx.strokeStyle = settings.borderColor || '#000000';
                ctx.globalAlpha = settings.borderOpacity || 1;
                ctx.lineWidth = settings.borderWidth;
                
                if (settings.borderRadius) {
                  // Draw rounded rectangle border
                  const radius = Math.min(settings.borderRadius, canvasWidth/4, canvasHeight/4);
                  const offset = settings.borderWidth / 2;
                  ctx.beginPath();
                  ctx.moveTo(radius, offset);
                  ctx.lineTo(canvas.width - radius, offset);
                  ctx.quadraticCurveTo(canvas.width - offset, offset, canvas.width - offset, radius);
                  ctx.lineTo(canvas.width - offset, canvas.height - radius);
                  ctx.quadraticCurveTo(canvas.width - offset, canvas.height - offset, canvas.width - radius, canvas.height - offset);
                  ctx.lineTo(radius, canvas.height - offset);
                  ctx.quadraticCurveTo(offset, canvas.height - offset, offset, canvas.height - radius);
                  ctx.lineTo(offset, radius);
                  ctx.quadraticCurveTo(offset, offset, radius, offset);
                  ctx.closePath();
                  ctx.stroke();
                } else {
                  // Draw rectangle border
                  ctx.strokeRect(
                    settings.borderWidth / 2,
                    settings.borderWidth / 2,
                    canvas.width - settings.borderWidth,
                    canvas.height - settings.borderWidth
                  );
                }
              }
              
              // Apply shadow if enabled
              if (settings.shadowEnabled) {
                ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
                ctx.shadowBlur = settings.shadowBlur || 5;
                ctx.shadowOffsetX = settings.shadowOffsetX || 2;
                ctx.shadowOffsetY = settings.shadowOffsetY || 2;
              }
              
              // Reset alpha for image
              ctx.globalAlpha = 1;
              
              // Center the image with padding
              const drawWidth = imageWidth;
              const drawHeight = imageHeight;
              const x = padding;
              const y = padding;
              
              // Draw the image
              ctx.drawImage(img, x, y, drawWidth, drawHeight);
              resolve();
            };
            
            img.onerror = () => {
              console.error(`Failed to load codec image: ${imagePath}`);
              // Fallback to text if image fails to load
              ctx.fillStyle = settings.textColor || '#FFFFFF';
              // Ensure font size scales with badge size but stays readable
              ctx.font = `${settings.fontSize || Math.max(constrainedSize / 3, 10)}px ${settings.fontFamily || 'Arial'}`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(settings.codecType || '', canvas.width / 2, canvas.height / 2);
              resolve();
            };
            
            img.src = imagePath;
          });
        } catch (error) {
          console.error('Error rendering codec image:', error);
          // Fallback to text if there's an error
          ctx.fillStyle = settings.textColor || '#FFFFFF';
          // Ensure font size scales with badge size but stays readable
          ctx.font = `${settings.fontSize || Math.max(constrainedSize / 3, 10)}px ${settings.fontFamily || 'Arial'}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(settings.codecType, canvas.width / 2, canvas.height / 2);
        }
      }

      // Notify parent component that rendering is complete
      if (onRender) {
        onRender(canvas);
      }
    };

    renderBadge();
  }, [settings, onRender]);

  // We no longer need to constrain the size as it will be determined by the image
  // This is just used for the initial canvas render
  const getInitialSize = () => {
    return 200; // Initial size that will be replaced when image loads
  };
  
  return (
    <canvas
      ref={canvasRef}
      width={getInitialSize()}
      height={getInitialSize()}
      style={{ 
        display: 'none', // Hide the canvas as it's only used for rendering
      }}
    />
  );
};

export default AudioBadge;