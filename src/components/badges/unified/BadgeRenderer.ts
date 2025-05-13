import { UnifiedBadgeSettings, BadgePosition, AudioBadgeSettings, ResolutionBadgeSettings, ReviewBadgeSettings } from '@/types/unifiedBadgeSettings';
import { getBadgePositionStyles } from '@/lib/utils/badge-position';
import { getSourceImageUrlForResolution } from '@/utils/resolutionUtils';
import { getAudioCodecIcon } from '@/utils/audioCodecUtils';

// Canvas dimensions for the badge preview
export const PREVIEW_CANVAS_WIDTH = 1000;
export const PREVIEW_CANVAS_HEIGHT = 1500;

/**
 * Main badge renderer class responsible for drawing badges on a canvas
 * based on unified badge settings
 */
export class BadgeRenderer {
  private ctx: CanvasRenderingContext2D;
  private width: number;
  private height: number;
  private debugMode: boolean;

  /**
   * Create a new BadgeRenderer instance
   * @param ctx - The canvas 2D context to draw on
   * @param width - Canvas width
   * @param height - Canvas height
   * @param debugMode - Whether to show debug information
   */
  constructor(
    ctx: CanvasRenderingContext2D,
    width: number = PREVIEW_CANVAS_WIDTH,
    height: number = PREVIEW_CANVAS_HEIGHT,
    debugMode: boolean = false
  ) {
    this.ctx = ctx;
    this.width = width;
    this.height = height;
    this.debugMode = debugMode;
  }

  /**
   * Clear the entire canvas
   */
  clear(): void {
    // Don't clear the canvas - this will remove the poster image
    // Instead, handle clearing in the UnifiedBadgePreview component
    // this.ctx.clearRect(0, 0, this.width, this.height);
    console.log('Canvas clear method called but skipped to preserve poster');
  }

  /**
   * Renders multiple badges on the canvas
   * @param badges - Array of badge settings to render
   * @param activeBadgeType - Currently selected badge type (for highlighting)
   * @param skipClear - If true, skip clearing the canvas (to preserve the background)
   */
  async renderBadges(
    badges: UnifiedBadgeSettings[],
    activeBadgeType: string | null = null,
    skipClear: boolean = true
  ): Promise<void> {
    // Only clear the canvas if explicitly requested
    if (!skipClear) {
      this.clear();
    }

    for (const badge of badges) {
      await this.renderBadge(badge, activeBadgeType === badge.badge_type);
    }
  }

  /**
   * Render a single badge on the canvas
   * @param badgeSettings - The badge settings to use
   * @param isActive - Whether this badge is currently selected
   */
  async renderBadge(
    badgeSettings: UnifiedBadgeSettings,
    isActive: boolean = false
  ): Promise<HTMLCanvasElement | null> {
    try {
      console.log(`Rendering ${badgeSettings.badge_type} badge`, badgeSettings);
      
      // Save the current canvas state to preserve the background
      this.ctx.save();
      
      // Create the badge canvas
      const badgeCanvas = await this.createBadgeCanvas(badgeSettings);
      
      if (!badgeCanvas) {
        console.error(`Failed to create canvas for ${badgeSettings.badge_type} badge`);
        this.ctx.restore();
        return null;
      }
      
      // Calculate position on the main canvas
      const { x, y } = this.calculateBadgePosition(
        badgeSettings.badge_position,
        badgeCanvas.width,
        badgeCanvas.height,
        badgeSettings.edge_padding
      );
      
      // Draw the badge on the main canvas
      this.ctx.drawImage(badgeCanvas, x, y);
      
      // If this badge is active, highlight it
      if (isActive && this.debugMode) {
        this.highlightActiveBadge(x, y, badgeCanvas.width, badgeCanvas.height);
      }
      
      // Restore the canvas state
      this.ctx.restore();
      
      return badgeCanvas;
    } catch (error) {
      console.error(`Error rendering ${badgeSettings.badge_type} badge:`, error);
      
      // Make sure to restore the canvas state even if there's an error
      this.ctx.restore();
      
      return null;
    }
  }

