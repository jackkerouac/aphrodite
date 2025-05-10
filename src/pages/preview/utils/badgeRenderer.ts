import { renderBadgeToCanvas, extractBadgeWithTransparency } from "@/services/badgeRenderer";
import { getSourceImageUrlForResolution } from "@/utils/resolutionUtils";
import { PosterDimensions } from "@/services/posterService";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";
import { BadgePosition } from "@/components/badges/PositionSelector";
import { getBadgePositionStyles } from "@/lib/utils/badge-position";

/**
 * Renders all badges to the canvas
 */
export const renderBadges = async (
  ctx: CanvasRenderingContext2D, 
  dimensions: PosterDimensions,
  showAudioBadge: boolean,
  showResolutionBadge: boolean,
  showReviewBadge: boolean,
  audioBadgeSettings: AudioBadgeSettings,
  resolutionBadgeSettings: ResolutionBadgeSettings,
  reviewBadgeSettings: ReviewBadgeSettings,
  activeBadgeType: string | null,
  debugMode: boolean
) => {
  // Comprehensive debug logging 
  console.group('Badge Renderer');
  console.log('Toggle States:', { showAudioBadge, showResolutionBadge, showReviewBadge });
  console.log('Canvas Dimensions:', dimensions);
  console.log('Active Badge:', activeBadgeType);
  console.log('Debug Mode:', debugMode);
  
  // Return early if dimensions are invalid
  if (!dimensions || dimensions.width < 50 || dimensions.height < 50) {
    console.log('Invalid dimensions, skipping badge rendering');
    console.groupEnd();
    return;
  }
  
  // Clear the entire canvas before drawing
  console.log('Clearing canvas...');
  ctx.clearRect(0, 0, dimensions.width, dimensions.height);

  // Track which badges will be rendered
  const badgesToRender = [];
  if (showAudioBadge === true) badgesToRender.push('audio');
  if (showResolutionBadge === true) badgesToRender.push('resolution');
  if (showReviewBadge === true) badgesToRender.push('review');
  
  console.log(`Will render badges: ${badgesToRender.join(', ') || 'none'}`);
  
  // Create promises array to handle all badge rendering
  const renderPromises = [];

  // Add render tasks to the array - each badge will only be rendered if its toggle is ON
  // Explicit equality check to ensure proper boolean comparison
  if (showAudioBadge === true) {
    console.log('Adding audio badge to render queue');
    renderPromises.push(renderAudioBadge(
      ctx,
      dimensions,
      audioBadgeSettings,
      activeBadgeType === "audio",
      debugMode
    ));
  } else {
    console.log('Audio badge toggle is OFF, not rendering');
  }

  if (showResolutionBadge === true) {
    console.log('Adding resolution badge to render queue');
    renderPromises.push(renderResolutionBadge(
      ctx,
      dimensions,
      resolutionBadgeSettings,
      activeBadgeType === "resolution",
      debugMode
    ));
  } else {
    console.log('Resolution badge toggle is OFF, not rendering');
  }

  if (showReviewBadge === true) {
    console.log('Adding review badge to render queue');
    renderPromises.push(renderReviewBadge(
      ctx,
      dimensions,
      reviewBadgeSettings,
      activeBadgeType === "review",
      debugMode
    ));
  } else {
    console.log('Review badge toggle is OFF, not rendering');
  }

  // Wait for all rendering to complete
  if (renderPromises.length > 0) {
    console.log(`Rendering ${renderPromises.length} badges...`);
    await Promise.all(renderPromises);
    console.log('Badge rendering complete');
  } else {
    console.log('No badges to render');
  }
  
  console.groupEnd();
};

/**
 * Renders an audio badge to the canvas
 */
