import { promises as fs } from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import FormData from 'form-data';
import BadgeRenderer from './badgeRenderer.js';
import CanvasBadgeRenderer from './canvasBadgeRenderer.js';
import { pool as db } from '../../db.js';
import MetadataService from './metadataService.js';
import sharp from 'sharp';
import PosterStandardizer from './posterStandardizer.js';

class PosterProcessor {
  constructor() {
    console.log('PosterProcessor initializing with standardization version 1.0');
    this.badgeRenderer = new BadgeRenderer();
    this.canvasBadgeRenderer = new CanvasBadgeRenderer();
    this.metadataService = new MetadataService();
    this.posterStandardizer = new PosterStandardizer();
    this.tempDir = process.env.TEMP_DIR || path.join(process.cwd(), 'temp');
    this.concurrency = parseInt(process.env.BATCH_CONCURRENCY || '4');
    this.useCanvasRenderer = process.env.USE_CANVAS_RENDERER !== 'false'; // Default to true
  }

  async init() {
    // Ensure temp directory exists
    await fs.mkdir(this.tempDir, { recursive: true });
    await this.badgeRenderer.init();
    if (this.useCanvasRenderer) {
      await this.canvasBadgeRenderer.init();
    }
  }

  async processItem(item, jobId, userId) {
    const tempPosterPath = path.join(this.tempDir, `poster-${item.jellyfin_item_id}.png`);
    const standardizedPosterPath = path.join(this.tempDir, `poster-standardized-${item.jellyfin_item_id}.png`);
    
    try {
      // Update item status to processing
      await this.updateItemStatus(item.id, 'processing');
      
      // Log the item to see what data we have
      console.log('Processing item:', item);

      // Fetch badge settings for this user
      const badgeSettings = await this.getBadgeSettings(userId, item);

      // Download poster from Jellyfin
      await this.downloadPoster(item.jellyfin_item_id, tempPosterPath, userId);
      
      // Standardize the poster to 1000px width
      const standardizationResult = await this.posterStandardizer.standardizePoster(
        tempPosterPath,
        standardizedPosterPath
      );
      console.log('Poster standardization result:', standardizationResult);

      // Apply badges using canvas renderer if enabled
      let modifiedPosterBuffer;
      if (this.useCanvasRenderer) {
        modifiedPosterBuffer = await this.applyBadgesWithCanvas(standardizedPosterPath, badgeSettings);
      } else {
        modifiedPosterBuffer = await this.badgeRenderer.applyMultipleBadges(
          standardizedPosterPath,
          badgeSettings
        );
      }
      
      // Save the modified poster for inspection
      const modifiedPosterPath = path.join(this.tempDir, `poster-modified-${item.jellyfin_item_id}.png`);
      await fs.writeFile(modifiedPosterPath, modifiedPosterBuffer);
      console.log(`Modified poster saved at: ${modifiedPosterPath}`);

      // Upload modified poster back to Jellyfin
      await this.uploadPoster(item.jellyfin_item_id, modifiedPosterBuffer, userId);

      // Update item status to completed
      await this.updateItemStatus(item.id, 'completed');

      // Clean up temp files
      // await fs.unlink(tempPosterPath).catch(() => {});
      // await fs.unlink(standardizedPosterPath).catch(() => {});
      console.log(`Temp poster saved at: ${tempPosterPath}`);
      console.log(`Standardized poster saved at: ${standardizedPosterPath}`);

      return { success: true, itemId: item.id };
    } catch (error) {
      console.error(`Error processing item ${item.id}:`, error);
      await this.updateItemStatus(item.id, 'failed', error.message);
      
      // Clean up temp files
      // await fs.unlink(tempPosterPath).catch(() => {});
      // await fs.unlink(standardizedPosterPath).catch(() => {});
      console.log(`Temp poster saved at: ${tempPosterPath} (in error state)`);
      console.log(`Standardized poster saved at: ${standardizedPosterPath} (in error state)`);

      return { success: false, itemId: item.id, error: error.message };
    }
  }