  /**
   * Creates a canvas with the badge rendered on it
   * @param badgeSettings - The badge settings to use
   * @returns Canvas element with the rendered badge
   */
  private async createBadgeCanvas(
    badgeSettings: UnifiedBadgeSettings
  ): Promise<HTMLCanvasElement> {
    // Create a temporary canvas for the badge
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    
    // Start with a reasonable size, we'll resize later if needed
    // For image badges (audio, resolution), the size will be adjusted based on the actual image dimensions
    const initialSize = badgeSettings.badge_size * 2;
    canvas.width = initialSize;
    canvas.height = initialSize;
    
    // For review badges, the size is determined by the badge_size setting
    // For audio and resolution badges, the size will be determined by the image dimensions
    if (badgeSettings.badge_type === 'review') {
      // Apply background for review badges
      this.drawBackground(ctx, badgeSettings, initialSize, initialSize);
    }
    
    // Draw badge content based on type
    switch (badgeSettings.badge_type) {
      case 'audio':
        await this.drawAudioBadge(ctx, badgeSettings as AudioBadgeSettings, initialSize, initialSize);
        break;
      case 'resolution':
        await this.drawResolutionBadge(ctx, badgeSettings as ResolutionBadgeSettings, initialSize, initialSize);
        break;
      case 'review':
        await this.drawReviewBadge(ctx, badgeSettings as ReviewBadgeSettings, initialSize, initialSize);
        break;
    }
    
    // For review badges, trim the canvas to remove excess space
    // For audio and resolution badges, the canvas is already properly sized by drawImageBadge
    if (badgeSettings.badge_type === 'review') {
      return this.trimCanvas(canvas);
    }
    
    return canvas;
  }

  /**
   * Draw the background, border, and shadow for a badge
   */
  private drawBackground(
    ctx: CanvasRenderingContext2D,
    settings: UnifiedBadgeSettings,
    width: number,
    height: number,
    contentWidth?: number,
    contentHeight?: number
  ): void {
    ctx.save();
    
    // Clear the canvas
    ctx.clearRect(0, 0, width, height);
    
    // Use the content dimensions if provided, otherwise use the settings badge size
    const badgeWidth = contentWidth ? width : settings.badge_size;
    const badgeHeight = contentHeight ? height : settings.badge_size;
    
    // Position at 0,0 for content-sized badges, otherwise center
    const x = contentWidth ? 0 : (width - badgeWidth) / 2;
    const y = contentHeight ? 0 : (height - badgeHeight) / 2;
    
    // Shadow
    if (settings.shadow_enabled) {
      ctx.shadowColor = settings.shadow_color;
      ctx.shadowBlur = settings.shadow_blur;
      ctx.shadowOffsetX = settings.shadow_offset_x;
      ctx.shadowOffsetY = settings.shadow_offset_y;
    }
    
    // Draw the background with rounded corners
    ctx.beginPath();
    const radius = settings.border_radius;
    
    // Draw rounded rectangle
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + badgeWidth - radius, y);
    ctx.quadraticCurveTo(x + badgeWidth, y, x + badgeWidth, y + radius);
    ctx.lineTo(x + badgeWidth, y + badgeHeight - radius);
    ctx.quadraticCurveTo(x + badgeWidth, y + badgeHeight, x + badgeWidth - radius, y + badgeHeight);
    ctx.lineTo(x + radius, y + badgeHeight);
    ctx.quadraticCurveTo(x, y + badgeHeight, x, y + badgeHeight - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    
    // Background fill with opacity
    const bgColor = settings.background_color;
    const bgOpacity = settings.background_opacity / 100;
    ctx.fillStyle = this.hexToRgba(bgColor, bgOpacity);
    ctx.fill();
    
    // Border
    if (settings.border_size > 0) {
      ctx.lineWidth = settings.border_size;
      const borderColor = settings.border_color;
      const borderOpacity = settings.border_opacity / 100;
      ctx.strokeStyle = this.hexToRgba(borderColor, borderOpacity);
      ctx.stroke();
    }
    
    ctx.restore();
  }

  /**
   * Draw an audio badge on the provided context
   */
  private async drawAudioBadge(
    ctx: CanvasRenderingContext2D,
    settings: AudioBadgeSettings,
    width: number,
    height: number
  ): Promise<void> {
    const { properties } = settings;
    const codecType = properties.codec_type || 'dolby_atmos';
    
    // Get the codec icon URL
    const iconUrl = await getAudioCodecIcon(codecType);
    
    if (!iconUrl) {
      console.error(`No icon found for codec type: ${codecType}`);
      return;
    }
    
    await this.drawImageBadge(ctx, iconUrl, settings, width, height);
  }

  /**
   * Draw a resolution badge on the provided context
   */
  private async drawResolutionBadge(
    ctx: CanvasRenderingContext2D,
    settings: ResolutionBadgeSettings,
    width: number,
    height: number
  ): Promise<void> {
    const { properties } = settings;
    const resolutionType = properties.resolution_type || '4k';
    
    // Get the resolution image URL
    const iconUrl = await getSourceImageUrlForResolution(resolutionType);
    
    if (!iconUrl) {
      console.error(`No icon found for resolution type: ${resolutionType}`);
      return;
    }
    
    await this.drawImageBadge(ctx, iconUrl, settings, width, height);
  }

