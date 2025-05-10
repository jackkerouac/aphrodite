import { pool } from '../db.js';
import logger from '../lib/logger.js';
import { getJobById, updateJobStatus, updateJobItemStatus } from '../models/jobs.js';
import { emitToUser } from '../lib/websocket.js';
import PosterProcessor from './badge-renderer/posterProcessor.js';

/**
 * Process a job and apply badges to all items
 */
export async function processJob(jobId) {
  try {
    const job = await getJobById(jobId);
    if (!job) {
      logger.error(`Job ${jobId} not found`);
      return;
    }

    logger.info(`Starting job ${jobId} processing`);
    await updateJobStatus(jobId, 'running');

    // Initialize poster processor
    const posterProcessor = new PosterProcessor();
    await posterProcessor.init();

    // Get job items
    const itemsResult = await pool.query(
      'SELECT ji.*, li.title, li.jellyfin_id, li.media_type 
       FROM job_items ji
       JOIN library_items li ON ji.library_item_id = li.id
       WHERE ji.job_id = $1 
       ORDER BY ji.id',
      [jobId]
    );
    const items = itemsResult.rows;

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
    const finalStatus = failedCount === items.length ? 'failed' : 'completed';

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

    logger.info(`Job ${jobId} completed. Processed: ${processedCount}, Failed: ${failedCount}`);
  } catch (error) {
    logger.error(`Fatal error processing job ${jobId}:`, error);
    await updateJobStatus(jobId, 'failed');

    // Emit job error event
    const job = await getJobById(jobId);
    if (job) {
      emitToUser(job.user_id, 'job-error', {
        jobId,
        error: error.message
      });
    }
  }
}

/**
 * Start processing a job in the background
 */
export function startJobProcessing(jobId) {
  // Process job asynchronously
  processJob(jobId).catch(error => {
    logger.error(`Error in job processing for job ${jobId}:`, error);
  });
}
