import { promises as fs } from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import BadgeRenderer from './badgeRenderer.js';
import db from '../../db.js';
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
    const tempPosterPath = path.join(this.tempDir, `poster-${item.jellyfin_id}.png`);
    
    try {
      // Update item status to processing
      await this.updateItemStatus(item.id, 'processing');

      // Fetch badge settings for this user
      const badgeSettings = await this.getBadgeSettings(userId, item);

      // Download poster from Jellyfin
      await this.downloadPoster(item.jellyfin_id, tempPosterPath, userId);

      // Apply badges
      const modifiedPosterBuffer = await this.badgeRenderer.applyMultipleBadges(
        tempPosterPath,
        badgeSettings
      );

      // Upload modified poster back to Jellyfin
      await this.uploadPoster(item.jellyfin_id, modifiedPosterBuffer, userId);

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
        font,
        font_size,
        font_color,
        logo_path,
        theme,
        padding,
        transparency,
        stacking_order,
        stacking_direction
      FROM resolution_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'audio' as type,
        enabled,
        position,
        font,
        font_size,
        font_color,
        logo_path,
        theme,
        padding,
        transparency,
        stacking_order,
        stacking_direction
      FROM audio_badge_settings
      WHERE user_id = $1 AND enabled = true
      
      UNION ALL
      
      SELECT 
        'review' as type,
        enabled,
        position,
        font,
        font_size,
        font_color,
        logo_path,
        theme,
        padding,
        transparency,
        stacking_order,
        stacking_direction
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
        theme: setting.theme || 'dark',
        fontSize: setting.font_size,
        padding: setting.padding,
        transparency: setting.transparency
      },
      value: this.getBadgeValue(setting.type, metadata)
    }));
  }

  async fetchItemMetadata(item, userId) {
    return await this.metadataService.fetchItemMetadata(item, userId);
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
      SELECT url, token 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    const posterUrl = `${settings.url}/Items/${jellyfinId}/Images/Primary`;
    const response = await fetch(posterUrl, {
      headers: {
        'X-MediaBrowser-Token': settings.token
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to download poster: ${response.statusText}`);
    }

    const buffer = await response.buffer();
    await fs.writeFile(outputPath, buffer);
  }

  async uploadPoster(jellyfinId, posterBuffer, userId) {
    // Get Jellyfin settings from database
    const settingsQuery = `
      SELECT url, token 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    const uploadUrl = `${settings.url}/Items/${jellyfinId}/Images/Primary`;
    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'X-MediaBrowser-Token': settings.token,
        'Content-Type': 'image/png'
      },
      body: posterBuffer
    });

    if (!response.ok) {
      throw new Error(`Failed to upload poster: ${response.statusText}`);
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