  async getBadgeSettings(userId, item) {
    console.log('Fetching badge settings for user:', userId);
    const query = `
      SELECT 
        'resolution' as type,
        enabled,
        position,
        size,
        font_family,
        font_size,
        text_color,
        background_color,
        background_opacity as transparency,
        border_radius,
        border_width,
        border_color,
        border_opacity,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        margin as padding,
        z_index as stacking_order
      FROM resolution_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'audio' as type,
        enabled,
        position,
        size,
        font_family,
        font_size,
        text_color,
        background_color,
        background_opacity as transparency,
        border_radius,
        border_width,
        border_color,
        border_opacity,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        margin as padding,
        z_index as stacking_order
      FROM audio_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'review' as type,
        enabled,
        position,
        size,
        font_family,
        font_size,
        text_color,
        background_color,
        background_opacity as transparency,
        border_radius,
        border_width,
        border_color,
        border_opacity,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        margin as padding,
        z_index as stacking_order
      FROM review_badge_settings
      WHERE user_id = $1 AND enabled = true
    `;

    const settingsResult = await db.query(query, [userId]);
    const settings = settingsResult.rows;
    console.log('Badge settings from database:', settings);
    
    // Fetch review badge specific settings
    const reviewSettingsQuery = `
      SELECT 
        badge_layout as display_format,
        source_order,
        show_logo,
        size,
        score_format,
        max_sources_to_show
      FROM review_badge_settings
      WHERE user_id = $1 AND enabled = true
    `;
    
    const reviewSettingsResult = await db.query(reviewSettingsQuery, [userId]);
    const reviewSettings = reviewSettingsResult.rows[0];
    console.log('Review badge specific settings:', reviewSettings);

    // Fetch metadata for the item to determine badge values
    const metadata = await this.fetchItemMetadata(item, userId);

    // Map all styling fields from the database
    return settings.map(setting => {
      let extraSettings = {};
      let value = null;
      
      // Add type-specific settings and values
      if (setting.type === 'review') {
        extraSettings = {
          displayFormat: reviewSettings?.display_format || 'vertical',
          sourceOrder: reviewSettings?.source_order || [],
          showLogo: reviewSettings?.show_logo !== false,
          size: parseInt(reviewSettings?.size || '100'),
          scoreFormat: reviewSettings?.score_format || 'rating/outOf',
          maxSourcesToShow: reviewSettings?.max_sources_to_show || 3
        };
        value = metadata.scores || [];
      } else {
        value = this.getBadgeValue(setting.type, metadata);
      }
      
      return {
        enabled: setting.enabled,
        settings: {
          type: setting.type,
          position: setting.position || 'top-right',
          size: setting.size ? parseInt(setting.size) : undefined,
          fontSize: setting.font_size ? parseInt(setting.font_size) : undefined,
          fontFamily: setting.font_family,
          textColor: setting.text_color,
          backgroundColor: setting.background_color,
          borderRadius: setting.border_radius ? parseInt(setting.border_radius) : undefined,
          borderWidth: setting.border_width ? parseInt(setting.border_width) : undefined,
          borderColor: setting.border_color,
          borderOpacity: setting.border_opacity ? parseFloat(setting.border_opacity) : undefined,
          shadowEnabled: setting.shadow_enabled,
          shadowColor: setting.shadow_color,
          shadowBlur: setting.shadow_blur ? parseInt(setting.shadow_blur) : undefined,
          shadowOffsetX: setting.shadow_offset_x ? parseInt(setting.shadow_offset_x) : undefined,
          shadowOffsetY: setting.shadow_offset_y ? parseInt(setting.shadow_offset_y) : undefined,
          padding: setting.padding ? parseInt(setting.padding) : 8,
          margin: setting.padding ? parseInt(setting.padding) : 8,
          transparency: setting.transparency ? parseFloat(setting.transparency) : 1,
          stackingOrder: setting.stacking_order ? parseInt(setting.stacking_order) : 0,
          ...extraSettings
        },
        value
      };
    });
  }

