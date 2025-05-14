import { pool as db } from '../../db.js';
import UnifiedPosterProcessor from './unifiedPosterProcessor.js';
import logger from '../../lib/logger.js';

/**
 * Controller for handling badge rendering jobs
 */
class BadgeRenderingJobController {
  constructor() {
    this.posterProcessor = new UnifiedPosterProcessor();
    this.activeJobs = new Map();
  }

  /**
   * Initialize the controller
   */
  async init() {
    await this.posterProcessor.init();
    logger.info('BadgeRenderingJobController initialized');
  }

  /**
   * Start processing a job
   * @param {number} jobId - The job ID
   * @returns {Promise<Object>} - Job result
   */
  async startJob(jobId) {
    try {
      logger.info(`Starting job ${jobId}`);
      
      // Check if job already in progress
      if (this.activeJobs.has(jobId)) {
        return { error: 'Job already in progress' };
      }
      
      // Get job details
      const jobQuery = `
        SELECT j.*, u.id as user_id
        FROM jobs j
        JOIN users u ON j.user_id = u.id
        WHERE j.id = $1
      `;
      
      const jobResult = await db.query(jobQuery, [jobId]);
      
      if (jobResult.rows.length === 0) {
        return { error: 'Job not found' };
      }
      
      const job = jobResult.rows[0];
      const userId = job.user_id;
      
      // Update job status to processing
      await this.updateJobStatus(jobId, 'processing');
      
      // Get all items for this job
      const itemsQuery = `
        SELECT *
        FROM job_items
        WHERE job_id = $1
      `;
      
      const itemsResult = await db.query(itemsQuery, [jobId]);
      const items = itemsResult.rows;
      
      logger.info(`Job ${jobId}: Found ${items.length} items to process`);
      
      // Store job in active jobs map
      this.activeJobs.set(jobId, {
        jobId,
        userId,
        totalItems: items.length,
        itemsProcessed: 0,
        itemsFailed: 0,
        startTime: Date.now()
      });
      
      // Process the items
      const results = await this.posterProcessor.processInBatches(
        items,
        jobId,
        userId,
        this.updateProgress.bind(this, jobId)
      );
      
      // Update job status
      const successCount = results.filter(r => r.success).length;
      const failureCount = results.filter(r => !r.success).length;
      
      await this.updateJobStatus(jobId, 'completed', {
        itemsProcessed: successCount,
        itemsFailed: failureCount,
        completedAt: new Date()
      });
      
      // Remove from active jobs
      this.activeJobs.delete(jobId);
      
      logger.info(`Job ${jobId} completed: ${successCount} successful, ${failureCount} failed`);
      
      return {
        success: true,
        jobId,
        itemsProcessed: successCount,
        itemsFailed: failureCount,
        totalItems: items.length
      };
    } catch (error) {
      logger.error(`Error processing job ${jobId}: ${error.message}`);
      
      // Update job status to failed
      await this.updateJobStatus(jobId, 'failed');
      
      // Remove from active jobs
      this.activeJobs.delete(jobId);
      
      return { error: error.message };
    }
  }

  /**
   * Update job progress
   * @param {number} jobId - The job ID
   * @param {Object} progress - Progress information
   */
  async updateProgress(jobId, progress) {
    try {
      // Update active job tracking
      const jobInfo = this.activeJobs.get(jobId);
      
      if (jobInfo) {
        jobInfo.itemsProcessed = progress.completed;
        jobInfo.itemsFailed = progress.failed;
        
        // Update job in database
        await this.updateJobStatus(jobId, 'processing', {
          itemsProcessed: progress.completed,
          itemsFailed: progress.failed
        });
        
        logger.info(`Job ${jobId} progress: ${progress.completed}/${progress.total} (${progress.progress}%)`);
      }
    } catch (error) {
      logger.error(`Error updating job progress: ${error.message}`);
    }
  }

  /**
   * Update job status in the database
   * @param {number} jobId - The job ID
   * @param {string} status - New status
   * @param {Object} additionalData - Additional data to update
   */
  async updateJobStatus(jobId, status, additionalData = {}) {
    try {
      const { itemsProcessed, itemsFailed, completedAt } = additionalData;
      
      let query = 'UPDATE jobs SET status = $1';
      const params = [status];
      let paramIndex = 2;
      
      if (itemsProcessed !== undefined) {
        query += `, items_processed = $${paramIndex}`;
        params.push(itemsProcessed);
        paramIndex++;
      }
      
      if (itemsFailed !== undefined) {
        query += `, items_failed = $${paramIndex}`;
        params.push(itemsFailed);
        paramIndex++;
      }
      
      if (completedAt) {
        query += `, completed_at = $${paramIndex}`;
        params.push(completedAt);
        paramIndex++;
      }
      
      query += `, updated_at = CURRENT_TIMESTAMP WHERE id = $${paramIndex}`;
      params.push(jobId);
      
      await db.query(query, params);
    } catch (error) {
      logger.error(`Error updating job status: ${error.message}`);
    }
  }

  /**
   * Get job status
   * @param {number} jobId - The job ID
   * @returns {Promise<Object>} - Job status
   */
  async getJobStatus(jobId) {
    try {
      // Check if job is active
      if (this.activeJobs.has(jobId)) {
        const activeJob = this.activeJobs.get(jobId);
        
        return {
          jobId,
          status: 'processing',
          progress: Math.round((activeJob.itemsProcessed / activeJob.totalItems) * 100),
          itemsProcessed: activeJob.itemsProcessed,
          itemsFailed: activeJob.itemsFailed,
          totalItems: activeJob.totalItems,
          elapsedTime: Date.now() - activeJob.startTime
        };
      }
      
      // Get job from database
      const query = `
        SELECT id, status, items_processed, items_failed, items_total,
               created_at, updated_at, completed_at
        FROM jobs
        WHERE id = $1
      `;
      
      const result = await db.query(query, [jobId]);
      
      if (result.rows.length === 0) {
        return { error: 'Job not found' };
      }
      
      const job = result.rows[0];
      
      return {
        jobId: job.id,
        status: job.status,
        progress: job.items_total > 0 ? Math.round((job.items_processed / job.items_total) * 100) : 0,
        itemsProcessed: job.items_processed,
        itemsFailed: job.items_failed,
        totalItems: job.items_total,
        createdAt: job.created_at,
        updatedAt: job.updated_at,
        completedAt: job.completed_at
      };
    } catch (error) {
      logger.error(`Error getting job status: ${error.message}`);
      return { error: error.message };
    }
  }

  /**
   * Cancel a job
   * @param {number} jobId - The job ID
   * @returns {Promise<Object>} - Result
   */
  async cancelJob(jobId) {
    try {
      logger.info(`Cancelling job ${jobId}`);
      
      // Check if job is active
      if (this.activeJobs.has(jobId)) {
        // Note: In a real implementation, we would need to signal to the running process to stop
        // For now, we'll just mark it as cancelled
        this.activeJobs.delete(jobId);
      }
      
      // Update job status to cancelled
      await this.updateJobStatus(jobId, 'cancelled');
      
      return { success: true, message: 'Job cancelled' };
    } catch (error) {
      logger.error(`Error cancelling job: ${error.message}`);
      return { error: error.message };
    }
  }
}

// Singleton instance
const jobController = new BadgeRenderingJobController();

export default jobController;
