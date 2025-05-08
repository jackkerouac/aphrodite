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

      // Set canvas dimensions based on badge size, constrained to reasonable limits
      const size = typeof settings.size === 'number' ? settings.size : 80;
      const constrainedSize = Math.min(Math.max(size, 20), 200);
      
      console.log(`AudioBadge: Setting canvas size to ${constrainedSize}x${constrainedSize}`);
      canvas.width = constrainedSize;
      canvas.height = constrainedSize;

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
              // Calculate dimensions for a balanced padding all around
              const aspectRatio = img.width / img.height;
              let drawWidth, drawHeight;
              
              // Fixed padding of 10px on all sides
              const padding = 10;
              const maxWidth = canvas.width - (padding * 2);
              const maxHeight = canvas.height - (padding * 2);
              
              // Calculate dimensions to best fit within the available space
              if (aspectRatio > 1) { // Image is wider than tall
                // For wide images, use the full width minus padding
                drawWidth = maxWidth;
                drawHeight = drawWidth / aspectRatio;
                
                // If the height is too large, scale down
                if (drawHeight > maxHeight) {
                  drawHeight = maxHeight;
                  drawWidth = drawHeight * aspectRatio;
                }
              } else { // Image is taller than wide or square
                // For tall images, use the full height minus padding
                drawHeight = maxHeight;
                drawWidth = drawHeight * aspectRatio;
                
                // If the width is too large, scale down
                if (drawWidth > maxWidth) {
                  drawWidth = maxWidth;
                  drawHeight = drawWidth / aspectRatio;
                }
              }
              
              // Center the image
              const x = (canvas.width - drawWidth) / 2;
              const y = (canvas.height - drawHeight) / 2;
              
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

  // Get a properly constrained size value for the badge
  const getConstrainedSize = () => {
    const size = typeof settings.size === 'number' ? settings.size : 80;
    return Math.min(Math.max(size, 20), 200);
  };
  
  return (
    <canvas
      ref={canvasRef}
      width={getConstrainedSize()}
      height={getConstrainedSize()}
      style={{ 
        display: 'none', // Hide the canvas as it's only used for rendering
      }}
    />
  );
};

export default AudioBadge;