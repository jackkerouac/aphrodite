import React, { useRef, useEffect, useState } from 'react';
import { UnifiedBadgeSettings } from '@/types/unifiedBadgeSettings';
import { BadgeRenderer, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT } from './BadgeRenderer';

// Import poster images (this helps with Vite's asset handling)
import posterDarkJpg from '@/assets/example_poster_dark.jpg';
import posterLightJpg from '@/assets/example_poster_light.jpg';
import posterDarkPng from '@/assets/example_poster_dark.png';
import posterLightPng from '@/assets/example_poster_light.png';

// Import the image preloader utility
import '@/utils/imagePreloader';

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
  
  // Poster image references to persist across renders
  const [posterImageObj, setPosterImageObj] = useState<HTMLImageElement | null>(null);

  // Load the poster image based on theme
  useEffect(() => {
    const loadPoster = async () => {
      if (!canvasRef.current) return;
      
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      
      try {
        // First try loading the JPG version - use imported variables
        const posterSrcJpg = isDarkMode ? posterDarkJpg : posterLightJpg;
        
        // Fallback to PNG if the JPG fails - use imported variables
        const posterSrcPng = isDarkMode ? posterDarkPng : posterLightPng;
        
        // Try to load the primary image first
        const tryLoadImage = (src: string, fallbackSrc?: string) => {
          const img = new Image();
          img.onload = () => {
            // Draw the poster as background
            ctx.clearRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
            ctx.drawImage(img, 0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
            
            // Store the loaded image for future reference
            setPosterImageObj(img);
            setPosterLoaded(true);
          };
          img.onerror = (err) => {
            console.error(`Failed to load poster image: ${src}`, err);
            
            // Try the fallback if available
            if (fallbackSrc) {
              console.log(`Trying fallback image: ${fallbackSrc}`);
              tryLoadImage(fallbackSrc);
            } else {
              // Create a placeholder poster if all attempts fail
              ctx.fillStyle = isDarkMode ? '#1e1e1e' : '#f5f5f5';
              ctx.fillRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
              setPosterLoaded(true);
            }
          };
          img.src = src;
        };
        
        // Start with JPG, fallback to PNG
        tryLoadImage(posterSrcJpg, posterSrcPng);
      } catch (error) {
        console.error('Error loading poster:', error);
        // Create a placeholder if an exception occurs
        ctx.fillStyle = isDarkMode ? '#1e1e1e' : '#f5f5f5';
        ctx.fillRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
        setPosterLoaded(true);
      }
    };
    
    // Always reset the posterLoaded state and reload when isDarkMode changes
    setPosterLoaded(false);
    setPosterImageObj(null);
    loadPoster();
  }, [isDarkMode]);
  
  // Render badges whenever they change or poster is loaded
  useEffect(() => {
    const renderBadges = async () => {
      if (!canvasRef.current || !posterLoaded) return;
      
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      
      try {
        // Determine which poster image to use
        let posterImage: HTMLImageElement | null = posterImageObj;
        
        if (!posterImage) {
          // If we don't have the stored image object, create one
          const currentPosterSrc = isDarkMode ? posterDarkJpg : posterLightJpg;
          posterImage = new Image();
          posterImage.src = currentPosterSrc;
          
          // Wait for the image to load if it's not already cached
          if (!posterImage.complete) {
            await new Promise<void>((resolve, reject) => {
              posterImage!.onload = () => resolve();
              posterImage!.onerror = () => {
                console.error('Failed to load poster for badge rendering');
                reject();
              };
            });
          }
        }
        
        // Always redraw the poster first
        ctx.clearRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
        
        if (posterImage && posterImage.complete) {
          // If we have a valid poster image, draw it
          ctx.drawImage(posterImage, 0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
        } else {
          // Fallback to a colored rectangle if image isn't available
          ctx.fillStyle = isDarkMode ? '#1e1e1e' : '#f5f5f5';
          ctx.fillRect(0, 0, PREVIEW_CANVAS_WIDTH, PREVIEW_CANVAS_HEIGHT);
        }
        
        // Create the badge renderer after poster is drawn
        const renderer = new BadgeRenderer(
          ctx, 
          PREVIEW_CANVAS_WIDTH, 
          PREVIEW_CANVAS_HEIGHT,
          debugMode
        );
        
        // Only render badges that are enabled
        const enabledBadges = badges.filter(badge => badge !== null);
        
        // Render all enabled badges, skip clearing the canvas to preserve the poster
        await renderer.renderBadges(enabledBadges, activeBadgeType, true);
      } catch (error) {
        console.error('Error rendering badges:', error);
      }
    };
    
    if (posterLoaded) {
      renderBadges();
    }
  }, [badges, activeBadgeType, posterLoaded, debugMode, isDarkMode, posterImageObj]);
  
  return (
    <div className={`unified-badge-preview ${className}`}>
      <canvas
        ref={canvasRef}
        width={PREVIEW_CANVAS_WIDTH}
        height={PREVIEW_CANVAS_HEIGHT}
        className="w-full h-auto border border-gray-300 shadow-sm rounded-lg"
        style={{ maxWidth: '100%', objectFit: 'contain' }}
      />
    </div>
  );
};

export default UnifiedBadgePreview;
