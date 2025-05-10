import fs from 'fs';
import logger from '../lib/logger.js';
import {
  getJobById,
  updateJobStatus,
  getJobItems,
  updateJobItemStatus
} from '../models/jobs.js';
import {
  processImageWithBadges,
  downloadImage,
  getTempPath,
  cleanupTempFiles
} from '../lib/imageProcessor.js';

// Import badge settings models
import { getResolutionBadgeSettingsByUserId } from '../models/resolutionBadgeSettings.js';
import { getAudioBadgeSettingsByUserId } from '../models/audioBadgeSettings.js';
import { getReviewBadgeSettingsByUserId } from '../models/reviewBadgeSettings.js';
import { getJellyfinSettingsByUserId } from '../models/jellyfinSettings.js';

/**
 * Process a single job
 * @param {number} jobId - The ID of the job to process
 */
export async function processJob(jobId) {
  try {
    // Get job details
    const job = await getJobById(jobId);
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }
    
    // Update job status to running
    await updateJobStatus(jobId, 'running');
    
    // Get enabled badge settings
    const badgeSettings = await getBadgeSettings(job.user_id);
    
    // Get Jellyfin settings for API access
    const jellyfinSettings = await getJellyfinSettingsByUserId(job.user_id);
    if (!jellyfinSettings) {
      throw new Error('Jellyfin settings not found');
    }
    
    // Process job items
    const { items } = await getJobItems(jobId, 1, 1000); // Get up to 1000 items at once
    
    let processed = 0;
    let failed = 0;
    
    for (const item of items) {
      try {
        await processJobItem(item, badgeSettings, jellyfinSettings);
        await updateJobItemStatus(item.id, 'completed');
        processed++;
      } catch (error) {
        logger.error(`Error processing item ${item.id}:`, error);
        await updateJobItemStatus(item.id, 'failed', error.message);
        failed++;
      }
      
      // Update job progress
      await updateJobStatus(jobId, 'running', {
        items_processed: processed,
        items_failed: failed
      });
    }
    
    // Mark job as completed
    await updateJobStatus(jobId, 'completed', {
      items_processed: processed,
      items_failed: failed
    });
    
    logger.info(`Job ${jobId} completed. Processed: ${processed}, Failed: ${failed}`);
  } catch (error) {
    logger.error(`Error processing job ${jobId}:`, error);
    await updateJobStatus(jobId, 'failed');
    throw error;
  }
}

/**
 * Process a single job item
 * @param {Object} item - The job item to process
 * @param {Object} badgeSettings - Badge settings to apply
 * @param {Object} jellyfinSettings - Jellyfin API settings
 */
async function processJobItem(item, badgeSettings, jellyfinSettings) {
  const tempFiles = [];
  
  try {
    // Download the original poster from Jellyfin
    const posterUrl = `${jellyfinSettings.jellyfin_url}/Items/${item.jellyfin_item_id}/Images/Primary`;
    const tempInputPath = getTempPath(`input_${item.id}.jpg`);
    tempFiles.push(tempInputPath);
    
    await downloadImage(posterUrl, tempInputPath);
    
    // Process the image with badges
    const tempOutputPath = getTempPath(`output_${item.id}.jpg`);
    tempFiles.push(tempOutputPath);
    
    await processImageWithBadges(tempInputPath, badgeSettings, tempOutputPath);
    
    // Upload the processed image back to Jellyfin
    await uploadToJellyfin(
      tempOutputPath,
      item.jellyfin_item_id,
      jellyfinSettings
    );
    
    logger.info(`Successfully processed item ${item.id}: ${item.title}`);
  } finally {
    // Clean up temporary files
    cleanupTempFiles(tempFiles);
  }
}

/**
 * Get enabled badge settings for a user
 * @param {number} userId - The user ID
 * @returns {Object} Combined badge settings
 */
async function getBadgeSettings(userId) {
  const [resolution, audio, review] = await Promise.all([
    getResolutionBadgeSettingsByUserId(userId),
    getAudioBadgeSettingsByUserId(userId),
    getReviewBadgeSettingsByUserId(userId)
  ]);
  
  const settings = {};
  
  // Only include enabled badges
  if (resolution?.display) {
    settings.resolution = resolution;
  }
  
  if (audio?.display) {
    settings.audio = audio;
  }
  
  if (review?.display) {
    settings.review = review;
  }
  
  return settings;
}

/**
 * Upload an image to Jellyfin
 * @param {string} imagePath - Path to the image file
 * @param {string} itemId - Jellyfin item ID
 * @param {Object} jellyfinSettings - Jellyfin API settings
 */
async function uploadToJellyfin(imagePath, itemId, jellyfinSettings) {
  try {
    const imageBuffer = fs.readFileSync(imagePath);
    
    const response = await fetch(
      `${jellyfinSettings.jellyfin_url}/Items/${itemId}/Images/Primary`,
      {
        method: 'POST',
        headers: {
          'X-Emby-Token': jellyfinSettings.jellyfin_api_key,
          'Content-Type': 'image/jpeg'
        },
        body: imageBuffer
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to upload image: ${response.statusText}`);
    }
    
    logger.info(`Uploaded processed image for item ${itemId}`);
  } catch (error) {
    logger.error(`Error uploading to Jellyfin:`, error);
    throw error;
  }
}
