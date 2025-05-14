import { pool } from '../db.js';
import logger from '../lib/logger.js';
import { getJobById, updateJobStatus, updateJobItemStatus } from '../models/jobs.js';
import { emitToUser } from '../lib/websocket.js';
import PosterProcessor from './badge-renderer/posterProcessor.js';

/**
 * Process a job and apply badges to all items
 */
export async function processJob(jobId) {
  let startTime = Date.now();
  let job = null;
  
  try {
    // First get the job without user_id constraint to find the user
    const { pool } = await import('../db.js');
    const jobResult = await pool.query('SELECT * FROM jobs WHERE id = $1', [jobId]);
    
    if (!jobResult.rows[0]) {
      logger.error(`Job ${jobId} not found`);
      return;
    }
    
    job = jobResult.rows[0];

    logger.info(`Starting job ${jobId} processing for user ${job.user_id}`);
    await updateJobStatus(jobId, 'running');

    // Initialize poster processor
    const posterProcessor = new PosterProcessor();
    await posterProcessor.init();

    // Get job items
    const itemsResult = await pool.query(
      'SELECT ji.*, ji.jellyfin_item_id, j.badge_settings FROM job_items ji ' +
      'JOIN jobs j ON ji.job_id = j.id ' +
      'WHERE ji.job_id = $1 ORDER BY ji.id',
      [jobId]
    );
    const items = itemsResult.rows;
    
    // Get the badge settings from the job
    try {
      let badgeSettings;
      if (typeof job.badge_settings === 'string') {
        badgeSettings = JSON.parse(job.badge_settings || '[]');
      } else if (job.badge_settings) {
        badgeSettings = job.badge_settings;
      } else {
        badgeSettings = [];
      }
      logger.info(`Job ${jobId} has ${badgeSettings.length} badge settings defined`);
    } catch (error) {
      logger.warn(`Failed to parse badge settings for job ${jobId}: ${error.message}`);
    }

    // Emit job started event
    emitToUser(job.user_id, 'job-status', {
      jobId,
      status: 'running',
      progress: 0,
      totalItems: items.length
    });

    let processedCount = 0;
    let failedCount = 0;

    // Progress callback for batch processing
    const onProgress = ({ completed, failed, total, progress }) => {
      processedCount = completed;
      failedCount = failed;

      // Log progress
      logger.info(`Job ${jobId} progress: ${progress}% (${completed}/${total} completed, ${failed} failed)`);
      
      // Update job status in database
      updateJobStatus(jobId, 'running', {
        items_processed: processedCount,
        items_failed: failedCount
      });

      // Emit progress update
      emitToUser(job.user_id, 'job-progress', {
        jobId,
        processedCount,
        failedCount,
        totalItems: total,
        progress
      });
    };

    // Process items in batches
    const results = await posterProcessor.processInBatches(
      items,
      jobId,
      job.user_id,
      onProgress
    );

    // Determine final status
    let finalStatus = 'completed';
    if (failedCount === items.length) {
      finalStatus = 'failed';
    } else if (failedCount > 0) {
      finalStatus = 'completed'; // We'll still mark as completed even with some failures
    }

    // Calculate summary statistics
    const successCount = processedCount - failedCount;
    const successRate = items.length > 0 ? (successCount / items.length) * 100 : 0;
    const duration = (Date.now() - startTime) / 1000;
    
    // Log completion
    logger.info(`Job ${jobId} completed with status: ${finalStatus}`);
    logger.info(`Job ${jobId} statistics: Processed: ${processedCount}/${items.length}, Success rate: ${successRate.toFixed(2)}%, Duration: ${duration.toFixed(2)}s`);
    
    // Complete the job
    await updateJobStatus(jobId, finalStatus, {
      items_processed: processedCount,
      items_failed: failedCount
    });

    // Emit job completed event
    emitToUser(job.user_id, 'job-status', {
      jobId,
      status: finalStatus,
      processedCount,
      failedCount,
      totalItems: items.length,
      progress: 100
    });

    // Return summary data for potential logging or future reporting
    return {
      jobId,
      status: finalStatus,
      processedCount,
      failedCount,
      successRate: successRate.toFixed(2),
      duration: duration.toFixed(2)
    };
  } catch (error) {
    const duration = (Date.now() - startTime) / 1000;
    logger.error(`Fatal error processing job ${jobId} after ${duration.toFixed(2)}s:`, error);
    await updateJobStatus(jobId, 'failed');

    // Emit job error event - use job value from above if already fetched
    if (job) {
      emitToUser(job.user_id, 'job-error', {
        jobId,
        error: error.message
      });
    } else {
      // If job wasn't found initially, try again to find user_id
      try {
        const { pool } = await import('../db.js');
        const jobResult = await pool.query('SELECT * FROM jobs WHERE id = $1', [jobId]);
        const job = jobResult.rows[0];
        
        if (job) {
          emitToUser(job.user_id, 'job-error', {
            jobId,
            error: error.message
          });
        }
      } catch (secondaryError) {
        logger.error(`Failed to emit job error for job ${jobId}:`, secondaryError);
      }
    }
    
    // Return error information
    return {
      jobId,
      status: 'failed',
      error: error.message,
      duration: duration.toFixed(2)
    };
  }
}

/**
 * Start processing a job in the background
 */
export function startJobProcessing(jobId) {
  console.log('Starting job processing for job ID:', jobId);
  // Process job asynchronously
  processJob(jobId).catch(error => {
    logger.error(`Error in job processing for job ${jobId}:`, error);
    console.error('Job processing error:', error);
  });
}
