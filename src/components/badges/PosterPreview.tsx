import React, { useEffect, useRef, useState } from 'react';
import { PosterDimensions } from '@/services/posterService';

interface BadgePosition {
  percentX: number;
  percentY: number;
}

interface BadgeSettings {
  position: BadgePosition;
  // Other badge settings could be included here
}

interface BadgesMap {
  audio?: BadgeSettings;
  resolution?: BadgeSettings;
  review?: BadgeSettings;
}

interface PosterPreviewProps {
  posterUrl: string;
  badges?: BadgesMap;
  onPosterLoad?: (dimensions: PosterDimensions) => void;
  onBadgePositionChange?: (type: string, position: BadgePosition) => void;
  activeBadgeType?: string | null;
  renderBadges?: (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => void;
}

const PosterPreview: React.FC<PosterPreviewProps> = ({ 
  posterUrl, 
  badges = {},
  onPosterLoad,
  onBadgePositionChange,
  activeBadgeType,
  renderBadges
}) => {
  const posterRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [posterDimensions, setPosterDimensions] = useState<PosterDimensions>({
    width: 0,
    height: 0,
    aspectRatio: 1,
  });
  const [isLoading, setIsLoading] = useState(true);

  // Simple direct image loader
  useEffect(() => {
    // If there's no image URL, don't try to load anything
    if (!posterUrl) {
      setIsLoading(false);
      return;
    }

    // Set up an image element to load the poster
    const img = new Image();
    
    img.onload = () => {
      console.log('Image loaded successfully with natural dimensions:', img.width, 'x', img.height);
      
      // Calculate a reasonable display size (max width 500px)
      const maxWidth = 500;
      const aspectRatio = img.width / img.height;
      const width = Math.min(maxWidth, img.width);
      const height = width / aspectRatio;
      
      // Set dimensions for the component
      const dimensions = {
        width,
        height,
        aspectRatio
      };
      
      // Update state with dimensions
      setPosterDimensions(dimensions);
      setIsLoading(false);
      
      // Notify parent component
      if (onPosterLoad) {
        onPosterLoad(dimensions);
      }
      
      // Set up canvas
      if (canvasRef.current && renderBadges) {
        canvasRef.current.width = width;
        canvasRef.current.height = height;
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          renderBadges(ctx, dimensions);
        }
      }
    };
    
    img.onerror = (error) => {
      console.error('Error loading image:', error);
      setIsLoading(false);
    };
    
    // Start loading the image
    img.src = posterUrl;
    console.log('Started loading image from URL:', posterUrl);
  }, [posterUrl, onPosterLoad, renderBadges]);

  // Handle drag events for badge positioning
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    
    if (!activeBadgeType || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert to percentages
    const percentX = (x / rect.width) * 100;
    const percentY = (y / rect.height) * 100;
    
    if (onBadgePositionChange) {
      onBadgePositionChange(activeBadgeType, { percentX, percentY });
    }
  };

  return (
    <div ref={containerRef} className="w-full flex justify-center">
      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-64 w-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-sm text-muted-foreground">Loading poster...</p>
        </div>
      ) : (
        <div 
          className="relative"
          style={{ 
            width: posterDimensions.width > 0 ? `${posterDimensions.width}px` : 'auto',
            height: posterDimensions.height > 0 ? `${posterDimensions.height}px` : 'auto',
          }}
        >
          <img 
            ref={posterRef}
            src={posterUrl} 
            alt="Poster Preview"
            width={posterDimensions.width || undefined}
            height={posterDimensions.height || undefined}
            className="block"
          />
          
          {posterDimensions.width > 0 && (
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 pointer-events-none"
              width={posterDimensions.width}
              height={posterDimensions.height}
            />
          )}
          
          {activeBadgeType && posterDimensions.width > 0 && (
            <div 
              className="absolute top-0 left-0 w-full h-full cursor-move"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default PosterPreview;