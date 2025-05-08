import { ReviewBadgeSettings } from '@/components/badges/types/ReviewBadge';
import { createTempCanvas, drawRoundedRect } from './utils';

/**
 * Renders a review badge to a canvas
 * @param options The options for rendering the review badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderReviewBadge = async (
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
  
  if (options.borderRadius && options.borderRadius > 0) {
    // Draw rounded rectangle background
    console.log(`Drawing review badge with border radius: ${options.borderRadius}`);
    drawRoundedRect(ctx, 0, 0, canvas.width, canvas.height, options.borderRadius);
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
    
    if (options.borderRadius && options.borderRadius > 0) {
      // Draw rounded rectangle border
      const offset = options.borderWidth / 2;
      drawRoundedRect(
        ctx, 
        offset, 
        offset, 
        canvas.width - options.borderWidth, 
        canvas.height - options.borderWidth, 
        options.borderRadius - offset
      );
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