  /**
   * Draw a review badge on the provided context
   */
  private async drawReviewBadge(
    ctx: CanvasRenderingContext2D,
    settings: ReviewBadgeSettings,
    width: number,
    height: number
  ): Promise<void> {
    const { properties, display_format } = settings;
    const reviewSources = properties.review_sources || ['imdb'];
    
    // Calculate badge dimensions based on size
    const badgeSize = settings.badge_size;
    const x = (width - badgeSize) / 2;
    const y = (height - badgeSize) / 2;
    
    // Save context state
    ctx.save();
    
    // Font settings
    const fontSize = Math.max(badgeSize * 0.3, 12);
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#FFFFFF';
    
    // Calculate positions based on display format
    if (display_format === 'horizontal') {
      // Horizontal layout
      const scoreY = y + badgeSize / 2;
      let scoreX = x + badgeSize / 2;
      
      // Divide space evenly for multiple sources
      const sourceWidth = badgeSize / reviewSources.length;
      
      reviewSources.forEach((source, index) => {
        // Position for this source
        const sourceX = x + (index * sourceWidth) + (sourceWidth / 2);
        
        // Draw the source logo or name
        ctx.fillText(source.toUpperCase(), sourceX, scoreY - fontSize * 0.6);
        
        // Draw the score (dummy value for preview)
        ctx.fillText('8.7', sourceX, scoreY + fontSize * 0.6);
      });
    } else {
      // Vertical layout - stack the scores
      const sourceHeight = badgeSize / reviewSources.length;
      
      reviewSources.forEach((source, index) => {
        // Position for this source
        const sourceY = y + (index * sourceHeight) + (sourceHeight / 2);
        
        // Draw the source logo or name
        ctx.fillText(source.toUpperCase(), x + badgeSize / 2 - fontSize, sourceY);
        
        // Draw the score (dummy value for preview)
        ctx.fillText('8.7', x + badgeSize / 2 + fontSize, sourceY);
      });
    }
    
    // Restore context state
    ctx.restore();
  }