const renderAudioBadge = async (
  ctx: CanvasRenderingContext2D,
  dimensions: PosterDimensions,
  badgeSettings: AudioBadgeSettings,
  isActive: boolean,
  debugMode: boolean
) => {
  try {
    // Log the EXACT settings being used
    console.log('Rendering audio badge with settings:', badgeSettings);
    console.log('Audio badge size about to be used:', badgeSettings.size);
    
    // Render the audio badge - this now returns a dynamically sized canvas based on the image
    const result = await renderBadgeToCanvas("audio", badgeSettings);
    if (!result || !result.canvas) {
      console.error("Failed to get canvas for audio badge");
      return;
    }
    
    console.log('Result canvas dimensions:', result.canvas.width, 'x', result.canvas.height);
    
    // Calculate position based on the new BadgePosition enum
    const badgePosition = badgeSettings.position as BadgePosition || BadgePosition.TopLeft;
    
    // Get the position styles based on the BadgePosition
    const positionStyles = getBadgePositionStyles(badgePosition, badgeSettings.margin || 16);
    
    // Calculate the actual position based on the styles
    const { top, right, bottom, left, transform } = positionStyles;
    
    // Calculate centerX and centerY based on the position
    let centerX, centerY;
    
    // Calculate X position
    if (left === '50%') {
      // Center horizontally
      centerX = dimensions.width / 2;
    } else if (left !== undefined) {
      // Left positioning
      centerX = parseInt(left, 10) + result.canvas.width / 2;
    } else if (right !== undefined) {
      // Right positioning
      centerX = dimensions.width - parseInt(right, 10) - result.canvas.width / 2;
    } else {
      // Fallback to default (left)
      centerX = 16 + result.canvas.width / 2;
    }
    
    // Calculate Y position
    if (top === '50%') {
      // Center vertically
      centerY = dimensions.height / 2;
    } else if (top !== undefined) {
      // Top positioning
      centerY = parseInt(top, 10) + result.canvas.height / 2;
    } else if (bottom !== undefined) {
      // Bottom positioning
      centerY = dimensions.height - parseInt(bottom, 10) - result.canvas.height / 2;
    } else {
      // Fallback to default (top)
      centerY = 16 + result.canvas.height / 2;
    }
    
    // Calculate the top-left position by accounting for badge dimensions
    const posX = centerX - (result.canvas.width / 2);
    const posY = centerY - (result.canvas.height / 2);
    
    console.log(`Drawing audio badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
    ctx.drawImage(result.canvas, posX, posY);
    
    // Highlight active badge with a non-visible indicator if it's currently selected
    if (isActive && debugMode) {
      ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
      ctx.lineWidth = 2;
      ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
      
      // Draw center point marker for debugging
      if (debugMode) {
        ctx.fillStyle = '#ff0000';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  } catch (error) {
    console.error("Error rendering audio badge:", error);
  }
};

/**
 * Renders a resolution badge to the canvas
 */
const renderResolutionBadge = async (
  ctx: CanvasRenderingContext2D,
  dimensions: PosterDimensions,
  badgeSettings: ResolutionBadgeSettings,
  isActive: boolean,
  debugMode: boolean
) => {
  try {
    // Enhance resolution badge settings with utility functions if not already present
    const enhancedResolutionSettings = {
      ...badgeSettings,
      // Ensure we're using the styled mode, not direct image rendering
      directImageRender: false
    };
    
    // Get the proper image path for this resolution type
    try {
      const resolutionImageUrl = await getSourceImageUrlForResolution(badgeSettings.resolutionType || '1080');
      console.log('Using resolution image URL:', resolutionImageUrl);
      
      const result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings, resolutionImageUrl);
      if (!result || !result.canvas) {
        console.error("Failed to get canvas for resolution badge");
        return;
      }
      
      // Calculate position based on the new BadgePosition enum
      const badgePosition = badgeSettings.position as BadgePosition || BadgePosition.TopRight;
      
      // Get the position styles based on the BadgePosition
      const positionStyles = getBadgePositionStyles(badgePosition, badgeSettings.margin || 16);
      
      // Calculate the actual position based on the styles
      const { top, right, bottom, left, transform } = positionStyles;
      
      // Calculate centerX and centerY based on the position
      let centerX, centerY;
      
      // Calculate X position
      if (left === '50%') {
        // Center horizontally
        centerX = dimensions.width / 2;
      } else if (left !== undefined) {
        // Left positioning
        centerX = parseInt(left, 10) + result.canvas.width / 2;
      } else if (right !== undefined) {
        // Right positioning
        centerX = dimensions.width - parseInt(right, 10) - result.canvas.width / 2;
      } else {
        // Fallback to default (right)
        centerX = dimensions.width - 16 - result.canvas.width / 2;
      }
      
      // Calculate Y position
      if (top === '50%') {
        // Center vertically
        centerY = dimensions.height / 2;
      } else if (top !== undefined) {
        // Top positioning
        centerY = parseInt(top, 10) + result.canvas.height / 2;
      } else if (bottom !== undefined) {
        // Bottom positioning
        centerY = dimensions.height - parseInt(bottom, 10) - result.canvas.height / 2;
      } else {
        // Fallback to default (top)
        centerY = 16 + result.canvas.height / 2;
      }
      
      // Calculate the top-left position by accounting for badge dimensions
      const posX = centerX - (result.canvas.width / 2);
      const posY = centerY - (result.canvas.height / 2);
      
      console.log(`Drawing resolution badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
      ctx.drawImage(result.canvas, posX, posY);
      
      // Highlight active badge with a non-visible indicator if it's currently selected
      if (isActive && debugMode) {
        ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
        ctx.lineWidth = 2;
        ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
        
        // Draw center point marker for debugging
        if (debugMode) {
          ctx.fillStyle = '#ff0000';
          ctx.beginPath();
          ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    } catch (error) {
      console.error("Error loading resolution badge image:", error);
    }
  } catch (error) {
    console.error("Error rendering resolution badge:", error);
  }
};

/**
 * Renders a review badge to the canvas
 */
const renderReviewBadge = async (
  ctx: CanvasRenderingContext2D,
  dimensions: PosterDimensions,
  badgeSettings: ReviewBadgeSettings,
  isActive: boolean,
  debugMode: boolean
) => {
  try {
    const result = await renderBadgeToCanvas("review", badgeSettings);
    if (!result || !result.canvas) {
      console.error("Failed to get canvas for review badge");
      return;
    }
    
    // Calculate position based on the new BadgePosition enum
    const badgePosition = badgeSettings.position as BadgePosition || BadgePosition.BottomLeft;
    
    // Get the position styles based on the BadgePosition
    const positionStyles = getBadgePositionStyles(badgePosition, badgeSettings.margin || 16);
    
    // Calculate the actual position based on the styles
    const { top, right, bottom, left, transform } = positionStyles;
    
    // Calculate centerX and centerY based on the position
    let centerX, centerY;
    
    // Calculate X position
    if (left === '50%') {
      // Center horizontally
      centerX = dimensions.width / 2;
    } else if (left !== undefined) {
      // Left positioning
      centerX = parseInt(left, 10) + result.canvas.width / 2;
    } else if (right !== undefined) {
      // Right positioning
      centerX = dimensions.width - parseInt(right, 10) - result.canvas.width / 2;
    } else {
      // Fallback to default (left)
      centerX = 16 + result.canvas.width / 2;
    }
    
    // Calculate Y position
    if (top === '50%') {
      // Center vertically
      centerY = dimensions.height / 2;
    } else if (top !== undefined) {
      // Top positioning
      centerY = parseInt(top, 10) + result.canvas.height / 2;
    } else if (bottom !== undefined) {
      // Bottom positioning
      centerY = dimensions.height - parseInt(bottom, 10) - result.canvas.height / 2;
    } else {
      // Fallback to default (bottom)
      centerY = dimensions.height - 16 - result.canvas.height / 2;
    }
    
    // Calculate the top-left position by accounting for badge dimensions
    const posX = centerX - (result.canvas.width / 2);
    const posY = centerY - (result.canvas.height / 2);
    
    console.log(`Drawing review badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
    ctx.drawImage(result.canvas, posX, posY);
    
    // Highlight active badge with a non-visible indicator if it's currently selected
    if (isActive && debugMode) {
      ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
      ctx.lineWidth = 2;
      ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
      
      // Draw center point marker for debugging
      if (debugMode) {
        ctx.fillStyle = '#ff0000';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  } catch (error) {
    console.error("Error rendering review badge:", error);
  }
};

/**
 * Saves a badge as a PNG with transparency
 */
export const saveBadgeAsPng = async (
  type: string,
  audioBadgeSettings: AudioBadgeSettings,
  resolutionBadgeSettings: ResolutionBadgeSettings,
  reviewBadgeSettings: ReviewBadgeSettings
) => {
  try {
    let result;
    let bounds;
    
    switch (type) {
      case "audio":
        result = await renderBadgeToCanvas("audio", audioBadgeSettings);
        // Use the entire canvas as the bounds since we're now sizing it exactly to the image
        bounds = { 
          x: 0, 
          y: 0, 
          width: result.canvas.width, 
          height: result.canvas.height 
        };
        console.log(`Extracting audio badge with dimensions: ${result.canvas.width}x${result.canvas.height}`);
        break;
      case "resolution":
        // Enhance resolution settings with utility functions
        const enhancedResolutionSettings = {
          ...resolutionBadgeSettings,
          // Ensure we're using the styled mode, not direct image rendering
          directImageRender: false
        };
        
        // Get the proper image path for this resolution type
        try {
          const resolutionImageUrl = await getSourceImageUrlForResolution(resolutionBadgeSettings.resolutionType || '1080');
          console.log('Using resolution image URL for export:', resolutionImageUrl);
          
          result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings, resolutionImageUrl);
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
        } catch (error) {
          console.error("Error loading resolution badge image for export:", error);
          // Fallback to text-based rendering
          result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings);
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
        }
        break;
      case "review":
        result = await renderBadgeToCanvas("review", reviewBadgeSettings);
        bounds = { 
          x: 0, 
          y: 0, 
          width: result.canvas.width, 
          height: result.canvas.height 
        };
        break;
      default:
        throw new Error(`Unknown badge type: ${type}`);
    }
    
    const pngData = extractBadgeWithTransparency(result.canvas, bounds);
    
    // Create a download link
    const link = document.createElement("a");
    link.href = pngData;
    link.download = `${type}-badge.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error(`Error saving ${type} badge:`, error);
  }
};