  async fetchItemMetadata(item, userId) {
    // Create an item object that the metadata service expects
    // First fetch basic data from Jellyfin to get the actual media type
    const jellyfinId = item.jellyfin_item_id;
    
    const metadataItem = {
      jellyfin_id: jellyfinId,
      media_type: 'Movie' // This will be overridden by actual type from Jellyfin
    };
    const metadata = await this.metadataService.fetchItemMetadata(metadataItem, userId);
    console.log('Fetched metadata:', metadata);
    return metadata;
  }

  getBadgeValue(type, metadata) {
    let value = null;
    console.log(`Getting badge value for ${type} with metadata:`, metadata);
    
    switch (type) {
      case 'resolution':
        value = metadata.resolution;
        // If no resolution data, try to get it from different fields
        if (!value && metadata.width && metadata.height) {
          // Determine resolution from width/height if available
          const width = metadata.width;
          if (width >= 7680) value = '8K';
          else if (width >= 3840) value = '4K';
          else if (width >= 2560) value = '1440p';
          else if (width >= 1920) value = '1080p';
          else if (width >= 1280) value = '720p';
          else if (width >= 854) value = '480p';
          else value = 'SD';
        }
        break;
      case 'audio':
        value = metadata.audioFormat;
        break;
      case 'review':
        // Review badge value is handled differently - it uses an array of scores
        value = metadata.scores || [];
        break;
      default:
        value = null;
    }
    
    console.log(`Badge value for ${type}: ${JSON.stringify(value)}`);
    return value;
  }

