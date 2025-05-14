import express from 'express';
import { pool as db } from '../db.js';
import jobController from '../services/unified-badge-renderer/jobController.js';
import logger from '../lib/logger.js';

const router = express.Router();

// Initialize the job controller
jobController.init().catch(error => {
  logger.error(`Failed to initialize job controller: ${error.message}`);
});

/**
 * @route POST /api/unified-badge-render/jobs
 * @desc Create a new badge rendering job
 * @access Private
 */
router.post('/jobs', async (req, res) => {
  try {
    const userId = req.query.user_id || '1';
    const { items, name } = req.body;
    
    // Validate input
    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'Invalid or empty items list' });
    }
    
    // Create a new job
    const jobQuery = `
      INSERT INTO jobs (user_id, name, status, items_total, items_processed, items_failed, created_at, updated_at)
      VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      RETURNING id
    `;
    
    const jobValues = [
      userId,
      name || 'Badge Rendering Job',
      'pending',
      items.length,
      0,
      0
    ];
    
    const jobResult = await db.query(jobQuery, jobValues);
    const jobId = jobResult.rows[0].id;
    
    // Create job items
    const itemInsertPromises = items.map(item => {
      const itemQuery = `
        INSERT INTO job_items (job_id, jellyfin_item_id, title, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      `;
      
      const itemValues = [
        jobId,
        item.jellyfin_item_id,
        item.title || 'Unknown',
        'pending'
      ];
      
      return db.query(itemQuery, itemValues);
    });
    
    await Promise.all(itemInsertPromises);
    
    logger.info(`Created job ${jobId} with ${items.length} items for user ${userId}`);
    
    // Return the job ID
    res.status(201).json({
      message: 'Job created successfully',
      jobId
    });
    
    // Start the job asynchronously
    jobController.startJob(jobId).catch(error => {
      logger.error(`Error starting job ${jobId}: ${error.message}`);
    });
  } catch (error) {
    logger.error(`Error creating job: ${error.message}`);
    res.status(500).json({ error: 'Failed to create job' });
  }
});

/**
 * @route GET /api/unified-badge-render/jobs/:id
 * @desc Get job status
 * @access Private
 */
router.get('/jobs/:id', async (req, res) => {
  try {
    const jobId = parseInt(req.params.id);
    const userId = req.query.user_id || '1';
    
    // Verify job belongs to user
    const verifyQuery = `
      SELECT id FROM jobs WHERE id = $1 AND user_id = $2
    `;
    
    const verifyResult = await db.query(verifyQuery, [jobId, userId]);
    
    if (verifyResult.rows.length === 0) {
      return res.status(404).json({ error: 'Job not found' });
    }
    
    // Get job status
    const status = await jobController.getJobStatus(jobId);
    
    res.json(status);
  } catch (error) {
    logger.error(`Error getting job status: ${error.message}`);
    res.status(500).json({ error: 'Failed to get job status' });
  }
});

/**
 * @route DELETE /api/unified-badge-render/jobs/:id
 * @desc Cancel a job
 * @access Private
 */
router.delete('/jobs/:id', async (req, res) => {
  try {
    const jobId = parseInt(req.params.id);
    const userId = req.query.user_id || '1';
    
    // Verify job belongs to user
    const verifyQuery = `
      SELECT id FROM jobs WHERE id = $1 AND user_id = $2
    `;
    
    const verifyResult = await db.query(verifyQuery, [jobId, userId]);
    
    if (verifyResult.rows.length === 0) {
      return res.status(404).json({ error: 'Job not found' });
    }
    
    // Cancel the job
    const result = await jobController.cancelJob(jobId);
    
    if (result.error) {
      return res.status(500).json({ error: result.error });
    }
    
    res.json({ message: 'Job cancelled successfully' });
  } catch (error) {
    logger.error(`Error cancelling job: ${error.message}`);
    res.status(500).json({ error: 'Failed to cancel job' });
  }
});

/**
 * @route GET /api/unified-badge-render/jobs
 * @desc Get all jobs for the user
 * @access Private
 */
router.get('/jobs', async (req, res) => {
  try {
    const userId = req.query.user_id || '1';
    
    // Get all jobs for the user
    const query = `
      SELECT id, name, status, items_total, items_processed, items_failed,
             created_at, updated_at, completed_at
      FROM jobs
      WHERE user_id = $1
      ORDER BY created_at DESC
    `;
    
    const result = await db.query(query, [userId]);
    
    res.json(result.rows);
  } catch (error) {
    logger.error(`Error getting jobs: ${error.message}`);
    res.status(500).json({ error: 'Failed to get jobs' });
  }
});

export default router;
