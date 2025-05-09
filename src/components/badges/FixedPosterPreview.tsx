import React, { useEffect, useRef, useState } from 'react';
import { PosterDimensions } from '@/services/posterService';

// Import the images directly
import examplePoster from '../../assets/example_poster_light.png';

// Import the BadgePosition enum instead of using percentX/percentY
import { BadgePosition } from '../badges/PositionSelector';

interface FixedPosterPreviewProps {
  onPosterLoad?: (dimensions: PosterDimensions) => void;
  onBadgePositionChange?: (type: string, position: BadgePosition) => void;
  activeBadgeType?: string | null;
  renderBadges?: (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => void;
  debugMode?: boolean;
}

const FixedPosterPreview: React.FC<FixedPosterPreviewProps> = ({
  onPosterLoad,
  onBadgePositionChange,
  activeBadgeType,
  renderBadges,
  debugMode = false
}) => {
  const posterRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const posterContainerRef = useRef<HTMLDivElement>(null);
  const [posterDimensions, setPosterDimensions] = useState<PosterDimensions>({
    width: 400,
    height: 600,
    aspectRatio: 2/3,
  });
  const [loaded, setLoaded] = useState(false);
  // Handle image load
  const handleImageLoad = () => {
    // Hard-coded dimensions since we know the image
    const dimensions = {
      width: 400,
      height: 600,
      aspectRatio: 2/3
    };
    
    setPosterDimensions(dimensions);
    setLoaded(true);
    
    if (onPosterLoad) {
      onPosterLoad(dimensions);
    }
    
    if (canvasRef.current && renderBadges) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Calling renderBadges after image load');
        renderBadges(ctx, dimensions);
      }
    }
  };

  // Re-render badges when active badge type changes or when dimensions might have updated
  // The renderBadges function reference will change when any badge toggle state changes
  useEffect(() => {
    if (loaded && canvasRef.current && renderBadges) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('FixedPosterPreview: Forcing badge re-render');
        // Force clear the canvas to ensure a complete redraw
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        renderBadges(ctx, posterDimensions);
      }
    }
  }, [activeBadgeType, loaded, renderBadges, posterDimensions]);

  // The drag-and-drop functionality has been replaced by the PositionSelector component
  // The badge position is now managed through the BadgeControls components
  // which use the PositionSelector to select from predefined positions

  return (
    <div ref={containerRef} className="w-full flex justify-center p-0 m-0">
      <div 
        ref={posterContainerRef} 
        className="relative m-0" 
        style={{ width: '400px', height: '600px' }}
      >
        <img 
          ref={posterRef}
          src={examplePoster}
          alt="Poster Preview"
          width={400}
          height={600}
          onLoad={handleImageLoad}
          className="block m-0 p-0"
        />
        
        {loaded && (
          <>
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 pointer-events-none z-10"
              width={400}
              height={600}
            />
            
            {/* Debug Grid */}
            {debugMode && (
              <div className="absolute top-0 left-0 w-full h-full z-5 pointer-events-none">
                {/* Horizontal lines every 10% */}
                {Array.from({ length: 9 }).map((_, i) => (
                  <div 
                    key={`h-${i}`}
                    className="absolute w-full border-t border-red-500 border-dashed opacity-30"
                    style={{ top: `${(i + 1) * 10}%` }}
                  />
                ))}
                
                {/* Vertical lines every 10% */}
                {Array.from({ length: 9 }).map((_, i) => (
                  <div 
                    key={`v-${i}`}
                    className="absolute h-full border-l border-red-500 border-dashed opacity-30"
                    style={{ left: `${(i + 1) * 10}%` }}
                  />
                ))}
                
                {/* Position indicators for each corner and center */}
                <div className="absolute top-0 left-0 bg-yellow-500 text-xs px-1 opacity-50">0,0</div>
                <div className="absolute top-0 right-0 bg-yellow-500 text-xs px-1 opacity-50">100,0</div>
                <div className="absolute bottom-0 left-0 bg-yellow-500 text-xs px-1 opacity-50">0,100</div>
                <div className="absolute bottom-0 right-0 bg-yellow-500 text-xs px-1 opacity-50">100,100</div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-yellow-500 text-xs px-1 opacity-50">50,50</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default FixedPosterPreview;