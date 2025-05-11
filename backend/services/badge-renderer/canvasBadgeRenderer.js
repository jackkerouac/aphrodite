import { createCanvas, loadImage, registerFont } from 'canvas';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';
import { RATING_LOGO_MAP, RATING_BG_COLOR_MAP } from './utils/logoMapping.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get the project root directory (go up from backend/services/badge-renderer to root)
const projectRoot = path.resolve(__dirname, '../../..');

class CanvasBadgeRenderer {
  constructor() {
    this.loaded = false;
    this.fonts = new Map();
  }

  async init() {
    if (this.loaded) return;
    
    // Load fonts - we'll load some default fonts
    try {
      const fontPath = path.join(projectRoot, 'src', 'assets', 'fonts');
      
      // Try to register some common fonts
      const fontFiles = {
        'Roboto': 'Roboto-Regular.ttf',
        'Roboto Bold': 'Roboto-Bold.ttf',
        'Inter': 'Inter-Regular.ttf',
        'Inter Bold': 'Inter-Bold.ttf'
      };

      for (const [fontName, fileName] of Object.entries(fontFiles)) {
        try {
          const fullPath = path.join(fontPath, fileName);
          const exists = await fs.access(fullPath).then(() => true).catch(() => false);
          
          if (exists) {
            registerFont(fullPath, { family: fontName });
            this.fonts.set(fontName, true);
            console.log(`Registered font: ${fontName}`);
          }
        } catch (err) {
          console.warn(`Failed to register font ${fontName}:`, err);
        }
      }
    } catch (err) {
      console.warn('Font loading failed:', err);
    }
    
    this.loaded = true;
  }

  async renderBadge(type, settings, metadata, sourceImagePath) {
    await this.init();
    
    // Start with a temporary size, will resize based on content
    let canvas = createCanvas(200, 100);
    let ctx = canvas.getContext('2d');

    // Handle different badge types
    switch (type) {
      case 'resolution':
        return await this.renderResolutionBadge(settings, metadata, sourceImagePath);
      case 'audio':
        return await this.renderAudioBadge(settings, metadata, sourceImagePath);
      case 'review':
        return await this.renderReviewBadge(settings, metadata);
      default:
        throw new Error(`Unsupported badge type: ${type}`);
    }
  }

  async renderResolutionBadge(settings, metadata, sourceImagePath) {
    // If we have a source image, render it with styling
    if (sourceImagePath) {
      return await this.renderImageBadge(settings, sourceImagePath);
    }
    
    // Otherwise render text-based badge
    return await this.renderTextBadge(settings, metadata.resolution || 'HD');
  }

  async renderAudioBadge(settings, metadata, sourceImagePath) {
    // If we have a source image, render it with styling
    if (sourceImagePath) {
      return await this.renderImageBadge(settings, sourceImagePath);
    }
    
    // Otherwise render text-based badge
    return await this.renderTextBadge(settings, metadata.audioFormat || 'Audio');
  }

