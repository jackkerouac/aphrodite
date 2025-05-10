import React, { useEffect, useRef, useState } from 'react';
import { PosterDimensions } from '@/services/posterService';

// Import the images directly
import examplePoster from '../../assets/example_poster_light.png';

interface BadgePosition {
  type: string;
  percentX: number;
  percentY: number;
  width: number;
  height: number;
  canvas?: HTMLCanvasElement;
}

interface FixedPosterPreviewProps {
  onPosterLoad?: (dimensions: PosterDimensions) => void;
  onBadgePositionChange?: (type: string, position: { percentX: number, percentY: number }) => void;
  onBadgeSelect?: (type: string | null) => void;
  activeBadgeType?: string | null;
  renderBadges?: (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => void;
  getBadgePositions?: () => BadgePosition[];
  showAudioBadge?: boolean;
  showResolutionBadge?: boolean;
  showReviewBadge?: boolean;
  debugMode?: boolean;
}

const FixedPosterPreview: React.FC<FixedPosterPreviewProps> = ({
  onPosterLoad,
  onBadgePositionChange,
  onBadgeSelect,
  activeBadgeType,
  renderBadges,
  getBadgePositions,
  showAudioBadge = true,
  showResolutionBadge = true,
  showReviewBadge = true,
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
  const [badgePositions, setBadgePositions] = useState<BadgePosition[]>([]);
  const [hoveredBadgeType, setHoveredBadgeType] = useState<string | null>(null);

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
  }, [activeBadgeType, loaded, renderBadges, posterDimensions, canvasRef, 
      showAudioBadge, showResolutionBadge, showReviewBadge]);

  // Function to check if a point is within a badge
  const getBadgeAtPosition = (clientX: number, clientY: number): string | null => {
    if (!posterContainerRef.current || !badgePositions.length) return null;
    
    const rect = posterContainerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    
    // Convert to percentages
    const percentX = (x / rect.width) * 100;
    const percentY = (y / rect.height) * 100;
    
    // Check each badge to see if the point is inside it
    // Use visible flags to only consider visible badges
    for (const badge of badgePositions) {
      if ((badge.type === 'audio' && !showAudioBadge) ||
          (badge.type === 'resolution' && !showResolutionBadge) ||
          (badge.type === 'review' && !showReviewBadge)) {
        continue;
      }
      
      // Calculate badge bounds in percentage units
      const halfWidth = badge.width / 2;
      const halfHeight = badge.height / 2;
      
      const left = badge.percentX - halfWidth;
      const right = badge.percentX + halfWidth;
      const top = badge.percentY - halfHeight;
      const bottom = badge.percentY + halfHeight;
      
      // Add a small margin for easier selection (10% of badge size)
      const margin = Math.min(halfWidth, halfHeight) * 0.2;
      
      // Check if point is within badge bounds with margin
      if (percentX >= left - margin && 
          percentX <= right + margin && 
          percentY >= top - margin && 
          percentY <= bottom + margin) {
        return badge.type;
      }
    }
    
    return null;
  };

  // Handle drag events for badge positioning
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (activeBadgeType) {
      updateBadgePosition(e.clientX, e.clientY);
    }
  };
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!posterContainerRef.current) return;
    
    // Check if we clicked on a badge
    const badgeType = getBadgeAtPosition(e.clientX, e.clientY);
    
    if (badgeType) {
      // If we clicked on a badge, select it
      if (onBadgeSelect) {
        onBadgeSelect(badgeType);
      }
      setIsDragging(true);
    } else if (activeBadgeType) {
      // If we already have an active badge and clicked elsewhere, start dragging it
      setIsDragging(true);
    }
    
    // Prevent default to avoid text selection during drag
    e.preventDefault();
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!posterContainerRef.current) return;
    
    // Check if cursor is over a badge (for hover effect)
    if (!isDragging) {
      const badgeType = getBadgeAtPosition(e.clientX, e.clientY);
      setHoveredBadgeType(badgeType);
      
      // Change cursor to pointer if hovering over a badge
      if (badgeType) {
        document.body.style.cursor = 'pointer';
      } else if (activeBadgeType) {
        document.body.style.cursor = 'move';
      } else {
        document.body.style.cursor = 'default';
      }
    }
    
    // Handle dragging
    if (isDragging && activeBadgeType) {
      updateBadgePosition(e.clientX, e.clientY);
      e.preventDefault(); // Prevent any text selection during dragging
    }
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
  
  const handleMouseLeave = () => {
    setHoveredBadgeType(null);
    document.body.style.cursor = 'default';
  };
  
  // Clean up event listeners on unmount
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      setIsDragging(false);
      document.body.style.cursor = 'default';
    };
    
    // Add global mouse up listener to catch mouse up outside the component
    window.addEventListener('mouseup', handleGlobalMouseUp);
    
    return () => {
      window.removeEventListener('mouseup', handleGlobalMouseUp);
      document.body.style.cursor = 'default';
    };
  }, []);

  // Update badge positions when needed for selection
  useEffect(() => {
    // This would come from a callback from the parent component to get current badge positions
    if (getBadgePositions) {
      const positions = getBadgePositions();
      setBadgePositions(positions);
    }
  }, [getBadgePositions, activeBadgeType, showAudioBadge, showResolutionBadge, showReviewBadge]);

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
            
            <div 
              className="absolute top-0 left-0 w-full h-full cursor-default z-20"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseLeave}
            />
            
            {/* Badge Selection Indicators */}
            {badgePositions.map((badge) => {
              // Only display indicators for visible badges
              if ((badge.type === 'audio' && !showAudioBadge) ||
                  (badge.type === 'resolution' && !showResolutionBadge) ||
                  (badge.type === 'review' && !showReviewBadge)) {
                return null;
              }
              
              // Calculate position in pixels
              const left = (badge.percentX / 100) * posterDimensions.width;
              const top = (badge.percentY / 100) * posterDimensions.height;
              const width = badge.width;
              const height = badge.height;
              
              // Determine if this badge is active or hovered
              const isActive = activeBadgeType === badge.type;
              const isHovered = hoveredBadgeType === badge.type;
              
              return (
                <div 
                  key={badge.type}
                  className={`absolute pointer-events-none z-30 transform -translate-x-1/2 -translate-y-1/2 border-2 rounded ${
                    isActive ? 'border-blue-500' : 
                    isHovered ? 'border-blue-300' : 'border-transparent'
                  }`}
                  style={{
                    left: `${left}px`,
                    top: `${top}px`,
                    width: `${width + 10}px`,
                    height: `${height + 10}px`,
                    transition: 'border-color 0.2s ease'
                  }}
                />
              );
            })}
            
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