  async downloadPoster(jellyfinId, outputPath, userId) {
    // Get Jellyfin settings from database
    const settingsQuery = `
      SELECT jellyfin_url as url, jellyfin_api_key as token, jellyfin_user_id 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    // Clean up the URL and build the poster URL
    const baseUrl = settings.url.replace(/\/$/, '');
    // Use the Items endpoint with api_key parameter
    const posterUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
    
    console.log('Downloading poster:', {
      url: posterUrl,
      itemId: jellyfinId
    });

    const response = await fetch(posterUrl);

    if (!response.ok) {
      console.error('Failed to download poster:', {
        status: response.status,
        statusText: response.statusText,
        url: posterUrl
      });
      throw new Error(`Failed to download poster: ${response.status} ${response.statusText}`);
    }

    const buffer = await response.buffer();
    await fs.writeFile(outputPath, buffer);
  }

  async uploadPoster(jellyfinId, posterBuffer, userId) {
    // Get Jellyfin settings from database
    const settingsQuery = `
      SELECT jellyfin_url as url, jellyfin_api_key as token, jellyfin_user_id 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    // Clean up the URL and build the upload URL
    const baseUrl = settings.url.replace(/\/$/, '');
    
    // Based on the verify-api-key.js results, the token works as a query parameter
    const uploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
    
    console.log('Uploading poster:', {
      url: uploadUrl,
      contentLength: posterBuffer.length,
      itemId: jellyfinId
    });

    try {
      // First, try to delete existing image (optional)
      const deleteUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
      
      console.log('Attempting to delete existing image...');
      const deleteResponse = await fetch(deleteUrl, {
        method: 'DELETE'
      });
      console.log('Delete response:', deleteResponse.status);
      
      // Now upload the new image - convert to base64 as per Jellyfin 10.10.7 requirements
      console.log('Uploading new poster...');
      const base64Data = posterBuffer.toString('base64');
      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'image/png',
          'Content-Encoding': 'base64'
        },
        body: base64Data
      });

      const responseText = await response.text();
      console.log('Upload response:', {
        status: response.status,
        statusText: response.statusText,
        body: responseText.substring(0, 200)
      });

      if (!response.ok) {
        // Try alternate approach with X-Emby-Token header and base64 encoding
        console.log('First attempt failed, trying with header authentication...');
        const headerUploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary`;
        
        const headerResponse = await fetch(headerUploadUrl, {
          method: 'POST',
          headers: {
            'X-Emby-Token': settings.token,
            'Content-Type': 'image/png',
            'Content-Encoding': 'base64'
          },
          body: base64Data
        });

        const headerResponseText = await headerResponse.text();
        console.log('Header upload response:', {
          status: headerResponse.status,
          statusText: headerResponse.statusText,
          body: headerResponseText.substring(0, 200)
        });

        if (!headerResponse.ok) {
          throw new Error(`Failed to upload poster: Both methods failed. Last error: ${headerResponse.status} ${headerResponse.statusText}`);
        }
      }

      console.log('Poster uploaded successfully!');
    } catch (error) {
      console.error('Error during poster upload:', error);
      throw error;
    }
  }

  async updateItemStatus(itemId, status, errorMessage = null) {
    const query = `
      UPDATE job_items 
      SET status = $1, 
          error_message = $2,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $3
    `;
    
    await db.query(query, [status, errorMessage, itemId]);
  }

  async applyBadgesWithCanvas(posterPath, badgeConfigs) {
    console.log('MARGIN_FIX_V2: Starting applyBadgesWithCanvas');
    try {
      // Load the poster
      let posterBuffer = await fs.readFile(posterPath);
      
      // Ensure the poster is in a format we can work with
      posterBuffer = await sharp(posterBuffer)
        .png()
        .toBuffer();
      
      const posterMetadata = await sharp(posterBuffer).metadata();
      console.log(`Poster dimensions: ${posterMetadata.width}x${posterMetadata.height}`);
      
      // No scaling needed - poster is already standardized to 1000px width
      console.log('Using standardized poster - no scaling required');
      
      // Sort badges by stacking order and filter enabled ones
      const enabledBadges = badgeConfigs.filter(config => {
        const hasValue = config.enabled && config.value !== null && config.value !== undefined;
        console.log(`Badge ${config.settings.type}: enabled=${config.enabled}, value=${config.value}, filtered=${hasValue}`);
        return hasValue;
      });
      
      const sortedBadges = enabledBadges
        .sort((a, b) => (a.settings.stackingOrder || 0) - (b.settings.stackingOrder || 0));
      
      console.log(`Processing ${sortedBadges.length} badges with canvas renderer...`); 
      
      // Apply each badge sequentially
      for (let i = 0; i < sortedBadges.length; i++) {
        const config = sortedBadges[i];
        console.log(`Applying badge ${i + 1}/${sortedBadges.length}: ${config.settings.type} at position ${config.settings.position}`);
        console.log(`Margin: ${config.settings.margin}, Size: ${config.settings.size}`);
        
        const poster = sharp(posterBuffer);
        const metadata = posterMetadata;
        
        // Determine the source image path based on badge type
        let sourceImagePath = null;
        if (config.settings.type === 'resolution' && config.value) {
          sourceImagePath = await this.canvasBadgeRenderer.getResolutionImagePath(config.value);
        } else if (config.settings.type === 'audio' && config.value) {
          sourceImagePath = await this.canvasBadgeRenderer.getAudioImagePath(config.value);
        }
        
        // Use badge settings directly - no scaling needed
        const badgeSettings = {
          ...config.settings
        };
        
        console.log(`Using badge settings:`, {
          type: config.settings.type,
          margin: badgeSettings.margin,
          size: badgeSettings.size,
          position: badgeSettings.position
        });
        
        // Generate badge using canvas renderer
        const badgeBuffer = await this.canvasBadgeRenderer.renderBadge(
          config.settings.type,
          badgeSettings,
          { 
            resolution: config.settings.type === 'resolution' ? config.value : undefined,
            audioFormat: config.settings.type === 'audio' ? config.value : undefined,
            rating: config.settings.type === 'review' ? config.value : undefined,
            ratingSource: config.settings.type === 'review' ? 'imdb' : undefined
          },
          sourceImagePath
        );
        
        // Create a Sharp instance from the badge buffer
        const badge = sharp(badgeBuffer);
        const badgeMetadata = await badge.metadata();
        
        // Verify badge size doesn't exceed poster size
        if (badgeMetadata.width > metadata.width || badgeMetadata.height > metadata.height) {
          console.warn(`Badge size (${badgeMetadata.width}x${badgeMetadata.height}) exceeds poster size (${metadata.width}x${metadata.height}). Skipping.`);
          continue;
        }

        // Calculate position based on settings, using the margin directly
        const position = this.calculateSafePosition(
          config.settings.position, 
          metadata.width, 
          metadata.height, 
          badgeMetadata.width, 
          badgeMetadata.height,
          config.settings.margin || 21
        );
        
        // Composite the badge onto the poster
        posterBuffer = await poster
          .composite([{
            input: badgeBuffer,
            ...position
          }])
          .png()
          .toBuffer();
          
        console.log(`Badge ${config.settings.type} applied successfully with canvas renderer`);
      }
      
      return posterBuffer;
    } catch (error) {
      console.error('Error applying badges with canvas:', error);
      throw new Error(`Failed to apply badges: ${error.message}`);
    }
  }

  calculateSafePosition(position, posterWidth, posterHeight, badgeWidth, badgeHeight, margin) {
    let left = 0;
    let top = 0;
    
    // Enhanced debug logging
    console.log('calculateSafePosition called with:', {
      position,
      posterWidth,
      posterHeight,
      badgeWidth,
      badgeHeight,
      margin,
      marginType: typeof margin
    });
    
    switch (position) {
      case 'top-left':
        left = margin;
        top = margin;
        break;
      case 'top-right':
        left = posterWidth - badgeWidth - margin;
        top = margin;
        break;
      case 'bottom-left':
        left = margin;
        top = posterHeight - badgeHeight - margin;
        break;
      case 'bottom-right':
        left = posterWidth - badgeWidth - margin;
        top = posterHeight - badgeHeight - margin;
        break;
      default:
        // Default to bottom-right
        left = posterWidth - badgeWidth - margin;
        top = posterHeight - badgeHeight - margin;
    }
    
    // Ensure position is within bounds
    const originalLeft = left;
    const originalTop = top;
    left = Math.max(0, Math.min(left, posterWidth - badgeWidth));
    top = Math.max(0, Math.min(top, posterHeight - badgeHeight));
    
    if (originalLeft !== left || originalTop !== top) {
      console.log('Position was clamped:', {
        originalLeft,
        originalTop,
        clampedLeft: left,
        clampedTop: top
      });
    }
    
    console.log(`Badge position for ${position}:`, {
      left,
      top,
      margin,
      centerX: left + badgeWidth/2,
      centerY: top + badgeHeight/2,
      distanceFromLeftEdge: left,
      distanceFromTopEdge: top,
      distanceFromRightEdge: posterWidth - (left + badgeWidth),
      distanceFromBottomEdge: posterHeight - (top + badgeHeight)
    });
    
    return { left, top };
  }

  async processInBatches(items, jobId, userId, onProgress) {
    const results = [];
    
    // Process items in batches based on concurrency
    for (let i = 0; i < items.length; i += this.concurrency) {
      const batch = items.slice(i, i + this.concurrency);
      
      // Process batch in parallel
      const batchResults = await Promise.all(
        batch.map(item => this.processItem(item, jobId, userId))
      );
      
      results.push(...batchResults);
      
      // Report progress
      if (onProgress) {
        const completed = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;
        const progress = (results.length / items.length) * 100;
        
        onProgress({
          completed,
          failed,
          total: items.length,
          progress: Math.round(progress)
        });
      }
    }
    
    return results;
  }
}

export default PosterProcessor;