  async renderReviewBadge(settings, metadata) {
    const sources = metadata.rating || [];
    const isHorizontal = settings.displayFormat !== 'vertical';
    const maxSources = settings.maxSourcesToShow || sources.length;
    
    // Sort sources according to sourceOrder from settings
    let sortedSources = sources;
    if (settings.sourceOrder && settings.sourceOrder.length > 0) {
      sortedSources = sources.sort((a, b) => {
        const aIndex = settings.sourceOrder.indexOf(a.name);
        const bIndex = settings.sourceOrder.indexOf(b.name);
        
        // If both are in the order array, sort by their position
        if (aIndex !== -1 && bIndex !== -1) {
          return aIndex - bIndex;
        }
        // If only one is in the order array, it comes first
        if (aIndex !== -1) return -1;
        if (bIndex !== -1) return 1;
        // If neither is in the order array, maintain original order
        return 0;
      });
    }
    
    const sourcesToShow = sortedSources.slice(0, maxSources);
    
    if (sourcesToShow.length === 0) {
      // No review data available - return empty badge
      return await this.renderTextBadge(settings, 'No Rating');
    }
    
    // Convert all ratings to 0-100 scale
    const normalizedSources = sourcesToShow.map(source => {
      let normalizedRating = source.rating;
      
      // Convert based on the outOf value
      if (source.outOf && source.outOf !== 100) {
        normalizedRating = Math.round((source.rating / source.outOf) * 100);
      }
      
      return {
        ...source,
        rating: normalizedRating,
        outOf: 100
      };
    });
    
    // Use the size from settings, or a reasonable default
    const baseSize = settings.size || 80;
    
    // Use padding from settings instead of hardcoded value
    const padding = settings.padding || 8;
    const logoHeight = baseSize * 0.4; // Reduced from 0.5 to 0.4 for better spacing
    const textHeight = baseSize * 0.25; // 25% of badge size for text
    const verticalSpacing = baseSize * 0.08; // Reduced from 0.1 to 0.08 for tighter spacing
    
    // Pre-load logo images for sizing calculations
    const logoPromises = normalizedSources.map(async (source) => {
      try {
        const logoPath = RATING_LOGO_MAP[source.name.toUpperCase()] || 
                         RATING_LOGO_MAP[source.name] || 
                         null;
        if (!logoPath) {
          console.warn(`No logo found for rating source: ${source.name}`);
          return null;
        }
        
        const fullPath = path.join(projectRoot, 'src', 'assets', logoPath);
        console.log(`Loading logo for ${source.name} from: ${fullPath}`);
        return await loadImage(fullPath);
      } catch (error) {
        console.error(`Failed to load logo for ${source.name}:`, error);
        return null;
      }
    });
    
    let logos = [];
    try {
      logos = await Promise.all(logoPromises);
      console.log(`Loaded ${logos.filter(Boolean).length} logos out of ${logoPromises.length} requested`);
    } catch (error) {
      console.error('Error loading logos:', error);
    }
    
    // Calculate dimensions based on loaded logos
    let badgeWidths = [];
    
    // Calculate each badge width based on its logo's aspect ratio
    logos.forEach((logo, index) => {
      if (logo) {
        // Use logo's aspect ratio to determine width while keeping height fixed
        const aspect = logo.width / logo.height;
        const badgeWidth = Math.max(logoHeight * aspect, baseSize * 0.5) + (padding * 2);
        badgeWidths[index] = badgeWidth;
      } else {
        // Fallback if logo couldn't be loaded
        badgeWidths[index] = baseSize + (padding * 2);
      }
    });
    
    // Calculate total canvas dimensions
    let canvasWidth, canvasHeight;
    if (isHorizontal) {
      // For horizontal layout, sum all badge widths
      canvasWidth = badgeWidths.reduce((sum, width) => sum + width, 0);
      canvasHeight = logoHeight + textHeight + verticalSpacing + (padding * 2);
    } else {
      // For vertical layout, use maximum badge width and stack heights
      canvasWidth = Math.max(...badgeWidths, baseSize);
      canvasHeight = (logoHeight + textHeight + verticalSpacing + (padding * 2)) * sourcesToShow.length;
    }
    
    // Create canvas with calculated dimensions
    const canvas = createCanvas(canvasWidth, canvasHeight);
    const ctx = canvas.getContext('2d');
    
    // Clear the canvas with transparent background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw the main background
    ctx.fillStyle = settings.backgroundColor;
    ctx.globalAlpha = settings.transparency || 1;
    
    if (settings.borderRadius && settings.borderRadius > 0) {
      this.drawRoundedRect(ctx, 0, 0, canvas.width, canvas.height, settings.borderRadius);
      ctx.fill();
    } else {
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    // Apply shadow if enabled
    if (settings.shadowEnabled) {
      ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
      ctx.shadowBlur = settings.shadowBlur || 5;
      ctx.shadowOffsetX = settings.shadowOffsetX || 2;
      ctx.shadowOffsetY = settings.shadowOffsetY || 2;
    }
    
    // Draw badges with logos and text
    if (isHorizontal) {
      // Draw sources horizontally
      let currentX = 0;
      
      sourcesToShow.forEach((source, index) => {
        const normalizedSource = normalizedSources[index];
        const badgeWidth = badgeWidths[index];
        const logo = logos[index];
        
        // Define position for this source
        const horLogoX = currentX + (badgeWidth / 2);
        const horLogoY = padding + (logoHeight / 2);
        
        // Apply source-specific background color if available
        const sourceName = source.name.toUpperCase();
        
        // Skip brand colors since this feature isn't in the database
        
        // Draw logo or text fallback
        if (logo) {
          const logoAspect = logo.width / logo.height;
          const logoDrawWidth = Math.min(logoHeight * logoAspect, badgeWidth - (padding * 2));
          const logoDrawHeight = logoDrawWidth / logoAspect;
          
          ctx.globalAlpha = 1;
          ctx.drawImage(
            logo,
            horLogoX - (logoDrawWidth / 2),
            horLogoY - (logoDrawHeight / 2),
            logoDrawWidth,
            logoDrawHeight
          );
        } else {
          // Text fallback
          ctx.globalAlpha = 1;
          ctx.fillStyle = settings.textColor || '#FFFFFF';
          const fontFamily = this.getFontFamily(settings.fontFamily);
          ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${fontFamily}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(source.name, horLogoX, horLogoY);
        }
        
        // Draw rating text
        const textY = padding + logoHeight + verticalSpacing + (textHeight / 2);
        ctx.fillStyle = settings.textColor || '#FFFFFF';
        const fontFamily = this.getFontFamily(settings.fontFamily);
        ctx.font = `bold ${settings.fontSize || Math.floor(textHeight * 0.8)}px ${fontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const ratingText = `${normalizedSource.rating}%`;
        ctx.fillText(ratingText, horLogoX, textY);
        
        // Add a visual divider between sources (except for the last one)
        if (index < sourcesToShow.length - 1) {
          ctx.strokeStyle = settings.textColor || '#FFFFFF';
          ctx.globalAlpha = 0.5;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(currentX + badgeWidth, padding);
          ctx.lineTo(currentX + badgeWidth, canvasHeight - padding);
          ctx.stroke();
          ctx.globalAlpha = 1;
        }
        
        currentX += badgeWidth;
      });
    } else {
      // Draw sources vertically
      let currentY = 0;
      
      sourcesToShow.forEach((source, index) => {
        const normalizedSource = normalizedSources[index];
        const badgeHeight = logoHeight + textHeight + verticalSpacing + (padding * 2);
        const logo = logos[index];
        
        // Define position for this source
        const vertLogoX = canvasWidth / 2;
        const vertLogoY = currentY + padding + (logoHeight / 2);
        
        // Apply source-specific background color if available
        const sourceName = source.name.toUpperCase();
        
        // Skip brand colors since this feature isn't in the database
        
        // Draw logo or text fallback
        if (logo) {
          const logoAspect = logo.width / logo.height;
          const logoDrawWidth = Math.min(logoHeight * logoAspect, canvasWidth - (padding * 2));
          const logoDrawHeight = logoDrawWidth / logoAspect;
          
          ctx.globalAlpha = 1;
          ctx.drawImage(
            logo,
            vertLogoX - (logoDrawWidth / 2),
            vertLogoY - (logoDrawHeight / 2),
            logoDrawWidth,
            logoDrawHeight
          );
        } else {
          // Text fallback
          ctx.globalAlpha = 1;
          ctx.fillStyle = settings.textColor || '#FFFFFF';
          const fontFamily = this.getFontFamily(settings.fontFamily);
          ctx.font = `bold ${Math.floor(logoHeight * 0.5)}px ${fontFamily}`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(source.name, vertLogoX, vertLogoY);
        }
        
        // Draw rating text
        const textY = currentY + padding + logoHeight + verticalSpacing + (textHeight / 2);
        ctx.fillStyle = settings.textColor || '#FFFFFF';
        const fontFamily = this.getFontFamily(settings.fontFamily);
        const calculatedFontSize = settings.fontSize || Math.floor(textHeight * 0.8);
        ctx.font = `bold ${calculatedFontSize}px ${fontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const ratingText = `${normalizedSource.rating}%`;
        ctx.fillText(ratingText, vertLogoX, textY);
        
        // Add a visual divider between sources (except for the last one)
        if (index < sourcesToShow.length - 1) {
          ctx.strokeStyle = settings.textColor || '#FFFFFF';
          ctx.globalAlpha = 0.5;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(padding, currentY + badgeHeight);
          ctx.lineTo(canvasWidth - padding, currentY + badgeHeight);
          ctx.stroke();
          ctx.globalAlpha = 1;
        }
        
        currentY += badgeHeight;
      });
    }
    
    return canvas.toBuffer('image/png');
  }

  async renderImageBadge(settings, imagePath) {
    try {
      // Load the image
      const img = await loadImage(imagePath);
      
      // Calculate dimensions based on settings - use the actual settings.size
      const targetWidth = settings.size || 100;
      const scaleFactor = targetWidth / img.width;
      
      const imageWidth = Math.round(img.width * scaleFactor);
      const imageHeight = Math.round(img.height * scaleFactor);
      
      // Add padding from settings
      const padding = settings.padding || settings.margin || 10;
      const badgeWidth = imageWidth + (padding * 2);
      const badgeHeight = imageHeight + (padding * 2);
      
      // Create canvas with calculated dimensions
      const canvas = createCanvas(badgeWidth, badgeHeight);
      const ctx = canvas.getContext('2d');
      
      // Apply background
      this.applyBackground(ctx, badgeWidth, badgeHeight, settings);
      
      // Draw the image
      ctx.drawImage(img, padding, padding, imageWidth, imageHeight);
      
      // Apply border if specified
      if (settings.borderWidth > 0) {
        this.applyBorder(ctx, badgeWidth, badgeHeight, settings);
      }
      
      return canvas.toBuffer('image/png');
    } catch (error) {
      console.error('Error rendering image badge:', error);
      // Fall back to text rendering
      return this.renderTextBadge(settings, 'N/A');
    }
  }

  async renderTextBadge(settings, text) {
    const size = settings.size || 100;
    // Create canvas with proportional dimensions based on size
    const width = size * 2;
    const height = size;
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext('2d');

    // Apply background
    this.applyBackground(ctx, canvas.width, canvas.height, settings);

    // Apply border if specified
    if (settings.borderWidth > 0) {
      this.applyBorder(ctx, canvas.width, canvas.height, settings);
    }

    // Draw text
    ctx.fillStyle = settings.textColor || '#FFFFFF';
    const fontSize = settings.fontSize || size / 3;
    
    // Use a font that's available, fallback to system fonts
    const fontFamily = this.getFontFamily(settings.fontFamily);
    ctx.font = `bold ${fontSize}px ${fontFamily}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, width / 2, height / 2);

    return canvas.toBuffer('image/png');
  }

  applyBackground(ctx, width, height, settings) {
    // Apply shadow first if enabled
    if (settings.shadowEnabled) {
      ctx.shadowColor = settings.shadowColor || 'rgba(0, 0, 0, 0.5)';
      ctx.shadowBlur = settings.shadowBlur || 5;
      ctx.shadowOffsetX = settings.shadowOffsetX || 2;
      ctx.shadowOffsetY = settings.shadowOffsetY || 2;
    }
    
    ctx.fillStyle = settings.backgroundColor || '#000000';
    ctx.globalAlpha = settings.transparency || 1;
    
    if (settings.borderRadius > 0) {
      this.drawRoundedRect(ctx, 0, 0, width, height, settings.borderRadius);
      ctx.fill();
    } else {
      ctx.fillRect(0, 0, width, height);
    }
    
    // Reset shadow after background
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    ctx.globalAlpha = 1; // Reset alpha
  }

  applyBorder(ctx, width, height, settings) {
    if (!settings.borderWidth || settings.borderWidth <= 0) return;
    
    ctx.strokeStyle = settings.borderColor || '#FFFFFF';
    ctx.lineWidth = settings.borderWidth;
    ctx.globalAlpha = settings.borderOpacity || 1;
    
    const offset = settings.borderWidth / 2;
    
    if (settings.borderRadius > 0) {
      this.drawRoundedRect(
        ctx, 
        offset, 
        offset, 
        width - settings.borderWidth, 
        height - settings.borderWidth, 
        settings.borderRadius - offset
      );
      ctx.stroke();
    } else {
      ctx.strokeRect(offset, offset, width - settings.borderWidth, height - settings.borderWidth);
    }
    
    ctx.globalAlpha = 1; // Reset alpha
  }

  drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  // Map resolution values to asset paths
  async getResolutionImagePath(resolution) {
    const resolutionMap = {
      '8K': 'resolution/8k.png',
      '4K': 'resolution/4k.png',
      '1440p': 'resolution/1440p.png',
      '1080p': 'resolution/1080p.png',
      '720p': 'resolution/720p.png',
      '480p': 'resolution/480p.png',
      'SD': 'resolution/sd.png'
    };
    
    let filename = resolutionMap[resolution];
    if (!filename) {
      // Check for lowercase versions as fallback
      const lowerResolution = resolution.toLowerCase();
      const resolutionMapLower = {
        '8k': 'resolution/8k.png',
        '4k': 'resolution/4k.png',
        '1440p': 'resolution/1440p.png',
        '1080p': 'resolution/1080p.png',
        '720p': 'resolution/720p.png',
        '480p': 'resolution/480p.png',
        'sd': 'resolution/sd.png'
      };
      filename = resolutionMapLower[lowerResolution];
    }
    
    if (!filename) return null;
    
    // Check if the file exists before returning the path
    const filePath = path.join(projectRoot, 'src', 'assets', filename);
    try {
      await fs.access(filePath);
      return filePath;
    } catch {
      console.warn(`Resolution image not found: ${filePath}`);
    }
    return null;
  }

  // Map audio formats to asset paths
  async getAudioImagePath(audioFormat) {
    if (!audioFormat) return null;
    
    // Normalize the audio format string
    const normalized = audioFormat.toLowerCase()
      .replace(/[\s\:\/\\\-]+/g, '_')
      .replace('dolby_digital_plus', 'plus')
      .replace('dolby_digital_5_1', 'plus')
      .replace('dolby_digital_51', 'plus')
      .replace('dolby_digital', 'digital')
      .replace('dolby_plus', 'plus')
      .replace('dolby_truehd', 'truehd')
      .replace('dts_hd', 'dtses')
      .replace('dts_x', 'dtsx');
    
    // Try multiple variations and handle edge cases
    const variations = [
      normalized,
      normalized.replace(/_/g, ''),
      normalized.replace(/_/g, '-')
    ];
    
    // Add specific mappings for common formats
    if (normalized.includes('dolby') || normalized.includes('digital')) {
      variations.push('digital');
    }
    if (normalized.includes('plus')) {
      variations.push('plus');
    }
    if (normalized.includes('dts')) {
      variations.push('dts', 'dtses', 'dtsx');
    }
    if (normalized.includes('truehd')) {
      variations.push('truehd', 'truehd_atmos');
    }
    if (normalized.includes('atmos')) {
      variations.push('atmos', 'dolby_atmos', 'plus_atmos', 'truehd_atmos');
    }
    
    const formats = [...new Set(variations)]; // Remove duplicates
    
    // Try both standard and compact directories
    for (const format of formats) {
      const attempts = [
        path.join(projectRoot, 'src', 'assets', 'audio_codec', 'standard', `${format}.png`),
        path.join(projectRoot, 'src', 'assets', 'audio_codec', 'compact', `${format}.png`)
      ];
      
      for (const filePath of attempts) {
        try {
          await fs.access(filePath);
          console.log(`Found audio image at: ${filePath}`);
          return filePath;
        } catch {
          continue;
        }
      }
    }
    
    console.warn(`Audio format image not found for: ${audioFormat} (normalized: ${normalized}, tried variations: ${formats.join(', ')})`);
    return null;
  }

  getFontFamily(requestedFont) {
    // Check if the requested font is registered
    if (requestedFont && this.fonts.has(requestedFont)) {
      return requestedFont;
    }
    
    // Fallback to available fonts
    const fallbacks = ['Roboto', 'Inter', 'DejaVu Sans', 'Arial', 'sans-serif'];
    for (const font of fallbacks) {
      if (this.fonts.has(font)) {
        return font;
      }
    }
    
    // Final fallback to generic sans-serif
    return 'Arial, sans-serif';
  }
}

export default CanvasBadgeRenderer;
