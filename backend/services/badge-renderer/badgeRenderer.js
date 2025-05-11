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

  createBadgeSvg(settings, value, posterWidth = 300, posterHeight = 450) {
    const { type, padding = 8 } = settings;
    
    // Use database settings for styling
    const backgroundColor = settings.backgroundColor || '#000000';
    const textColor = settings.textColor || '#FFFFFF';
    const borderColor = settings.borderColor || textColor;
    const borderRadius = settings.borderRadius || 6;
    const borderWidth = settings.borderWidth || 2;
    const borderOpacity = settings.borderOpacity || 1;
    const transparency = settings.transparency || 0.8;
    const fontSize = settings.fontSize || 14;
    const fontFamily = settings.fontFamily || 'Arial, sans-serif';
    
    const icon = this.getBadgeIcon(type);
    const text = `${icon} ${value}`;
    
    // Estimate text width (approximate)
    const textWidth = text.length * (fontSize * 0.6);
    let badgeWidth = textWidth + (padding * 2);
    let badgeHeight = fontSize + (padding * 2);
    
    // Ensure badge doesn't exceed poster dimensions
    // Max badge width should be 1/3 of poster width
    const maxBadgeWidth = posterWidth ? posterWidth / 3 : 200;
    // Max badge height should be 1/10 of poster height
    const maxBadgeHeight = posterHeight ? posterHeight / 10 : 40;
    
    badgeWidth = Math.min(badgeWidth, maxBadgeWidth);
    badgeHeight = Math.min(badgeHeight, maxBadgeHeight);

    // Create SVG with shadow support
    let shadowFilter = '';
    let filterDef = '';
    if (settings.shadowEnabled) {
      shadowFilter = 'filter="url(#shadow)"';
      filterDef = `
        <defs>
          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="${settings.shadowOffsetX || 0}" dy="${settings.shadowOffsetY || 0}" 
                         stdDeviation="${settings.shadowBlur || 5}" 
                         flood-color="${settings.shadowColor || '#000000'}" 
                         flood-opacity="0.5"/>
          </filter>
        </defs>`;
    }

    // Create SVG
    return `
      <svg width="${badgeWidth}" height="${badgeHeight}" viewBox="0 0 ${badgeWidth} ${badgeHeight}" xmlns="http://www.w3.org/2000/svg">
        ${filterDef}
        <rect 
          x="${borderWidth/2}" y="${borderWidth/2}" 
          width="${badgeWidth - borderWidth}" height="${badgeHeight - borderWidth}" 
          rx="${borderRadius}" ry="${borderRadius}"
          fill="${backgroundColor}"
          fill-opacity="${transparency}"
          stroke="${borderColor}"
          stroke-width="${borderWidth}"
          stroke-opacity="${borderOpacity}"
          ${shadowFilter}
        />
        <text 
          x="${badgeWidth / 2}" 
          y="${badgeHeight / 2}" 
          font-size="${fontSize}" 
          font-family="${fontFamily}"
          fill="${textColor}"
          text-anchor="middle"
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

  calculateSafePosition(position, posterWidth, posterHeight, badgeWidth, badgeHeight, padding) {
    let left = 0;
    let top = 0;
    
    switch (position) {
      case 'top-left':
        left = padding;
        top = padding;
        break;
      case 'top-right':
        left = posterWidth - badgeWidth - padding;
        top = padding;
        break;
      case 'bottom-left':
        left = padding;
        top = posterHeight - badgeHeight - padding;
        break;
      case 'bottom-right':
        left = posterWidth - badgeWidth - padding;
        top = posterHeight - badgeHeight - padding;
        break;
      default:
        // Default to bottom-right
        left = posterWidth - badgeWidth - padding;
        top = posterHeight - badgeHeight - padding;
    }
    
    // Ensure position is within bounds
    left = Math.max(0, Math.min(left, posterWidth - badgeWidth));
    top = Math.max(0, Math.min(top, posterHeight - badgeHeight));
    
    return { left, top };
  }

  async applyMultipleBadges(posterPath, badgeConfigs) {
    try {
      console.log('Applying multiple badges. Badge configs received:', badgeConfigs);
      
      let posterBuffer = await fs.readFile(posterPath);
      
      // Ensure the poster is in a format we can work with
      posterBuffer = await sharp(posterBuffer)
        .png()
        .toBuffer();
      
      // Sort badges by stacking order
      const enabledBadges = badgeConfigs.filter(config => {
        const hasValue = config.enabled && config.value !== null && config.value !== undefined;
        console.log(`Badge ${config.settings.type}: enabled=${config.enabled}, value=${config.value}, filtered=${hasValue}`);
        return hasValue;
      });
      
      const sortedBadges = enabledBadges
        .sort((a, b) => (a.settings.stackingOrder || 0) - (b.settings.stackingOrder || 0));
      
      console.log(`Filtered and sorted badges (${sortedBadges.length} out of ${badgeConfigs.length}):`, sortedBadges);

      // Apply each badge sequentially
      console.log(`Processing ${sortedBadges.length} badges...`);
      for (let i = 0; i < sortedBadges.length; i++) {
        const config = sortedBadges[i];
        console.log(`Applying badge ${i + 1}/${sortedBadges.length}: ${config.settings.type} at position ${config.settings.position}`);
        
        const poster = sharp(posterBuffer);
        const metadata = await poster.metadata();
        
        console.log('Poster metadata:', metadata);
        console.log('Badge config:', config);
        const badgeSvg = this.createBadgeSvg(config.settings, config.value, metadata.width, metadata.height);
        
        // Create a Sharp instance from the badge SVG
        const badgeBuffer = Buffer.from(badgeSvg);
        const badge = sharp(badgeBuffer);
        const badgeMetadata = await badge.metadata();
        
        // Ensure badge fits within poster
        if (badgeMetadata.width > metadata.width || badgeMetadata.height > metadata.height) {
          console.warn(`Badge too large (${badgeMetadata.width}x${badgeMetadata.height}) for poster (${metadata.width}x${metadata.height}). Skipping.`);
          continue;
        }
        
        // Calculate position with offset to ensure badge stays within bounds
        const position = this.calculateSafePosition(
          config.settings.position, 
          metadata.width, 
          metadata.height, 
          badgeMetadata.width, 
          badgeMetadata.height,
          config.settings.padding || 8
        );
        
        console.log(`Badge position calculated: ${JSON.stringify(position)}`);
        
        posterBuffer = await poster
          .composite([{
            input: badgeBuffer,
            ...position
          }])
          .png()
          .toBuffer();
          
        console.log(`Badge ${config.settings.type} applied successfully`);
      }

      return posterBuffer;
    } catch (error) {
      console.error('Error applying multiple badges:', error);
      throw new Error(`Failed to apply badges: ${error.message}`);
    }
  }
}

export default BadgeRenderer;
