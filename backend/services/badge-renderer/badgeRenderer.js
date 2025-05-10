import sharp from 'sharp';
import path from 'path';
import fs from 'fs/promises';

class BadgeRenderer {
  constructor() {
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
    // Initialize if needed
  }

  async applyBadge(posterPath, settings, badgeValue) {
    try {
      // Load the poster image using sharp
      const posterBuffer = await fs.readFile(posterPath);
      const poster = sharp(posterBuffer);
      const metadata = await poster.metadata();

      // Create badge SVG
      const badgeSvg = this.createBadgeSvg(settings, badgeValue, metadata.width, metadata.height);

      // Composite the badge onto the poster
      const modifiedPoster = await poster
        .composite([{
          input: Buffer.from(badgeSvg),
          gravity: this.getGravity(settings.position)
        }])
        .png()
        .toBuffer();

      return modifiedPoster;
    } catch (error) {
      console.error('Error applying badge:', error);
      throw new Error(`Failed to apply badge: ${error.message}`);
    }
  }

  createBadgeSvg(settings, value, posterWidth, posterHeight) {
    const { type, position, theme = 'dark', padding = 8 } = settings;
    const style = this.badgeStyles[type][theme];
    const fontSize = settings.fontSize || 14;
    const icon = this.getBadgeIcon(type);
    const text = `${icon} ${value}`;
    
    // Estimate text width (approximate)
    const textWidth = text.length * (fontSize * 0.6);
    const badgeWidth = textWidth + (padding * 2);
    const badgeHeight = fontSize + (padding * 2);
    const borderRadius = 6;

    // Create SVG
    return `
      <svg width="${badgeWidth}" height="${badgeHeight}" xmlns="http://www.w3.org/2000/svg">
        <rect 
          x="1" y="1" 
          width="${badgeWidth - 2}" height="${badgeHeight - 2}" 
          rx="${borderRadius}" ry="${borderRadius}"
          fill="${style.bg}"
          stroke="${style.border}"
          stroke-width="2"
        />
        <text 
          x="${padding}" 
          y="${badgeHeight / 2}" 
          font-size="${fontSize}" 
          font-family="Arial, sans-serif"
          fill="${style.text}"
          dominant-baseline="middle"
        >${text}</text>
      </svg>
    `;
  }

  getBadgeIcon(type) {
    const icons = {
      audio: '♪',
      resolution: '⬜',
      review: '★'
    };
    return icons[type] || '';
  }

  getGravity(position) {
    switch (position) {
      case 'top-left':
        return 'northwest';
      case 'top-right':
        return 'northeast';
      case 'bottom-left':
        return 'southwest';
      case 'bottom-right':
        return 'southeast';
      default:
        return 'southeast';
    }
  }

  async applyMultipleBadges(posterPath, badgeConfigs) {
    try {
      let posterBuffer = await fs.readFile(posterPath);
      
      // Sort badges by stacking order
      const sortedBadges = badgeConfigs
        .filter(config => config.enabled && config.value)
        .sort((a, b) => (a.settings.stackingOrder || 0) - (b.settings.stackingOrder || 0));

      // Apply each badge sequentially
      for (const config of sortedBadges) {
        const poster = sharp(posterBuffer);
        const metadata = await poster.metadata();
        const badgeSvg = this.createBadgeSvg(config.settings, config.value, metadata.width, metadata.height);
        
        posterBuffer = await poster
          .composite([{
            input: Buffer.from(badgeSvg),
            gravity: this.getGravity(config.settings.position)
          }])
          .png()
          .toBuffer();
      }

      return posterBuffer;
    } catch (error) {
      console.error('Error applying multiple badges:', error);
      throw new Error(`Failed to apply badges: ${error.message}`);
    }
  }
}

export default BadgeRenderer;
