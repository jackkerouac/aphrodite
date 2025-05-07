import { audioCodecImages } from '../constants';

/**
 * Utility functions for generating and downloading poster images with badges
 */

/**
 * Creates a composite image with badges on a poster
 * @param posterImage - The source poster image element
 * @param displaySettings - Which badges to display
 * @param badgeSettings - Settings for each badge type
 * @returns A promise that resolves to a data URL of the composite image
 */
export const generatePosterWithBadges = async (
  posterImage: HTMLImageElement,
  displaySettings: {
    showResolutionBadge: boolean;
    showAudioBadge: boolean;
    showReviewBadge: boolean;
  },
  badgeSettings: {
    resolutionBadgeSettings: any | null;
    audioBadgeSettings: any | null;
    reviewBadgeSettings: any | null;
  }
): Promise<string> => {
  try {
    // Create a canvas element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      throw new Error('Could not create canvas context');
    }
    
    // Set canvas dimensions to match the poster image
    canvas.width = posterImage.naturalWidth;
    canvas.height = posterImage.naturalHeight;
    
    // Draw the poster image on the canvas
    ctx.drawImage(posterImage, 0, 0);
    
    // Function to draw the resolution badge
    const drawResolutionBadge = (settings: any) => {
      if (!settings) return;
      
      // Calculate position
      const position = settings.position || 'top-left';
      const margin = settings.margin || 10;
      const scale = settings.size / 100 || 1;
      
      let x = margin;
      let y = margin;
      
      if (position.includes('right')) {
        x = canvas.width - margin - 100; // Approximate width
      }
      
      if (position.includes('bottom')) {
        y = canvas.height - margin - 30; // Approximate height
      }
      
      // Set font and measure text
      const fontSize = 16 * scale;
      const text = settings.resolution_type || '1080p';
      ctx.font = `bold ${fontSize}px Arial`;
      const textWidth = ctx.measureText(text).width;
      const padding = 10 * scale;
      const badgeWidth = textWidth + (padding * 2);
      const badgeHeight = fontSize + (padding * 2);
      
      // Apply background
      ctx.fillStyle = settings.background_color || '#000000';
      ctx.globalAlpha = settings.background_transparency || 0.8;
      
      // Draw background with rounded corners
      const radius = (settings.border_radius || 4) * scale;
      ctx.beginPath();
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
      ctx.fill();
      
      // Draw border if specified
      if ((settings.border_width || 0) > 0) {
        ctx.strokeStyle = settings.border_color || '#ffffff';
        ctx.lineWidth = (settings.border_width || 1) * scale;
        ctx.globalAlpha = settings.border_transparency || 0.8;
        ctx.stroke();
      }
      
      // Draw shadow if enabled
      if (settings.shadow_toggle) {
        // Save current state
        ctx.save();
        
        // Draw shadow
        ctx.shadowColor = settings.shadow_color || '#000000';
        ctx.shadowBlur = (settings.shadow_blur_radius || 5) * scale;
        ctx.shadowOffsetX = (settings.shadow_offset_x || 2) * scale;
        ctx.shadowOffsetY = (settings.shadow_offset_y || 2) * scale;
        
        // Fill a shape for the shadow
        ctx.fill();
        
        // Restore state
        ctx.restore();
      }
      
      // Draw text
      ctx.fillStyle = settings.text_color || '#ffffff';
      ctx.globalAlpha = 1 - (settings.text_transparency || 0);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, x + (badgeWidth / 2), y + (badgeHeight / 2));
      
      // Reset global alpha
      ctx.globalAlpha = 1;
    };
    
    // Function to draw the audio badge
    const drawAudioBadge = async (settings: any) => {
      if (!settings) return;
      
      // Get audio codec image
      const audioCodecType = settings.audio_codec_type || 'dolby_atmos';
      const imagePath = audioCodecImages[audioCodecType] || audioCodecImages['dolby_atmos'];
      
      // Load the image
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = (err) => reject(new Error(`Failed to load audio codec image: ${err}`));
        img.src = imagePath;
      });
      
      // Calculate position
      const position = settings.position || 'top-right';
      const margin = settings.margin || 10;
      const scale = settings.size / 100 || 1;
      
      let x = margin;
      let y = margin;
      
      if (position.includes('right')) {
        x = canvas.width - margin - (img.width * scale) - (settings.border_width || 0) * 2 - 8; // 8px for padding
      }
      
      if (position.includes('bottom')) {
        y = canvas.height - margin - (img.height * scale) - (settings.border_width || 0) * 2 - 8; // 8px for padding
      }
      
      // Calculate badge dimensions with padding
      const padding = 4;
      const badgeWidth = img.width * scale + padding * 2;
      const badgeHeight = img.height * scale + padding * 2;
      
      // Draw background
      ctx.fillStyle = settings.background_color || '#000000';
      ctx.globalAlpha = settings.background_transparency || 0.8;
      
      // Draw background with rounded corners
      const radius = settings.border_radius || 4;
      ctx.beginPath();
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
      ctx.fill();
      
      // Draw border if specified
      if ((settings.border_width || 0) > 0) {
        ctx.strokeStyle = settings.border_color || '#ffffff';
        ctx.lineWidth = settings.border_width || 1;
        ctx.globalAlpha = settings.border_transparency || 0.8;
        ctx.stroke();
      }
      
      // Draw shadow if enabled
      if (settings.shadow_toggle) {
        ctx.save();
        ctx.shadowColor = settings.shadow_color || '#000000';
        ctx.shadowBlur = settings.shadow_blur_radius || 5;
        ctx.shadowOffsetX = settings.shadow_offset_x || 2;
        ctx.shadowOffsetY = settings.shadow_offset_y || 2;
        ctx.fill();
        ctx.restore();
      }
      
      // Draw image
      ctx.globalAlpha = 1;
      ctx.drawImage(
        img,
        x + padding,
        y + padding,
        img.width * scale,
        img.height * scale
      );
    };
    
    // Function to draw the review badge
    const drawReviewBadge = (settings: any) => {
      if (!settings) return;
      
      // Calculate position
      const position = settings.position || 'bottom-left';
      const margin = settings.margin || 10;
      const scale = settings.size / 100 || 1;
      
      let x = margin;
      let y = margin;
      
      if (position.includes('right')) {
        x = canvas.width - margin - 200; // Approximate width
      }
      
      if (position.includes('bottom')) {
        y = canvas.height - margin - 60; // Approximate height
      }
      
      // Get sources to display
      const sources = (settings.display_sources || ['IMDB', 'TMDB']).slice(0, 2);
      const isVertical = settings.badge_layout === 'vertical';
      const sourcesText = sources.map((source: string) => `${source}: 8.5`);
      
      // Set font and calculate dimensions
      const fontSize = (settings.font_size || 16) * scale;
      const logoSize = (settings.logo_size || 24) * scale;
      const spacing = (settings.spacing || 5) * scale;
      const logoTextSpacing = (settings.logoTextSpacing || 5) * scale;
      
      ctx.font = `${settings.font_weight || 600} ${fontSize}px ${settings.font_family || 'Arial'}`;
      
      // Calculate badge dimensions
      let badgeWidth = 0;
      let badgeHeight = 0;
      const padding = 10 * scale;
      
      if (isVertical) {
        // Measure each source text
        for (const source of sources) {
          const textWidth = ctx.measureText(`${source}: 8.5`).width;
          const sourceWidth = settings.show_logo ? logoSize + logoTextSpacing + textWidth : textWidth;
          badgeWidth = Math.max(badgeWidth, sourceWidth);
        }
        badgeWidth += padding * 2;
        badgeHeight = (settings.show_logo ? Math.max(fontSize, logoSize) : fontSize) * sources.length + 
                      spacing * (sources.length - 1) + padding * 2;
      } else {
        // Calculate total width for horizontal layout
        let totalWidth = 0;
        for (const source of sources) {
          const textWidth = ctx.measureText(`${source}: 8.5`).width;
          totalWidth += settings.show_logo ? logoSize + logoTextSpacing + textWidth : textWidth;
        }
        badgeWidth = totalWidth + spacing * (sources.length - 1) + padding * 2;
        badgeHeight = settings.show_logo ? Math.max(fontSize, logoSize) + padding * 2 : fontSize + padding * 2;
      }
      
      // Apply background
      ctx.fillStyle = settings.background_color || '#000000';
      ctx.globalAlpha = settings.background_transparency || 0.8;
      
      // Draw background with rounded corners
      const radius = (settings.border_radius || 4) * scale;
      ctx.beginPath();
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
      ctx.fill();
      
      // Draw border if specified
      if ((settings.border_width || 0) > 0) {
        ctx.strokeStyle = settings.border_color || '#ffffff';
        ctx.lineWidth = (settings.border_width || 1) * scale;
        ctx.globalAlpha = settings.border_transparency || 0.8;
        ctx.stroke();
      }
      
      // Draw shadow if enabled
      if (settings.shadow_toggle) {
        // Save current state
        ctx.save();
        
        // Draw shadow
        ctx.shadowColor = settings.shadow_color || '#000000';
        ctx.shadowBlur = (settings.shadow_blur_radius || 5) * scale;
        ctx.shadowOffsetX = (settings.shadow_offset_x || 2) * scale;
        ctx.shadowOffsetY = (settings.shadow_offset_y || 2) * scale;
        
        // Fill a shape for the shadow
        ctx.fill();
        
        // Restore state
        ctx.restore();
      }
      
      // Draw sources
      ctx.fillStyle = settings.text_color || '#ffffff';
      ctx.globalAlpha = 1 - (settings.text_transparency || 0);
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      
      let currentX = x + padding;
      let currentY = y + padding + (settings.show_logo ? Math.max(fontSize, logoSize) / 2 : fontSize / 2);
      
      for (let i = 0; i < sources.length; i++) {
        const source = sources[i];
        const text = `${source}: 8.5`;
        
        // Draw logo if enabled
        if (settings.show_logo) {
          // Save context to restore font after logo
          ctx.save();
          ctx.font = `bold ${logoSize}px ${settings.font_family || 'Arial'}`;
          ctx.fillText(source.slice(0, 1), currentX, currentY);
          ctx.restore();
          
          currentX += logoSize + logoTextSpacing;
        }
        
        // Draw text
        ctx.fillText(text, currentX, currentY);
        
        // Move position for next source
        if (isVertical) {
          currentX = x + padding;
          currentY += (settings.show_logo ? Math.max(fontSize, logoSize) : fontSize) + spacing;
        } else {
          const textWidth = ctx.measureText(text).width;
          currentX += textWidth + spacing;
        }
      }
      
      // Reset global alpha
      ctx.globalAlpha = 1;
    };
    
    // Draw Resolution Badge
    if (displaySettings.showResolutionBadge && badgeSettings.resolutionBadgeSettings) {
      drawResolutionBadge(badgeSettings.resolutionBadgeSettings);
    }
    
    // Draw Audio Badge
    if (displaySettings.showAudioBadge && badgeSettings.audioBadgeSettings) {
      await drawAudioBadge(badgeSettings.audioBadgeSettings);
    }
    
    // Draw Review Badge
    if (displaySettings.showReviewBadge && badgeSettings.reviewBadgeSettings) {
      drawReviewBadge(badgeSettings.reviewBadgeSettings);
    }
    
    // Convert canvas to data URL
    const dataUrl = canvas.toDataURL('image/png');
    return dataUrl;
  } catch (error) {
    console.error('Error generating poster with badges:', error);
    throw error;
  }
};

/**
 * Downloads the composite image as a PNG file
 * @param dataUrl - The data URL of the image to download
 * @param filename - The name of the downloaded file
 */
export const downloadPoster = (dataUrl: string, filename: string = 'poster.png'): void => {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};