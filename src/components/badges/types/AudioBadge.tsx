import React, { useEffect, useRef } from 'react';
import { getAudioCodecImagePath } from '@/utils/audioCodecUtils';
import { BadgePosition } from '../PositionSelector';

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
  position: BadgePosition; // Updated to use BadgePosition enum
  margin: number; // Edge padding in pixels
  codecType?: string;
  enabled?: boolean; // Whether this badge is enabled (visible)
  useBrandColors?: boolean; // Whether to use brand-specific colors
}

interface AudioBadgeProps {
  settings: AudioBadgeSettings;
  onRender?: (canvas: HTMLCanvasElement) => void;
}

const AudioBadge: React.FC<AudioBadgeProps> = ({ settings, onRender }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const renderBadge = async () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Start with a temporary canvas size
      const initialSize = 200;
      
      canvas.width = initialSize;
      canvas.height = initialSize;

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
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
              // Get original image dimensions
              const originalWidth = img.width;
              const originalHeight = img.height;
              
              // Calculate the scaling factor based on the size setting
              // Use size to determine the target width of the image
              const targetImageWidth = settings.size || 100;
              const scaleFactor = targetImageWidth / originalWidth;
              
              // Scale image dimensions
              const imageWidth = Math.round(originalWidth * scaleFactor);
              const imageHeight = Math.round(originalHeight * scaleFactor);
              
              // Set border radius (if any) - scale proportionally with the size
              const borderRadius = settings.borderRadius ? settings.borderRadius * scaleFactor : 0;
              
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
              
              if (settings.shadowEnabled) {
                // Scale shadow parameters with the image size
                const shadowScaleFactor = Math.max(0.5, Math.min(1, scaleFactor));
                const shadowOffsetX = (settings.shadowOffsetX || 2) * shadowScaleFactor;
                const shadowOffsetY = (settings.shadowOffsetY || 2) * shadowScaleFactor;
                const shadowBlur = (settings.shadowBlur || 5) * shadowScaleFactor;
                
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
              if (settings.shadowEnabled) {
                const shadowScaleFactor = Math.max(0.5, Math.min(1, scaleFactor));
                ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
                ctx.shadowBlur = (settings.shadowBlur || 5) * shadowScaleFactor;
                ctx.shadowOffsetX = (settings.shadowOffsetX || 2) * shadowScaleFactor;
                ctx.shadowOffsetY = (settings.shadowOffsetY || 2) * shadowScaleFactor;
              }
              
              // Apply background with or without rounded corners
              ctx.fillStyle = settings.backgroundColor;
              ctx.globalAlpha = settings.backgroundOpacity;
              
              if (borderRadius > 0) {
                // Draw rounded rectangle background
                ctx.beginPath();
                ctx.moveTo(badgeX + borderRadius, badgeY);
                ctx.lineTo(badgeX + badgeWidth - borderRadius, badgeY);
                ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY, badgeX + badgeWidth, badgeY + borderRadius);
                ctx.lineTo(badgeX + badgeWidth, badgeY + badgeHeight - borderRadius);
                ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY + badgeHeight, badgeX + badgeWidth - borderRadius, badgeY + badgeHeight);
                ctx.lineTo(badgeX + borderRadius, badgeY + badgeHeight);
                ctx.quadraticCurveTo(badgeX, badgeY + badgeHeight, badgeX, badgeY + badgeHeight - borderRadius);
                ctx.lineTo(badgeX, badgeY + borderRadius);
                ctx.quadraticCurveTo(badgeX, badgeY, badgeX + borderRadius, badgeY);
                ctx.closePath();
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
              const scaledBorderWidth = settings.borderWidth ? settings.borderWidth * Math.min(1, scaleFactor) : 0;
              
              // ONLY draw a border if it's explicitly requested AND has width > 0 AND opacity > 0
              if (scaledBorderWidth > 0 && 
                  settings.borderOpacity !== undefined && 
                  settings.borderOpacity > 0) {
                
                // Set border properties
                ctx.strokeStyle = settings.borderColor || '#000000';
                ctx.globalAlpha = settings.borderOpacity;
                ctx.lineWidth = scaledBorderWidth;
                
                if (borderRadius > 0) {
                  // Draw rounded rectangle border
                  const offset = scaledBorderWidth / 2;
                  ctx.beginPath();
                  ctx.moveTo(badgeX + borderRadius, badgeY + offset);
                  ctx.lineTo(badgeX + badgeWidth - borderRadius, badgeY + offset);
                  ctx.quadraticCurveTo(badgeX + badgeWidth - offset, badgeY + offset, badgeX + badgeWidth - offset, badgeY + borderRadius);
                  ctx.lineTo(badgeX + badgeWidth - offset, badgeY + badgeHeight - borderRadius);
                  ctx.quadraticCurveTo(badgeX + badgeWidth - offset, badgeY + badgeHeight - offset, badgeX + badgeWidth - borderRadius, badgeY + badgeHeight - offset);
                  ctx.lineTo(badgeX + borderRadius, badgeY + badgeHeight - offset);
                  ctx.quadraticCurveTo(badgeX + offset, badgeY + badgeHeight - offset, badgeX + offset, badgeY + badgeHeight - borderRadius);
                  ctx.lineTo(badgeX + offset, badgeY + borderRadius);
                  ctx.quadraticCurveTo(badgeX + offset, badgeY + offset, badgeX + borderRadius, badgeY + offset);
                  ctx.closePath();
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
              
              // Notify parent component that rendering is complete
              if (onRender) {
                onRender(canvas);
              }
              
              resolve();
            };
            
            img.onerror = () => {
              console.error(`Failed to load codec image: ${imagePath}`);
              // Fallback to text if image fails to load
              ctx.fillStyle = settings.textColor || '#FFFFFF';
              ctx.font = `${settings.fontSize || 12}px ${settings.fontFamily || 'Arial'}`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(settings.codecType || '', canvas.width / 2, canvas.height / 2);
              
              if (onRender) {
                onRender(canvas);
              }
              
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
          ctx.fillText(settings.codecType || '', canvas.width / 2, canvas.height / 2);
          
          if (onRender) {
            onRender(canvas);
          }
        }
      } else {
        // No codec type specified, just render a placeholder
        ctx.fillStyle = settings.textColor || '#FFFFFF';
        ctx.font = `${settings.fontSize || 12}px ${settings.fontFamily || 'Arial'}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Audio', canvas.width / 2, canvas.height / 2);
        
        if (onRender) {
          onRender(canvas);
        }
      }
    };

    renderBadge();
  }, [settings, onRender]);
  
  return (
    <canvas
      ref={canvasRef}
      width={200}
      height={200}
      style={{ 
        display: 'none', // Hide the canvas as it's only used for rendering
      }}
    />
  );
};

export default AudioBadge;