import React, { useEffect, useRef, useState } from 'react';
import { PosterDimensions } from '@/services/posterService';

// Import the images directly
import examplePoster from '../../assets/example_poster_light.png';

interface FixedPosterPreviewProps {
  onPosterLoad?: (dimensions: PosterDimensions) => void;
  onBadgePositionChange?: (type: string, position: { percentX: number, percentY: number }) => void;
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
  const [isDragging, setIsDragging] = useState(false);

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

  // Handle drag events for badge positioning
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    updateBadgePosition(e.clientX, e.clientY);
  };
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!activeBadgeType) return;
    setIsDragging(true);
    // Prevent default to avoid text selection during drag
    e.preventDefault();
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !activeBadgeType) return;
    updateBadgePosition(e.clientX, e.clientY);
    e.preventDefault(); // Prevent any text selection during dragging
  };
  
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  const updateBadgePosition = (clientX: number, clientY: number) => {
    if (!activeBadgeType || !posterContainerRef.current) return;
    
    const rect = posterContainerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    
    // Constrain position within the poster bounds
    const constrainedX = Math.max(0, Math.min(rect.width, x));
    const constrainedY = Math.max(0, Math.min(rect.height, y));
    
    // Convert to percentages - this is the center position of badge
    const percentX = (constrainedX / rect.width) * 100;
    const percentY = (constrainedY / rect.height) * 100;
    
    console.log(`Badge position updated: ${percentX.toFixed(2)}%, ${percentY.toFixed(2)}%`);
    
    if (onBadgePositionChange) {
      onBadgePositionChange(activeBadgeType, { percentX, percentY });
    }
  };
  
  // Clean up event listeners on unmount
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      setIsDragging(false);
    };
    
    // Add global mouse up listener to catch mouse up outside the component
    window.addEventListener('mouseup', handleGlobalMouseUp);
    
    return () => {
      window.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, []);

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
            
            {activeBadgeType && (
              <div 
                className="absolute top-0 left-0 w-full h-full cursor-move z-20"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
              />
            )}
            
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