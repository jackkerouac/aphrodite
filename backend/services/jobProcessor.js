import { pool } from '../db.js';
import logger from '../lib/logger.js';
import { getJobById, updateJobStatus, updateJobItemStatus } from '../models/jobs.js';
import fetch from 'node-fetch';
import path from 'path';
import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Base directory for image processing (Docker-aware)
const TEMP_DIR = process.env.TEMP_DIR || path.join(__dirname, '../../temp');
const PROCESSED_DIR = process.env.PROCESSED_DIR || path.join(__dirname, '../../processed');

// Ensure directories exist
async function ensureDirectories() {
  await fs.mkdir(TEMP_DIR, { recursive: true });
  await fs.mkdir(PROCESSED_DIR, { recursive: true });
}

/**
 * Process a job and apply badges to all items
 */
export async function processJob(jobId) {
  try {
    await ensureDirectories();
    
    const job = await getJobById(jobId);
    if (!job) {
      logger.error(`Job ${jobId} not found`);
      return;
    }

    logger.info(`Starting job ${jobId} processing`);
    await updateJobStatus(jobId, 'running');

    // Get job items
    const itemsResult = await pool.query(
      'SELECT * FROM job_items WHERE job_id = $1 ORDER BY id',
      [jobId]
    );
    const items = itemsResult.rows;

    let processedCount = 0;
    let failedCount = 0;

    // Process each item
    for (const item of items) {
      try {
        await processItem(job, item);
        processedCount++;
        await updateJobItemStatus(item.id, 'completed');
        
        // Update job progress
        await updateJobStatus(jobId, 'running', {
          items_processed: processedCount,
          items_failed: failedCount
        });
      } catch (error) {
        logger.error(`Error processing item ${item.id}:`, error);
        failedCount++;
        await updateJobItemStatus(item.id, 'failed', error.message);
        
        // Update job progress
        await updateJobStatus(jobId, 'running', {
          items_processed: processedCount,
          items_failed: failedCount
        });
      }
    }

    // Complete the job
    const finalStatus = failedCount === items.length ? 'failed' : 'completed';
    await updateJobStatus(jobId, finalStatus, {
      items_processed: processedCount,
      items_failed: failedCount
    });

    logger.info(`Job ${jobId} completed. Processed: ${processedCount}, Failed: ${failedCount}`);
  } catch (error) {
    logger.error(`Fatal error processing job ${jobId}:`, error);
    await updateJobStatus(jobId, 'failed');
  }
}

/**
 * Process a single item - download poster, apply badges, upload back
 */
async function processItem(job, item) {
  // Get Jellyfin settings
  const jellyfinResult = await pool.query(
    'SELECT * FROM jellyfin_settings WHERE user_id = $1',
    [job.user_id]
  );
  const jellyfinSettings = jellyfinResult.rows[0];
  
  if (!jellyfinSettings) {
    throw new Error('Jellyfin settings not found for user');
  }

  // Download original poster
  const posterPath = await downloadPoster(
    jellyfinSettings.jellyfin_url,
    jellyfinSettings.jellyfin_api_key,
    item.jellyfin_item_id
  );

  // Get enabled badges for user
  const enabledBadges = await getEnabledBadges(job.user_id);
  
  // Apply each enabled badge
  let processedPath = posterPath;
  
  if (enabledBadges.audio) {
    processedPath = await applyAudioBadge(processedPath, job.user_id, item);
  }
  
  if (enabledBadges.resolution) {
    processedPath = await applyResolutionBadge(processedPath, job.user_id, item);
  }
  
  if (enabledBadges.review) {
    processedPath = await applyReviewBadge(processedPath, job.user_id, item);
  }

  // Upload the processed image back to Jellyfin
  await uploadToJellyfin(
    jellyfinSettings.jellyfin_url,
    jellyfinSettings.jellyfin_api_key,
    item.jellyfin_item_id,
    processedPath
  );

  // Clean up temporary files
  if (posterPath !== processedPath) {
    await fs.unlink(posterPath);
  }
  await fs.unlink(processedPath);
}

/**
 * Download poster from Jellyfin
 */
async function downloadPoster(jellyfinUrl, apiKey, itemId) {
  const url = `${jellyfinUrl}/Items/${itemId}/Images/Primary`;
  const response = await fetch(url, {
    headers: {
      'X-Emby-Token': apiKey
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to download poster: ${response.statusText}`);
  }

  const buffer = await response.buffer();
  const posterPath = path.join(TEMP_DIR, `${itemId}_original.jpg`);
  await fs.writeFile(posterPath, buffer);
  
  return posterPath;
}

/**
 * Get enabled badges for a user
 */
async function getEnabledBadges(userId) {
  const [audioResult, resolutionResult, reviewResult] = await Promise.all([
    pool.query('SELECT enabled FROM audio_badge_settings WHERE user_id = $1', [userId]),
    pool.query('SELECT enabled FROM resolution_badge_settings WHERE user_id = $1', [userId]),
    pool.query('SELECT enabled FROM review_badge_settings WHERE user_id = $1', [userId])
  ]);

  return {
    audio: audioResult.rows[0]?.enabled || false,
    resolution: resolutionResult.rows[0]?.enabled || false,
    review: reviewResult.rows[0]?.enabled || false
  };
}

/**
 * Apply audio badge to image
 * This is a placeholder - actual implementation would use canvas or image processing library
 */
async function applyAudioBadge(imagePath, userId, item) {
  // TODO: Implement actual badge application using canvas
  logger.info(`Applying audio badge to ${item.title}`);
  return imagePath; // For now, return unchanged
}

/**
 * Apply resolution badge to image
 * This is a placeholder - actual implementation would use canvas or image processing library
 */
async function applyResolutionBadge(imagePath, userId, item) {
  // TODO: Implement actual badge application using canvas
  logger.info(`Applying resolution badge to ${item.title}`);
  return imagePath; // For now, return unchanged
}

/**
 * Apply review badge to image
 * This is a placeholder - actual implementation would use canvas or image processing library
 */
async function applyReviewBadge(imagePath, userId, item) {
  // TODO: Implement actual badge application using canvas
  logger.info(`Applying review badge to ${item.title}`);
  return imagePath; // For now, return unchanged
}

/**
 * Upload processed image back to Jellyfin
 */
async function uploadToJellyfin(jellyfinUrl, apiKey, itemId, imagePath) {
  const imageBuffer = await fs.readFile(imagePath);
  
  const url = `${jellyfinUrl}/Items/${itemId}/Images/Primary`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-Emby-Token': apiKey,
      'Content-Type': 'image/jpeg'
    },
    body: imageBuffer
  });

  if (!response.ok) {
    throw new Error(`Failed to upload poster: ${response.statusText}`);
  }
}
