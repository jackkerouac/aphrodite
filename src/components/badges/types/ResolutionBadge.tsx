import React, { useEffect, useRef } from 'react';

export interface ResolutionBadgeSettings {
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
  resolutionType?: string;
  useCustomText?: boolean;
  customText?: string;
}

interface ResolutionBadgeProps {
  settings: ResolutionBadgeSettings;
  onRender?: (canvas: HTMLCanvasElement) => void;
}

const ResolutionBadge: React.FC<ResolutionBadgeProps> = ({ settings, onRender }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const renderBadge = async () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Set canvas dimensions based on badge size
      canvas.width = settings.size * 2; // Make the badge wider for resolution text
      canvas.height = settings.size;

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

      // Draw resolution text
      const displayText = settings.useCustomText && settings.customText 
        ? settings.customText 
        : settings.resolutionType || '4K';
      
      ctx.globalAlpha = 1; // Reset alpha for text
      ctx.fillStyle = settings.textColor || '#FFFFFF';
      ctx.font = `${settings.fontSize || settings.size / 2}px ${settings.fontFamily || 'Arial'}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(displayText, canvas.width / 2, canvas.height / 2);

      // Notify parent component that rendering is complete
      if (onRender) {
        onRender(canvas);
      }
    };

    renderBadge();
  }, [settings, onRender]);

  return (
    <canvas
      ref={canvasRef}
      width={settings.size * 2}
      height={settings.size}
      style={{ 
        display: 'none', // Hide the canvas as it's only used for rendering
      }}
    />
  );
};

export default ResolutionBadge;