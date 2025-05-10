import React, { useState, useEffect, useRef } from 'react';

export interface BadgePosition {
  percentX: number;
  percentY: number;
}

interface BadgePositionerProps {
  onPositionChange: (position: BadgePosition) => void;
  initialPosition?: BadgePosition;
  containerRef: React.RefObject<HTMLElement>;
  children: React.ReactNode;
  dragEnabled?: boolean;
  badgeWidth?: number;
  badgeHeight?: number;
}

const BadgePositioner: React.FC<BadgePositionerProps> = ({ 
  onPositionChange, 
  initialPosition = { percentX: 5, percentY: 5 }, 
  containerRef,
  children,
  dragEnabled = true,
  badgeWidth = 100,
  badgeHeight = 100
}) => {
  const [position, setPosition] = useState<BadgePosition>(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const badgeRef = useRef<HTMLDivElement>(null);

  // Update position when initialPosition changes
  useEffect(() => {
    setPosition(initialPosition);
  }, [initialPosition]);

  // Convert percentage-based position to pixels
  const getPixelPosition = (): { x: number, y: number } => {
    if (!containerRef.current) return { x: 0, y: 0 };
    
    const containerRect = containerRef.current.getBoundingClientRect();
    return {
      x: (position.percentX / 100) * containerRect.width,
      y: (position.percentY / 100) * containerRect.height
    };
  };

  // Handle mouse down event to start dragging
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!dragEnabled) return;
    
    e.preventDefault();
    setIsDragging(true);
    
    if (badgeRef.current) {
      const badgeRect = badgeRef.current.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - badgeRect.left,
        y: e.clientY - badgeRect.top
      });
    }
  };

  // Handle mouse move event during dragging
  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;
    
    e.preventDefault();
    
    const containerRect = containerRef.current.getBoundingClientRect();
    
    // Calculate new position in pixels
    let newX = e.clientX - containerRect.left - dragOffset.x;
    let newY = e.clientY - containerRect.top - dragOffset.y;
    
    // Constrain to container boundaries
    newX = Math.max(0, Math.min(containerRect.width - badgeWidth, newX));
    newY = Math.max(0, Math.min(containerRect.height - badgeHeight, newY));
    
    // Convert to percentages
    const newPercentX = (newX / containerRect.width) * 100;
    const newPercentY = (newY / containerRect.height) * 100;
    
    setPosition({ percentX: newPercentX, percentY: newPercentY });
    onPositionChange({ percentX: newPercentX, percentY: newPercentY });
  };

  // Handle mouse up event to stop dragging
  const handleMouseUp = () => {
    if (isDragging) {
      setIsDragging(false);
    }
  };

  // Attach and detach global event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    } else {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  // Get pixel position for rendering
  const pixelPosition = getPixelPosition();

  return (
    <div
      ref={badgeRef}
      style={{
        position: 'absolute',
        left: `${pixelPosition.x}px`,
        top: `${pixelPosition.y}px`,
        width: `${badgeWidth}px`,
        height: `${badgeHeight}px`,
        cursor: dragEnabled ? 'move' : 'default',
        zIndex: isDragging ? 1000 : 1,
        userSelect: 'none'
      }}
      onMouseDown={handleMouseDown}
    >
      {children}
    </div>
  );
};

export default BadgePositioner;