  /**
   * Draw an image-based badge (used by audio and resolution badges)
   */
  private async drawImageBadge(
    ctx: CanvasRenderingContext2D,
    imageUrl: string,
    settings: UnifiedBadgeSettings,
    width: number,
    height: number
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      
      img.onload = () => {
        // Get the defined padding from settings or use a default
        const padding = 10; // Fixed padding around the image
        
        // Use the actual image dimensions plus padding
        // Use the badge_size as a scaling factor for the image
        const scale = settings.badge_size / 100; // 100 is the default size
        
        console.log(`Badge rendering: Badge type ${settings.badge_type}, badge_size=${settings.badge_size}, scale=${scale}`);
        
        // Calculate scaled dimensions while preserving aspect ratio
        const drawWidth = img.width * scale;
        const drawHeight = img.height * scale;
        
        // Update the canvas size to match the image size plus padding
        // This effectively resizes the badge to fit the image
        if (ctx.canvas) {
          ctx.canvas.width = drawWidth + (padding * 2);
          ctx.canvas.height = drawHeight + (padding * 2);
        }
        
        // Clear the canvas with the new dimensions
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        
        // Redraw the background with the new dimensions
        this.drawBackground(ctx, settings, ctx.canvas.width, ctx.canvas.height, drawWidth, drawHeight);
        
        // Calculate position (centered in badge)
        const x = padding;
        const y = padding;
        
        // Draw the image
        ctx.drawImage(img, x, y, drawWidth, drawHeight);
        resolve();
      };
      
      img.onerror = () => {
        console.error(`Failed to load image: ${imageUrl}`);
        reject(new Error(`Failed to load image: ${imageUrl}`));
      };
      
      img.src = imageUrl;
    });
  }

  /**
   * Trim a canvas to remove empty space around the content
   */
  private trimCanvas(canvas: HTMLCanvasElement): HTMLCanvasElement {
    const ctx = canvas.getContext('2d')!;
    const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = pixels.data;
    
    let left = canvas.width;
    let top = canvas.height;
    let right = 0;
    let bottom = 0;
    
    // Find the bounds of non-transparent pixels
    for (let y = 0; y < canvas.height; y++) {
      for (let x = 0; x < canvas.width; x++) {
        const alpha = data[((y * canvas.width + x) * 4) + 3];
        if (alpha > 0) {
          if (x < left) left = x;
          if (x > right) right = x;
          if (y < top) top = y;
          if (y > bottom) bottom = y;
        }
      }
    }
    
    // Add a small padding
    const padding = 10;
    left = Math.max(0, left - padding);
    top = Math.max(0, top - padding);
    right = Math.min(canvas.width, right + padding);
    bottom = Math.min(canvas.height, bottom + padding);
    
    // Get the width and height of the content
    const trimWidth = right - left + 1;
    const trimHeight = bottom - top + 1;
    
    // If there's no content found, return the original canvas
    if (trimWidth <= padding * 2 || trimHeight <= padding * 2) {
      return canvas;
    }
    
    // Create a new canvas with the trimmed dimensions
    const trimmedCanvas = document.createElement('canvas');
    trimmedCanvas.width = trimWidth;
    trimmedCanvas.height = trimHeight;
    
    // Draw the trimmed content onto the new canvas
    const trimmedCtx = trimmedCanvas.getContext('2d')!;
    trimmedCtx.drawImage(
      canvas,
      left, top, trimWidth, trimHeight,
      0, 0, trimWidth, trimHeight
    );
    
    return trimmedCanvas;
  }

  /**
   * Calculate the position of a badge on the main canvas
   */
  private calculateBadgePosition(
    position: BadgePosition,
    badgeWidth: number,
    badgeHeight: number,
    padding: number
  ): { x: number, y: number } {
    const positionStyles = getBadgePositionStyles(position, padding);
    
    let x = 0, y = 0;
    
    // Calculate X position
    if (positionStyles.left === '50%') {
      // Center horizontally
      x = (this.width - badgeWidth) / 2;
    } else if (positionStyles.left !== undefined) {
      // Left positioning
      x = parseInt(positionStyles.left, 10);
    } else if (positionStyles.right !== undefined) {
      // Right positioning
      x = this.width - badgeWidth - parseInt(positionStyles.right, 10);
    }
    
    // Calculate Y position
    if (positionStyles.top === '50%') {
      // Center vertically
      y = (this.height - badgeHeight) / 2;
    } else if (positionStyles.top !== undefined) {
      // Top positioning
      y = parseInt(positionStyles.top, 10);
    } else if (positionStyles.bottom !== undefined) {
      // Bottom positioning
      y = this.height - badgeHeight - parseInt(positionStyles.bottom, 10);
    }
    
    // Apply an additional padding offset to ensure badges don't touch the edge of the poster
    const edgePadding = 5; // Small additional padding from poster edge
    
    // Ensure badges stay within the canvas boundaries with a minimum edge padding
    x = Math.max(edgePadding, Math.min(this.width - badgeWidth - edgePadding, x));
    y = Math.max(edgePadding, Math.min(this.height - badgeHeight - edgePadding, y));
    
    return { x, y };
  }

  /**
   * Highlight the currently active badge
   */
  private highlightActiveBadge(
    x: number,
    y: number,
    width: number,
    height: number
  ): void {
    this.ctx.save();
    
    // Draw a highlight border
    this.ctx.strokeStyle = '#4f46e5'; // Indigo color
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(x - 2, y - 2, width + 4, height + 4);
    
    // Draw center point marker
    this.ctx.fillStyle = '#ff0000';
    this.ctx.beginPath();
    this.ctx.arc(x + width / 2, y + height / 2, 3, 0, Math.PI * 2);
    this.ctx.fill();
    
    this.ctx.restore();
  }

  /**
   * Convert a hex color to rgba
   */
  private hexToRgba(hex: string, alpha: number): string {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    const fullHex = hex.replace(shorthandRegex, (m, r, g, b) => {
      return r + r + g + g + b + b;
    });
    
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(fullHex);
    if (!result) {
      return `rgba(0, 0, 0, ${alpha})`;
    }
    
    const r = parseInt(result[1], 16);
    const g = parseInt(result[2], 16);
    const b = parseInt(result[3], 16);
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  /**
   * Extract a badge as a PNG with transparency
   */
  public static async extractBadgeWithTransparency(
    canvas: HTMLCanvasElement
  ): Promise<string> {
    return canvas.toDataURL('image/png');
  }

  /**
   * Render a single badge and return it as a data URL
   * This is a public method used for downloading individual badges
   * @param badgeSettings - The badge settings to use
   * @returns Data URL of the rendered badge with transparency
   */
  async renderSingleBadge(badgeSettings: UnifiedBadgeSettings): Promise<string> {
    try {
      console.log(`Rendering single badge for download: ${badgeSettings.badge_type}`);
      
      // Clear the canvas for this new badge
      this.ctx.clearRect(0, 0, this.width, this.height);
      
      // Create the badge canvas
      const badgeCanvas = await this.createBadgeCanvas(badgeSettings);
      
      if (!badgeCanvas) {
        throw new Error(`Failed to create canvas for ${badgeSettings.badge_type} badge`);
      }
      
      // Return the badge as a data URL
      return BadgeRenderer.extractBadgeWithTransparency(badgeCanvas);
    } catch (error) {
      console.error(`Error rendering single badge: ${error}`);
      throw error;
    }
  }
}
