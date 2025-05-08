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

      // Calculate extra space needed for shadow
      let canvasExtra = 0;
      let badgeX = 0;
      let badgeY = 0;
      const badgeWidth = canvas.width;
      const badgeHeight = canvas.height;
      
      // Add extra space for shadow if enabled
      if (settings.shadowEnabled) {
        const shadowOffsetX = settings.shadowOffsetX || 2;
        const shadowOffsetY = settings.shadowOffsetY || 2;
        const shadowBlur = settings.shadowBlur || 5;
        
        // Calculate shadow padding on all sides
        const shadowPaddingLeft = Math.max(0, -shadowOffsetX) + shadowBlur;
        const shadowPaddingTop = Math.max(0, -shadowOffsetY) + shadowBlur;
        const shadowPaddingRight = Math.max(0, shadowOffsetX) + shadowBlur;
        const shadowPaddingBottom = Math.max(0, shadowOffsetY) + shadowBlur;
        
        // Expand canvas to accommodate shadow
        const newWidth = canvas.width + shadowPaddingLeft + shadowPaddingRight;
        const newHeight = canvas.height + shadowPaddingTop + shadowPaddingBottom;
        
        // Resize canvas
        canvas.width = newWidth;
        canvas.height = newHeight;
        
        // Calculate badge position within shadow space
        badgeX = shadowPaddingLeft;
        badgeY = shadowPaddingTop;
      }
      
      // Apply shadow if enabled - moved here to affect the entire badge
      if (settings.shadowEnabled) {
        ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
        ctx.shadowBlur = settings.shadowBlur || 5;
        ctx.shadowOffsetX = settings.shadowOffsetX || 2;
        ctx.shadowOffsetY = settings.shadowOffsetY || 2;
      }

      // Apply background
      ctx.fillStyle = settings.backgroundColor;
      ctx.globalAlpha = settings.backgroundOpacity;
      
      if (settings.borderRadius) {
        // Draw rounded rectangle background
        const radius = settings.borderRadius;
        ctx.beginPath();
        ctx.moveTo(badgeX + radius, badgeY);
        ctx.lineTo(badgeX + badgeWidth - radius, badgeY);
        ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY, badgeX + badgeWidth, badgeY + radius);
        ctx.lineTo(badgeX + badgeWidth, badgeY + badgeHeight - radius);
        ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY + badgeHeight, badgeX + badgeWidth - radius, badgeY + badgeHeight);
        ctx.lineTo(badgeX + radius, badgeY + badgeHeight);
        ctx.quadraticCurveTo(badgeX, badgeY + badgeHeight, badgeX, badgeY + badgeHeight - radius);
        ctx.lineTo(badgeX, badgeY + radius);
        ctx.quadraticCurveTo(badgeX, badgeY, badgeX + radius, badgeY);
        ctx.closePath();
        ctx.fill();
      } else {
        // Draw rectangle background
        ctx.fillRect(badgeX, badgeY, badgeWidth, badgeHeight);
      }

      // Reset shadow for border to avoid doubling the effect
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;

      // Apply border if specified
      if (settings.borderWidth && settings.borderWidth > 0) {
        // Ensure border color is properly specified or use black as default
        ctx.strokeStyle = settings.borderColor || '#000000';
        // Ensure appropriate border opacity is applied
        ctx.globalAlpha = settings.borderOpacity !== undefined ? settings.borderOpacity : 1;
        // Set correct line width
        ctx.lineWidth = settings.borderWidth;
        
        if (settings.borderRadius) {
          // Draw rounded rectangle border
          const radius = settings.borderRadius;
          const offset = settings.borderWidth / 2; // Adjust for line width
          ctx.beginPath();
          ctx.moveTo(badgeX + radius, badgeY + offset);
          ctx.lineTo(badgeX + badgeWidth - radius, badgeY + offset);
          ctx.quadraticCurveTo(badgeX + badgeWidth - offset, badgeY + offset, badgeX + badgeWidth - offset, badgeY + radius);
          ctx.lineTo(badgeX + badgeWidth - offset, badgeY + badgeHeight - radius);
          ctx.quadraticCurveTo(badgeX + badgeWidth - offset, badgeY + badgeHeight - offset, badgeX + badgeWidth - radius, badgeY + badgeHeight - offset);
          ctx.lineTo(badgeX + radius, badgeY + badgeHeight - offset);
          ctx.quadraticCurveTo(badgeX + offset, badgeY + badgeHeight - offset, badgeX + offset, badgeY + badgeHeight - radius);
          ctx.lineTo(badgeX + offset, badgeY + radius);
          ctx.quadraticCurveTo(badgeX + offset, badgeY + offset, badgeX + radius, badgeY + offset);
          ctx.closePath();
          ctx.stroke();
        } else {
          // Draw rectangle border
          ctx.strokeRect(
            badgeX + settings.borderWidth / 2,
            badgeY + settings.borderWidth / 2,
            badgeWidth - settings.borderWidth,
            badgeHeight - settings.borderWidth
          );
        }
      }

      // Draw codec image if specified
      if (settings.codecType) {
        try {
          // Reset alpha and shadow for image
          ctx.globalAlpha = 1;
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
          
          // Load the codec image
          const imagePath = getAudioCodecImagePath(settings.codecType);
          const img = new Image();
          
          await new Promise<void>((resolve, reject) => {
            img.onload = () => {
              // Calculate image position to center it within the badge with proper padding
              // Add additional padding (8% of badge width) to ensure image doesn't touch borders
              const padding = Math.max(Math.round(badgeWidth * 0.08), 12);
              const availableWidth = badgeWidth - (padding * 2);
              const availableHeight = badgeHeight - (padding * 2);
              
              // Scale image to fit within available space while maintaining aspect ratio
              const scale = Math.min(
                availableWidth / img.width,
                availableHeight / img.height
              );
              
              const scaledWidth = img.width * scale;
              const scaledHeight = img.height * scale;
              
              // Center the scaled image within the available space
              const x = badgeX + (badgeWidth - scaledWidth) / 2;
              const y = badgeY + (badgeHeight - scaledHeight) / 2;
              
              // Draw the image with scaled dimensions to ensure proper padding
              ctx.drawImage(img, x, y, scaledWidth, scaledHeight);
              resolve();
            };
            img.onerror = () => {
              console.error(`Failed to load codec image: ${imagePath}`);
              // Fallback to text if image fails to load
              ctx.fillStyle = settings.textColor || '#FFFFFF';
              ctx.font = `${settings.fontSize || 12}px ${settings.fontFamily || 'Arial'}`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(settings.codecType || '', badgeX + badgeWidth / 2, badgeY + badgeHeight / 2);
              resolve();
            };
            
            img.src = imagePath;
          });
        } catch (error) {
          console.error('Error rendering codec image:', error);
          // Fallback to text if there's an error
          ctx.fillStyle = settings.textColor || '#FFFFFF';
          ctx.font = `${settings.fontSize || 12}px ${settings.fontFamily || 'Arial'}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(settings.codecType || '', badgeX + badgeWidth / 2, badgeY + badgeHeight / 2);
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