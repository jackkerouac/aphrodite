import { AudioBadgeSettings } from '@/components/badges/types/AudioBadge';
import { ResolutionBadgeSettings } from '@/components/badges/types/ResolutionBadge';
import { ReviewBadgeSettings, ReviewSource } from '@/components/badges/types/ReviewBadge';
import { getAudioCodecImagePath } from '@/utils/audioCodecUtils';

export type BadgeType = 'audio' | 'resolution' | 'review';

export interface BadgeRenderingCommonOptions {
  position?: {
    percentX: number;
    percentY: number;
  };
}

export interface BadgeRenderingResult {
  canvas: HTMLCanvasElement;
  position?: {
    percentX: number;
    percentY: number;
  };
}

// Helper function to create a temporary canvas in the DOM
const createTempCanvas = (width: number, height: number): HTMLCanvasElement => {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return canvas;
};

/**
 * Renders a badge to a canvas based on the badge type and options
 * @param type The type of badge to render
 * @param options The options for rendering the badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderBadgeToCanvas = async (
  type: BadgeType,
  options: AudioBadgeSettings | ResolutionBadgeSettings | ReviewBadgeSettings & BadgeRenderingCommonOptions,
  sourceImageUrl?: string
): Promise<BadgeRenderingResult> => {
  const position = options.position || { percentX: 0, percentY: 0 };
  let canvas: HTMLCanvasElement;
  
  switch (type) {
    case 'audio': {
      const audioOptions = options as AudioBadgeSettings;
      canvas = await renderAudioBadge(audioOptions, sourceImageUrl);
      break;
    }
    case 'resolution': {
      const resolutionOptions = options as ResolutionBadgeSettings;
      canvas = await renderResolutionBadge(resolutionOptions, sourceImageUrl);
      break;
    }
    case 'review': {
      const reviewOptions = options as ReviewBadgeSettings;
      canvas = await renderReviewBadge(reviewOptions, sourceImageUrl);
      break;
    }
    default:
      throw new Error(`Unsupported badge type: ${type}`);
  }

  return {
    canvas,
    position
  };
};

/**
 * Renders an audio badge to a canvas
 * @param options The options for rendering the audio badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
const renderAudioBadge = async (
  options: AudioBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  // Scale the size to a reasonable value relative to the poster
  // Keep the original size for calculations but use a scaled version for the canvas
  const badgeSize = Math.min(options.size, 200);
  const canvas = createTempCanvas(badgeSize, badgeSize);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error("Could not get canvas context");
  }

  // If we have a source image, load and draw it
  if (sourceImageUrl) {
    await new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve();
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${sourceImageUrl}`));
      img.src = sourceImageUrl;
    });
    return canvas;
  }

  // Apply background
  ctx.fillStyle = options.backgroundColor;
  ctx.globalAlpha = options.backgroundOpacity;
  
  if (options.borderRadius) {
    // Draw rounded rectangle background
    const radius = options.borderRadius;
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
  if (options.borderWidth && options.borderWidth > 0) {
    ctx.strokeStyle = options.borderColor || '#000000';
    ctx.globalAlpha = options.borderOpacity || 1;
    ctx.lineWidth = options.borderWidth;
    
    if (options.borderRadius) {
      // Draw rounded rectangle border
      const radius = options.borderRadius;
      const offset = options.borderWidth / 2; // Adjust for line width
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
        options.borderWidth / 2,
        options.borderWidth / 2,
        canvas.width - options.borderWidth,
        canvas.height - options.borderWidth
      );
    }
  }

  // Apply shadow if enabled
  if (options.shadowEnabled) {
    ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = options.shadowBlur || 5;
    ctx.shadowOffsetX = options.shadowOffsetX || 2;
    ctx.shadowOffsetY = options.shadowOffsetY || 2;
  }

  // Draw codec image if specified
  if (options.codecType) {
    try {
      // Reset alpha for image
      ctx.globalAlpha = 1;
      
      // Load the codec image
      const imagePath = getAudioCodecImagePath(options.codecType);
      const img = new Image();
      
      await new Promise<void>((resolve, reject) => {
        img.onload = () => {
          // Calculate dimensions to maintain aspect ratio
          const aspectRatio = img.width / img.height;
          let drawWidth, drawHeight;
          
          // If image is wider than tall
          if (aspectRatio > 1) {
            drawWidth = canvas.width * 0.8;
            drawHeight = drawWidth / aspectRatio;
          } else {
            drawHeight = canvas.height * 0.8;
            drawWidth = drawHeight * aspectRatio;
          }
          
          // Center the image
          const x = (canvas.width - drawWidth) / 2;
          const y = (canvas.height - drawHeight) / 2;
          
          // Draw the image
          ctx.drawImage(img, x, y, drawWidth, drawHeight);
          resolve();
        };
        
        img.onerror = () => {
          console.error(`Failed to load codec image: ${imagePath}`);
          // Fallback to text if image fails to load
          ctx.fillStyle = options.textColor || '#FFFFFF';
          ctx.font = `${options.fontSize || options.size / 3}px ${options.fontFamily || 'Arial'}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(options.codecType || '', canvas.width / 2, canvas.height / 2);
          resolve();
        };
        
        img.src = imagePath;
      });
    } catch (error) {
      console.error('Error rendering codec image:', error);
      // Fallback to text if there's an error
      ctx.fillStyle = options.textColor || '#FFFFFF';
      ctx.font = `${options.fontSize || options.size / 3}px ${options.fontFamily || 'Arial'}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(options.codecType, canvas.width / 2, canvas.height / 2);
    }
  }

  return canvas;
};

/**
 * Renders a resolution badge to a canvas
 * @param options The options for rendering the resolution badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
const renderResolutionBadge = async (
  options: ResolutionBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  // Scale the size to a reasonable value relative to the poster
  const scaledSize = Math.min(options.size, 200);
  const canvas = createTempCanvas(scaledSize * 2, scaledSize);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error("Could not get canvas context");
  }

  // If we have a source image, load and draw it
  if (sourceImageUrl) {
    await new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve();
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${sourceImageUrl}`));
      img.src = sourceImageUrl;
    });
    return canvas;
  }

  // Apply background
  ctx.fillStyle = options.backgroundColor;
  ctx.globalAlpha = options.backgroundOpacity;
  
  if (options.borderRadius) {
    // Draw rounded rectangle background
    const radius = options.borderRadius;
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
  if (options.borderWidth && options.borderWidth > 0) {
    ctx.strokeStyle = options.borderColor || '#000000';
    ctx.globalAlpha = options.borderOpacity || 1;
    ctx.lineWidth = options.borderWidth;
    
    if (options.borderRadius) {
      // Draw rounded rectangle border
      const radius = options.borderRadius;
      const offset = options.borderWidth / 2; // Adjust for line width
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
        options.borderWidth / 2,
        options.borderWidth / 2,
        canvas.width - options.borderWidth,
        canvas.height - options.borderWidth
      );
    }
  }

  // Apply shadow if enabled
  if (options.shadowEnabled) {
    ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = options.shadowBlur || 5;
    ctx.shadowOffsetX = options.shadowOffsetX || 2;
    ctx.shadowOffsetY = options.shadowOffsetY || 2;
  }

  // Draw resolution text
  const displayText = options.useCustomText && options.customText 
    ? options.customText 
    : options.resolutionType || '4K';
  
  ctx.globalAlpha = 1; // Reset alpha for text
  ctx.fillStyle = options.textColor || '#FFFFFF';
  ctx.font = `${options.fontSize || options.size / 2}px ${options.fontFamily || 'Arial'}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(displayText, canvas.width / 2, canvas.height / 2);

  return canvas;
};

/**
 * Renders a review badge to a canvas
 * @param options The options for rendering the review badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
const renderReviewBadge = async (
  options: ReviewBadgeSettings, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  const isHorizontal = options.displayFormat !== 'vertical';
  const sources = options.sources || [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ];
  const maxSources = options.maxSourcesToShow || 2;
  const sourcesToShow = sources.slice(0, maxSources);
  
  // Scale the size to a reasonable value relative to the poster
  const scaledSize = Math.min(options.size, 200);
  
  // Calculate canvas dimensions based on layout and number of sources
  let canvasWidth, canvasHeight;
  if (isHorizontal) {
    canvasWidth = scaledSize * (sourcesToShow.length * 1.5);
    canvasHeight = scaledSize;
  } else {
    canvasWidth = scaledSize * 1.5;
    canvasHeight = scaledSize * sourcesToShow.length;
  }

  // Set minimum dimensions
  canvasWidth = Math.max(canvasWidth, scaledSize);
  canvasHeight = Math.max(canvasHeight, scaledSize);

  const canvas = createTempCanvas(canvasWidth, canvasHeight);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error("Could not get canvas context");
  }

  // If we have a source image, load and draw it
  if (sourceImageUrl) {
    await new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve();
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${sourceImageUrl}`));
      img.src = sourceImageUrl;
    });
    return canvas;
  }

  // Apply background
  ctx.fillStyle = options.backgroundColor;
  ctx.globalAlpha = options.backgroundOpacity;
  
  if (options.borderRadius) {
    // Draw rounded rectangle background
    const radius = options.borderRadius;
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
  if (options.borderWidth && options.borderWidth > 0) {
    ctx.strokeStyle = options.borderColor || '#000000';
    ctx.globalAlpha = options.borderOpacity || 1;
    ctx.lineWidth = options.borderWidth;
    
    if (options.borderRadius) {
      // Draw rounded rectangle border
      const radius = options.borderRadius;
      const offset = options.borderWidth / 2;
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
        options.borderWidth / 2,
        options.borderWidth / 2,
        canvas.width - options.borderWidth,
        canvas.height - options.borderWidth
      );
    }
  }

  // Apply shadow if enabled
  if (options.shadowEnabled) {
    ctx.shadowColor = options.shadowColor || 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = options.shadowBlur || 5;
    ctx.shadowOffsetX = options.shadowOffsetX || 2;
    ctx.shadowOffsetY = options.shadowOffsetY || 2;
  }

  // Draw review sources
  ctx.globalAlpha = 1; // Reset alpha for text
  ctx.fillStyle = options.textColor || '#FFFFFF';
  ctx.font = `${options.fontSize || options.size / 3}px ${options.fontFamily || 'Arial'}`;
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
      if (options.showDividers && index < sourcesToShow.length - 1) {
        ctx.beginPath();
        ctx.moveTo(sectionWidth * (index + 1), canvas.height * 0.2);
        ctx.lineTo(sectionWidth * (index + 1), canvas.height * 0.8);
        ctx.strokeStyle = options.dividerColor || options.textColor || '#FFFFFF';
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
      if (options.showDividers && index < sourcesToShow.length - 1) {
        ctx.beginPath();
        ctx.moveTo(canvas.width * 0.2, sectionHeight * (index + 1));
        ctx.lineTo(canvas.width * 0.8, sectionHeight * (index + 1));
        ctx.strokeStyle = options.dividerColor || options.textColor || '#FFFFFF';
        ctx.stroke();
      }
    });
  }

  return canvas;
};

/**
 * Extracts a badge from a canvas with transparent background
 * @param canvas The canvas containing the badge
 * @param badgeBounds The bounds of the badge to extract
 * @returns Base64 encoded PNG data URL
 */
export const extractBadgeWithTransparency = (
  canvas: HTMLCanvasElement,
  badgeBounds: {x: number, y: number, width: number, height: number}
): string => {
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = badgeBounds.width;
  tempCanvas.height = badgeBounds.height;
  const tempCtx = tempCanvas.getContext('2d');

  if (!tempCtx) {
    throw new Error("Could not get canvas context");
  }

  tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
  tempCtx.drawImage(
    canvas,
    badgeBounds.x,
    badgeBounds.y,
    badgeBounds.width,
    badgeBounds.height,
    0,
    0,
    badgeBounds.width,
    badgeBounds.height
  );

  return tempCanvas.toDataURL('image/png');
};