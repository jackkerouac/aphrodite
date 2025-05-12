import React, { useRef, useEffect, useState } from 'react';
import { UnifiedBadgeSettings } from '@/types/unifiedBadgeSettings';
import { BadgeRenderer, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT } from './BadgeRenderer';

interface UnifiedBadgePreviewProps {
  badges: UnifiedBadgeSettings[];
  activeBadgeType?: string | null;
  className?: string;
  isDarkMode?: boolean;
  debugMode?: boolean;
}

/**
 * Component for displaying badge previews on a poster
 */
const UnifiedBadgePreview: React.FC<UnifiedBadgePreviewProps> = ({
  badges,
  activeBadgeType = null,
  className = '',
  isDarkMode = false,
  debugMode = false
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [posterLoaded, setPosterLoaded] = useState(false);
  
  // Load the poster image based on theme
  useEffect(() => {
    const loadPoster = async () => {
      if (!canvasRef.current) return;
      
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      
      try {
        // Load the appropriate poster based on theme
        const posterSrc = isDarkMode 
          ? '/src/assets/example_poster_dark.png'
          : '/src/assets/example_poster_light.png';
        
        const img = new Image();
        img.onload = () => {
          // Draw the poster as background
          ctx.drawImage(img, 0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
          setPosterLoaded(true);
        };
        img.onerror = (err) => {
          console.error('Failed to load poster image:', err);
          
          // Create a placeholder poster
          ctx.fillStyle = isDarkMode ? '#1e1e1e' : '#f5f5f5';
          ctx.fillRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
          setPosterLoaded(true);
        };
        img.src = posterSrc;
      } catch (error) {
        console.error('Error loading poster:', error);
      }
    };
    
    loadPoster();
  }, [isDarkMode]);
  
  // Render badges whenever they change or poster is loaded
  useEffect(() => {
    const renderBadges = async () => {
      if (!canvasRef.current || !posterLoaded) return;
      
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      
      try {
        // Create the badge renderer
        const renderer = new BadgeRenderer(
          ctx, 
          PREVIEW_CANVAS_WIDTH, 
          PREVIEW_CANVAS_HEIGHT,
          debugMode
        );
        
        // Only render badges that are enabled
        const enabledBadges = badges.filter(badge => badge !== null);
        
        // Render all enabled badges
        await renderer.renderBadges(enabledBadges, activeBadgeType);
      } catch (error) {
        console.error('Error rendering badges:', error);
      }
    };
    
    if (posterLoaded) {
      renderBadges();
    }
  }, [badges, activeBadgeType, posterLoaded, debugMode]);
  
  return (
    <div className={`unified-badge-preview ${className}`}>
      <canvas
        ref={canvasRef}
        width={PREVIEW_CANVAS_WIDTH}
        height={PREVIEW_CANVAS_HEIGHT}
        className="w-full h-auto border border-gray-300 shadow-sm rounded-lg"
      />
    </div>
  );
};

export default UnifiedBadgePreview;
