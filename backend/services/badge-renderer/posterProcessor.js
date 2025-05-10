import { promises as fs } from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import BadgeRenderer from './badgeRenderer.js';
import { pool as db } from '../../db.js';
import MetadataService from './metadataService.js';

class PosterProcessor {
  constructor() {
    this.badgeRenderer = new BadgeRenderer();
    this.metadataService = new MetadataService();
    this.tempDir = process.env.TEMP_DIR || path.join(process.cwd(), 'temp');
    this.concurrency = parseInt(process.env.BATCH_CONCURRENCY || '4');
  }

  async init() {
    // Ensure temp directory exists
    await fs.mkdir(this.tempDir, { recursive: true });
    await this.badgeRenderer.init();
  }

  async processItem(item, jobId, userId) {
    const tempPosterPath = path.join(this.tempDir, `poster-${item.jellyfin_item_id}.png`);
    
    try {
      // Update item status to processing
      await this.updateItemStatus(item.id, 'processing');

      // Fetch badge settings for this user
      const badgeSettings = await this.getBadgeSettings(userId, item);

      // Download poster from Jellyfin
      await this.downloadPoster(item.jellyfin_item_id, tempPosterPath, userId);

      // Apply badges
      const modifiedPosterBuffer = await this.badgeRenderer.applyMultipleBadges(
        tempPosterPath,
        badgeSettings
      );

      // Upload modified poster back to Jellyfin
      await this.uploadPoster(item.jellyfin_item_id, modifiedPosterBuffer, userId);

      // Update item status to completed
      await this.updateItemStatus(item.id, 'completed');

      // Clean up temp file
      await fs.unlink(tempPosterPath).catch(() => {});

      return { success: true, itemId: item.id };
    } catch (error) {
      console.error(`Error processing item ${item.id}:`, error);
      await this.updateItemStatus(item.id, 'failed', error.message);
      
      // Clean up temp file
      await fs.unlink(tempPosterPath).catch(() => {});

      return { success: false, itemId: item.id, error: error.message };
    }
  }

  async getBadgeSettings(userId, item) {
    const query = `
      SELECT 
        'resolution' as type,
        enabled,
        position,
        font_family,
        font_size,
        text_color,
        NULL as logo_path,
        NULL as theme,
        margin as padding,
        background_opacity as transparency,
        z_index as stacking_order,
        NULL as stacking_direction
      FROM resolution_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'audio' as type,
        enabled,
        position,
        font_family,
        font_size,
        text_color,
        badge_image as logo_path,
        NULL as theme,
        margin as padding,
        background_opacity as transparency,
        z_index as stacking_order,
        NULL as stacking_direction
      FROM audio_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'review' as type,
        enabled,
        position,
        font_family,
        font_size,
        text_color,
        NULL as logo_path,
        NULL as theme,
        margin as padding,
        background_opacity as transparency,
        z_index as stacking_order,
        NULL as stacking_direction
      FROM review_badge_settings
      WHERE user_id = $1 AND enabled = true
    `;

    const settingsResult = await db.query(query, [userId]);
    const settings = settingsResult.rows;

    // Fetch metadata for the item to determine badge values
    const metadata = await this.fetchItemMetadata(item, userId);

    return settings.map(setting => ({
      enabled: setting.enabled,
      settings: {
        type: setting.type,
        position: setting.position || 'top-right',
        theme: 'dark', // Default to dark theme
        fontSize: setting.font_size,
        padding: setting.padding || 8,
        transparency: setting.transparency || 1
      },
      value: this.getBadgeValue(setting.type, metadata)
    }));
  }

  async fetchItemMetadata(item, userId) {
    // Create an item object that the metadata service expects
    const metadataItem = {
      jellyfin_id: item.jellyfin_item_id,
      media_type: 'Movie' // Default to Movie for now, could be determined from title or other metadata
    };
    return await this.metadataService.fetchItemMetadata(metadataItem, userId);
  }

  getBadgeValue(type, metadata) {
    switch (type) {
      case 'resolution':
        return metadata.resolution;
      case 'audio':
        return metadata.audioFormat;
      case 'review':
        return metadata.imdbRating || metadata.tmdbRating;
      default:
        return null;
    }
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
    // Use the Items endpoint directly for downloading images
    const posterUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary`;
    
    const headers = {};
    if (settings.token) {
      headers['X-Emby-Token'] = settings.token;
    }

    console.log('Downloading poster:', {
      url: posterUrl,
      token: settings.token ? '***' + settings.token.slice(-4) : 'none'
    });

    const response = await fetch(posterUrl, {
      headers: headers
    });

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
    // Use the Items endpoint directly for uploading images
    const uploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary`;
    
    const headers = {
      'Content-Type': 'image/png'
    };
    
    if (settings.token) {
      headers['X-Emby-Token'] = settings.token;
    }

    console.log('Uploading poster:', {
      url: uploadUrl,
      token: settings.token ? '***' + settings.token.slice(-4) : 'none'
    });

    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: headers,
      body: posterBuffer
    });

    if (!response.ok) {
      console.error('Failed to upload poster:', {
        status: response.status,
        statusText: response.statusText,
        url: uploadUrl
      });
      throw new Error(`Failed to upload poster: ${response.status} ${response.statusText}`);
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
