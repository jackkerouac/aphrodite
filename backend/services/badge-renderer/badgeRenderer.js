import { createCanvas, loadImage } from 'canvas';
import path from 'path';
import fs from 'fs/promises';

class BadgeRenderer {
  constructor() {
    this.fonts = new Map();
    this.badgeStyles = {
      audio: {
        light: { bg: '#DBEAFE', text: '#1E40AF', border: '#93C5FD' },
        dark: { bg: '#1E3A8A', text: '#DBEAFE', border: '#1D4ED8' }
      },
      resolution: {
        light: { bg: '#DCFCE7', text: '#166534', border: '#86EFAC' },
        dark: { bg: '#14532D', text: '#DCFCE7', border: '#15803D' }
      },
      review: {
        light: { bg: '#FEF3C7', text: '#78350F', border: '#FDE68A' },
        dark: { bg: '#78350F', text: '#FEF3C7', border: '#92400E' }
      }
    };
  }

  async init() {
    // Initialize fonts if needed
    // For now, we'll use the default system fonts
  }

  async applyBadge(posterPath, settings, badgeValue) {
    try {
      // Load the poster image
      const posterImage = await loadImage(posterPath);
      const canvas = createCanvas(posterImage.width, posterImage.height);
      const ctx = canvas.getContext('2d');

      // Draw the original poster
      ctx.drawImage(posterImage, 0, 0);

      // Apply the badge based on type and settings
      await this.drawBadge(ctx, settings, badgeValue, canvas.width, canvas.height);

      // Return the modified image as a buffer
      return canvas.toBuffer('image/png');
    } catch (error) {
      console.error('Error applying badge:', error);
      throw new Error(`Failed to apply badge: ${error.message}`);
    }
  }

  async drawBadge(ctx, settings, value, canvasWidth, canvasHeight) {
    const { type, position, theme = 'dark', padding = 8 } = settings;
    
    // Get style for this badge type and theme
    const style = this.badgeStyles[type][theme];
    
    // Set up text properties
    const fontSize = settings.fontSize || 14;
    ctx.font = `${fontSize}px Arial`;
    ctx.textBaseline = 'middle';
    
    // Measure text
    const text = `${this.getBadgeIcon(type)} ${value}`;
    const textMetrics = ctx.measureText(text);
    const textWidth = textMetrics.width;
    const textHeight = fontSize;
    
    // Calculate badge dimensions
    const badgeWidth = textWidth + (padding * 2);
    const badgeHeight = textHeight + (padding * 2);
    const borderRadius = 6;
    
    // Calculate position
    const { x, y } = this.calculatePosition(
      position, 
      badgeWidth, 
      badgeHeight, 
      canvasWidth, 
      canvasHeight
    );
    
    // Draw badge background with rounded corners
    ctx.fillStyle = style.bg;
    ctx.strokeStyle = style.border;
    ctx.lineWidth = 2;
    this.drawRoundedRect(ctx, x, y, badgeWidth, badgeHeight, borderRadius);
    ctx.fill();
    ctx.stroke();
    
    // Draw text
    ctx.fillStyle = style.text;
    ctx.fillText(text, x + padding, y + padding + (textHeight / 2));
  }

  getBadgeIcon(type) {
    const icons = {
      audio: '🔊',
      resolution: '📽️',
      review: '⭐'
    };
    return icons[type] || '';
  }

  calculatePosition(position, badgeWidth, badgeHeight, canvasWidth, canvasHeight) {
    const margin = 16; // Distance from edge
    
    switch (position) {
      case 'top-left':
        return { x: margin, y: margin };
      case 'top-right':
        return { x: canvasWidth - badgeWidth - margin, y: margin };
      case 'bottom-left':
        return { x: margin, y: canvasHeight - badgeHeight - margin };
      case 'bottom-right':
        return { x: canvasWidth - badgeWidth - margin, y: canvasHeight - badgeHeight - margin };
      default:
        return { x: margin, y: margin };
    }
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

  async applyMultipleBadges(posterPath, badgeConfigs) {
    try {
      // Load the poster image
      const posterImage = await loadImage(posterPath);
      const canvas = createCanvas(posterImage.width, posterImage.height);
      const ctx = canvas.getContext('2d');

      // Draw the original poster
      ctx.drawImage(posterImage, 0, 0);

      // Apply each badge
      for (const config of badgeConfigs) {
        if (config.enabled && config.value) {
          await this.drawBadge(ctx, config.settings, config.value, canvas.width, canvas.height);
        }
      }

      // Return the modified image as a buffer
      return canvas.toBuffer('image/png');
    } catch (error) {
      console.error('Error applying multiple badges:', error);
      throw new Error(`Failed to apply badges: ${error.message}`);
    }
  }
}

export default BadgeRenderer;
