import React, { useEffect, useRef } from 'react';

export interface ReviewSource {
  name: string;
  rating: number;
  outOf?: number;
}

export interface ReviewBadgeSettings {
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
  sources?: ReviewSource[];
  displayFormat?: 'horizontal' | 'vertical';
  maxSourcesToShow?: number;
  showDividers?: boolean;
  dividerColor?: string;
  showIcons?: boolean;
}

interface ReviewBadgeProps {
  settings: ReviewBadgeSettings;
  onRender?: (canvas: HTMLCanvasElement) => void;
}

const ReviewBadge: React.FC<ReviewBadgeProps> = ({ settings, onRender }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const renderBadge = async () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Set canvas dimensions based on badge size
      const isHorizontal = settings.displayFormat !== 'vertical';
      const sources = settings.sources || [];
      const maxSources = settings.maxSourcesToShow || 2;
      const sourcesToShow = sources.slice(0, maxSources);
      
      // Calculate canvas dimensions based on layout and number of sources
      let canvasWidth, canvasHeight;
      if (isHorizontal) {
        canvasWidth = settings.size * (sourcesToShow.length * 1.5);
        canvasHeight = settings.size;
      } else {
        canvasWidth = settings.size * 1.5;
        canvasHeight = settings.size * sourcesToShow.length;
      }

      // Set minimum dimensions
      canvasWidth = Math.max(canvasWidth, settings.size);
      canvasHeight = Math.max(canvasHeight, settings.size);
      
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;

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

      // Draw review sources
      ctx.globalAlpha = 1; // Reset alpha for text
      ctx.fillStyle = settings.textColor || '#FFFFFF';
      ctx.font = `${settings.fontSize || settings.size / 3}px ${settings.fontFamily || 'Arial'}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      if (isHorizontal) {
        // Draw sources horizontally
        const sectionWidth = canvas.width / sourcesToShow.length;
        sourcesToShow.forEach((source, index) => {
          const x = sectionWidth * (index + 0.5);
          const y = canvas.height / 2;
          const outOf = source.outOf || 10;
          const text = `${source.name}: ${source.rating}/${outOf}`;
          ctx.fillText(text, x, y);
          
          // Draw divider if needed
          if (settings.showDividers && index < sourcesToShow.length - 1) {
            ctx.beginPath();
            ctx.moveTo(sectionWidth * (index + 1), canvas.height * 0.2);
            ctx.lineTo(sectionWidth * (index + 1), canvas.height * 0.8);
            ctx.strokeStyle = settings.dividerColor || settings.textColor || '#FFFFFF';
            ctx.stroke();
          }
        });
      } else {
        // Draw sources vertically
        const sectionHeight = canvas.height / sourcesToShow.length;
        sourcesToShow.forEach((source, index) => {
          const x = canvas.width / 2;
          const y = sectionHeight * (index + 0.5);
          const outOf = source.outOf || 10;
          const text = `${source.name}: ${source.rating}/${outOf}`;
          ctx.fillText(text, x, y);
          
          // Draw divider if needed
          if (settings.showDividers && index < sourcesToShow.length - 1) {
            ctx.beginPath();
            ctx.moveTo(canvas.width * 0.2, sectionHeight * (index + 1));
            ctx.lineTo(canvas.width * 0.8, sectionHeight * (index + 1));
            ctx.strokeStyle = settings.dividerColor || settings.textColor || '#FFFFFF';
            ctx.stroke();
          }
        });
      }

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
      style={{ 
        display: 'none', // Hide the canvas as it's only used for rendering
      }}
    />
  );
};

export default ReviewBadge;