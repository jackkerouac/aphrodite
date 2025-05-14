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
import logger from '../../lib/logger.js';

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
      logger.info(`Job ${jobId}: Processing item ${item.id} (${item.jellyfin_item_id}: ${item.title || 'No title'})`);
      
      // Validate input
      if (!item.jellyfin_item_id) {
        throw new Error('Missing jellyfin_item_id for item');
      }

      // Fetch badge settings for this user
      let badgeSettings = [];
      try {
        badgeSettings = await this.getBadgeSettings(userId, item);
        logger.info(`Job ${jobId}: Retrieved ${badgeSettings.length} badge settings for item ${item.id}`);
      } catch (settingsError) {
        logger.error(`Job ${jobId}: Failed to get badge settings: ${settingsError.message}`);
        throw new Error(`Failed to get badge settings: ${settingsError.message}`);
      }

      // Verify we have valid badge settings
      if (!badgeSettings || badgeSettings.length === 0) {
        logger.warn(`Job ${jobId}: No badge settings available for item ${item.id}`);
        await this.updateItemStatus(item.id, 'completed', 'No badge settings available');
        return { success: true, itemId: item.id, message: 'No badge settings available' };
      }

      // Download poster from Jellyfin
      try {
        await this.downloadPoster(item.jellyfin_item_id, tempPosterPath, userId);
        logger.info(`Job ${jobId}: Downloaded poster for item ${item.id}`);
      } catch (downloadError) {
        logger.error(`Job ${jobId}: Failed to download poster: ${downloadError.message}`);
        await this.updateItemStatus(item.id, 'failed', `Failed to download poster: ${downloadError.message}`);
        throw new Error(`Failed to download poster: ${downloadError.message}`);
      }
      
      // Standardize the poster to 1000px width
      try {
        const standardizationResult = await this.posterStandardizer.standardizePoster(
          tempPosterPath,
          standardizedPosterPath
        );
        logger.info(`Job ${jobId}: Standardized poster for item ${item.id}: ${JSON.stringify(standardizationResult)}`);
      } catch (standardizeError) {
        logger.error(`Job ${jobId}: Failed to standardize poster: ${standardizeError.message}`);
        await this.updateItemStatus(item.id, 'failed', `Failed to standardize poster: ${standardizeError.message}`);
        throw new Error(`Failed to standardize poster: ${standardizeError.message}`);
      }

      // Apply badges using canvas renderer if enabled
      let modifiedPosterBuffer;
      let badgeApplied = false;
      let badgeError = null;
      
      // Try canvas renderer first if enabled
      if (this.useCanvasRenderer) {
        try {
          // Log all badge settings coming from the job
          logger.info(`Job ${jobId}: Using badge settings:`, JSON.stringify(badgeSettings.map(badge => ({
            type: badge.settings.type,
            size: badge.settings.size,
            position: badge.settings.position
          }))));
          
          modifiedPosterBuffer = await this.applyBadgesWithCanvas(standardizedPosterPath, badgeSettings);
          badgeApplied = true;
          logger.info(`Job ${jobId}: Successfully applied badges with canvas renderer for item ${item.id}`);
        } catch (canvasError) {
          logger.error(`Job ${jobId}: Canvas renderer failed: ${canvasError.message}. Trying fallback renderer...`);
          badgeError = canvasError.message;
          
          // Fall back to the SVG renderer
          try {
            modifiedPosterBuffer = await this.badgeRenderer.applyMultipleBadges(
              standardizedPosterPath,
              badgeSettings
            );
            badgeApplied = true;
            logger.info(`Job ${jobId}: Successfully applied badges with fallback SVG renderer for item ${item.id}`);
          } catch (svgError) {
            logger.error(`Job ${jobId}: SVG renderer also failed: ${svgError.message}. Continuing with original poster...`);
            badgeError = `Canvas renderer error: ${canvasError.message}. SVG renderer error: ${svgError.message}`;
            // If both renderers fail, use the standardized poster without badges
            modifiedPosterBuffer = await fs.readFile(standardizedPosterPath);
          }
        }
      } else {
        // If canvas renderer is disabled, use SVG renderer directly
        try {
          modifiedPosterBuffer = await this.badgeRenderer.applyMultipleBadges(
            standardizedPosterPath,
            badgeSettings
          );
          badgeApplied = true;
          logger.info(`Job ${jobId}: Successfully applied badges with SVG renderer for item ${item.id}`);
        } catch (svgError) {
          logger.error(`Job ${jobId}: SVG renderer failed: ${svgError.message}. Continuing with original poster...`);
          badgeError = svgError.message;
          // If SVG renderer fails, use the standardized poster without badges
          modifiedPosterBuffer = await fs.readFile(standardizedPosterPath);
        }
      }
      
      // Verify we have a valid buffer
      if (!modifiedPosterBuffer || modifiedPosterBuffer.length === 0) {
        logger.error(`Job ${jobId}: Empty poster buffer for item ${item.id}`);
        throw new Error('Generated poster buffer is empty');
      }

      // Save the modified poster for inspection
      const modifiedPosterPath = path.join(this.tempDir, `poster-modified-${item.jellyfin_item_id}.png`);
      await fs.writeFile(modifiedPosterPath, modifiedPosterBuffer);
      logger.info(`Job ${jobId}: Modified poster saved at: ${modifiedPosterPath}${badgeApplied ? '' : ' (without badges due to renderer errors)'}`);

      // Upload modified poster back to Jellyfin
      try {
        await this.uploadPoster(item.jellyfin_item_id, modifiedPosterBuffer, userId);
        logger.info(`Job ${jobId}: Uploaded modified poster for item ${item.id}`);
      } catch (uploadError) {
        logger.error(`Job ${jobId}: Failed to upload poster: ${uploadError.message}`);
        await this.updateItemStatus(item.id, 'failed', `Failed to upload poster: ${uploadError.message}`);
        throw new Error(`Failed to upload poster: ${uploadError.message}`);
      }

      // Update item status to completed
      if (badgeApplied) {
        await this.updateItemStatus(item.id, 'completed');
        logger.info(`Job ${jobId}: Item ${item.id} completed successfully with badges applied`);
      } else {
        await this.updateItemStatus(item.id, 'completed', `Badges could not be applied: ${badgeError || 'Unknown error'}`);
        logger.warn(`Job ${jobId}: Item ${item.id} completed but no badges were applied: ${badgeError || 'Unknown error'}`);
      }

      // Keep temp files for debugging purposes
      return { success: true, itemId: item.id, badgeApplied };
    } catch (error) {
      logger.error(`Job ${jobId}: Error processing item ${item.id}: ${error.message}`);
      await this.updateItemStatus(item.id, 'failed', error.message);
      
      return { success: false, itemId: item.id, error: error.message };
    }
  }

  async getBadgeSettings(userId, item) {
    // Map SQL positions to BadgePosition enum values
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
        z_index as stacking_order,
        use_brand_colors
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
        z_index as stacking_order,
        use_brand_colors
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
        z_index as stacking_order,
        use_brand_colors
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
          use_brand_colors: setting.use_brand_colors,
          // Fixed settings for Review badges specifically - ensure maxSourcesToShow is properly mapped
          maxSourcesToShow: setting.type === 'review' ? (reviewSettings?.max_sources_to_show ? parseInt(reviewSettings.max_sources_to_show) : 3) : undefined,
          displayFormat: setting.type === 'review' ? (reviewSettings?.display_format || 'vertical') : undefined,
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
    // Added a comment to clarify that errorMessage can now also be a warning message for completed items
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
      
      console.log(`Processing ${sortedBadges.length} badges with canvas renderer:`, 
        sortedBadges.map(b => 
          `${b.settings.type} (size=${b.settings.size}, position=${b.settings.position})` 
        ));
      
      // If no badges to process, return the original poster
      if (sortedBadges.length === 0) {
        console.log('No enabled badges to process, returning original poster');
        return posterBuffer;
      } 
      
      // Apply each badge sequentially
      for (let i = 0; i < sortedBadges.length; i++) {
      const config = sortedBadges[i];
      console.log(`Applying badge ${i + 1}/${sortedBadges.length}: ${config.settings.type} at position ${config.settings.position}`);
      console.log(`Margin: ${config.settings.margin}, Size: ${config.settings.size}`);
      
      const poster = sharp(posterBuffer);
      const metadata = posterMetadata;
      
      // Debug print complete config
      console.log(`Complete badge config for type=${config.settings.type}:`, JSON.stringify(config));
      
      // Special handling for review badge values - ensure the scores array is properly formatted
      if (config.settings.type === 'review' && Array.isArray(config.value)) {
      console.log('Processing review badge with scores:', config.value);
      
      // Format the scores array correctly - this is key for matching frontend preview
      config.value = config.value.map(score => ({
      name: score.name,
      rating: parseFloat(score.rating) || 0,
      outOf: parseFloat(score.outOf) || (score.name === 'RT' || score.name === 'Metacritic' ? 100 : 10)
      }));
      }
      
      // Determine the source image path based on badge type
      let sourceImagePath = null;
      try {
      if (config.settings.type === 'resolution' && config.value) {
      sourceImagePath = await this.canvasBadgeRenderer.getResolutionImagePath(config.value);
      } else if (config.settings.type === 'audio' && config.value) {
      sourceImagePath = await this.canvasBadgeRenderer.getAudioImagePath(config.value);
      }
      } catch (error) {
      console.error(`Error getting source image path: ${error.message}. Continuing without source image.`);
      sourceImagePath = null;
      }
      
      // Ensure badge size is a numeric value and is preserved in the rendering
      const badgeSize = typeof config.settings.size === 'number' ? config.settings.size :
                     typeof config.settings.badge_size === 'number' ? config.settings.badge_size : 100;
      
      console.log(`Using badge size: ${badgeSize} for ${config.settings.type} badge`);
      
      // Map visual settings with consistent naming between frontend/backend
      const badgeSettings = {
      ...config.settings,
      // Ensure type is explicitly set for identification in applyBackground
      type: config.settings.type,
      // Map transparency to backgroundOpacity for consistency with frontend
      backgroundOpacity: config.settings.transparency !== undefined ? config.settings.transparency : 1,
      // Ensure size is passed through directly
      size: badgeSize,
      badge_size: badgeSize,
        // Important display settings for review badges
          sources: config.settings.type === 'review' ? config.value : undefined,
          maxSourcesToShow: config.settings.type === 'review' ? config.settings.maxSourcesToShow : undefined,
          displayFormat: config.settings.type === 'review' ? config.settings.displayFormat || 'vertical' : undefined,
          // Other important settings
          borderOpacity: config.settings.borderOpacity !== undefined ? config.settings.borderOpacity : 1,
          showDividers: config.settings.type === 'review' ? true : undefined
        };
        
        console.log(`Using badge settings:`, {
          type: config.settings.type,
          margin: badgeSettings.margin,
          size: badgeSettings.size,
          position: badgeSettings.position
        });
        
        // Generate badge using canvas renderer
        let badgeBuffer;
        try {
          badgeBuffer = await this.canvasBadgeRenderer.renderBadge(
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
        } catch (renderError) {
          console.error(`Error rendering badge: ${renderError.message}. Skipping this badge.`);
          continue; // Skip this badge and move to the next one
        }
        
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
        try {
          posterBuffer = await poster
            .composite([{
              input: badgeBuffer,
              ...position
            }])
            .png()
            .toBuffer();
        } catch (compositeError) {
          console.error(`Error compositing badge onto poster: ${compositeError.message}. Using previous poster state.`);
          // Continue with the current posterBuffer without this badge
          continue;
        }
          
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
    
    // Ensure margin is a number
    const safeMargin = typeof margin === 'number' && !isNaN(margin) ? margin : 21;
    
    // Enhanced debug logging
    console.log('calculateSafePosition called with:', {
      position,
      posterWidth,
      posterHeight,
      badgeWidth,
      badgeHeight,
      margin: safeMargin,
      marginType: typeof safeMargin
    });
    
    // Map position string to coordinates based on margin
    switch (position) {
      case 'top-left':
        left = safeMargin;
        top = safeMargin;
        break;
      case 'top-right':
        left = posterWidth - badgeWidth - safeMargin;
        top = safeMargin;
        break;
      case 'bottom-left':
        left = safeMargin;
        top = posterHeight - badgeHeight - safeMargin;
        break;
      case 'bottom-right':
        left = posterWidth - badgeWidth - safeMargin;
        top = posterHeight - badgeHeight - safeMargin;
        break;
      case 'top-center':
        left = (posterWidth - badgeWidth) / 2;
        top = safeMargin;
        break;
      case 'bottom-center':
        left = (posterWidth - badgeWidth) / 2;
        top = posterHeight - badgeHeight - safeMargin;
        break;
      case 'center-left':
        left = safeMargin;
        top = (posterHeight - badgeHeight) / 2;
        break;
      case 'center-right':
        left = posterWidth - badgeWidth - safeMargin;
        top = (posterHeight - badgeHeight) / 2;
        break;
      case 'center':
        left = (posterWidth - badgeWidth) / 2;
        top = (posterHeight - badgeHeight) / 2;
        break;
      default:
        // Default to bottom-right if position is unrecognized
        left = posterWidth - badgeWidth - safeMargin;
        top = posterHeight - badgeHeight - safeMargin;
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
      margin: safeMargin,
      centerX: left + badgeWidth/2,
      centerY: top + badgeHeight/2,
      distanceFromLeftEdge: left,
      distanceFromTopEdge: top,
      distanceFromRightEdge: posterWidth - (left + badgeWidth),
      distanceFromBottomEdge: posterHeight - (top + badgeHeight)
    });
    
    return { left, top };
  }

  /**
   * Process items in batches with improved error handling and logging
   */
  async processInBatches(items, jobId, userId, onProgress) {
    const results = [];
    const failedItems = [];
    let startTime = Date.now();
    
    // Log start of batch processing
    console.log(`Starting batch processing for job ${jobId} with ${items.length} items and concurrency ${this.concurrency}`);
    logger.info(`Starting batch processing for job ${jobId}. Items: ${items.length}, Concurrency: ${this.concurrency}`);
    
    // Process items in batches based on concurrency
    for (let i = 0; i < items.length; i += this.concurrency) {
      const batchStartTime = Date.now();
      const batch = items.slice(i, i + this.concurrency);
      const batchNumber = Math.floor(i / this.concurrency) + 1;
      const totalBatches = Math.ceil(items.length / this.concurrency);
      
      // Log batch start
      console.log(`Processing batch ${batchNumber}/${totalBatches} with ${batch.length} items`);
      logger.info(`Job ${jobId}: Processing batch ${batchNumber}/${totalBatches} with ${batch.length} items`);
      
      try {
        // Process batch in parallel
        const batchResults = await Promise.all(
          batch.map(item => this.processItem(item, jobId, userId)
            .catch(error => {
              // Capture individual item errors but don't fail the whole batch
              logger.error(`Error processing item ${item.id} (${item.jellyfin_item_id}): ${error.message}`);
              return { 
                success: false, 
                itemId: item.id, 
                error: error.message,
                jellyfin_item_id: item.jellyfin_item_id 
              };
            })
          )
        );
        
        results.push(...batchResults);
        
        // Track failed items for possible retry
        const batchFailedItems = batchResults.filter(r => !r.success);
        if (batchFailedItems.length > 0) {
          failedItems.push(...batchFailedItems);
          logger.warn(`Job ${jobId}: ${batchFailedItems.length} items failed in batch ${batchNumber}`);
          console.log(`${batchFailedItems.length} items failed in batch ${batchNumber}:`, 
            batchFailedItems.map(item => ({ id: item.itemId, error: item.error })));
        }
        
        // Calculate batch duration and performance
        const batchDuration = (Date.now() - batchStartTime) / 1000;
        const itemsPerSecond = batch.length / batchDuration;
        console.log(`Batch ${batchNumber} completed in ${batchDuration.toFixed(2)}s (${itemsPerSecond.toFixed(2)} items/sec)`);
        logger.info(`Job ${jobId}: Batch ${batchNumber} completed in ${batchDuration.toFixed(2)}s (${itemsPerSecond.toFixed(2)} items/sec)`);
      } catch (batchError) {
        // Log batch failure but continue with next batch
        logger.error(`Job ${jobId}: Error processing batch ${batchNumber}: ${batchError.message}`);
        console.error(`Error processing batch ${batchNumber}:`, batchError);
      }
      
      // Report progress after each batch
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
    
    // Log final summary
    const totalDuration = (Date.now() - startTime) / 1000;
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;
    const successRate = (successCount / items.length) * 100;
    
    console.log(`Batch processing complete. Duration: ${totalDuration.toFixed(2)}s, Success: ${successCount}/${items.length} (${successRate.toFixed(2)}%), Failed: ${failureCount}`);
    logger.info(`Job ${jobId}: Batch processing complete. Duration: ${totalDuration.toFixed(2)}s, Success: ${successCount}/${items.length} (${successRate.toFixed(2)}%), Failed: ${failureCount}`);
    
    return results;
  }
}

export default PosterProcessor;
