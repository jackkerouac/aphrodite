import express from 'express';
import {
  getJobs,
  getJobById,
  createJob,
  updateJobStatus,
  getJobItems,
  createJobItems
} from '../models/jobs.js';
import logger from '../lib/logger.js';

const router = express.Router();

/**
 * @route GET /api/jobs
 * @description Get all jobs for a user with pagination
 * @query {number} userId - User ID
 * @query {number} page - Page number (default: 1)
 * @query {number} limit - Items per page (default: 10)
 */
router.get('/', async (req, res) => {
  try {
    const { userId, page = 1, limit = 10 } = req.query;
    
    if (!userId) {
      return res.status(400).json({ message: 'User ID is required' });
    }
    
    const result = await getJobs(parseInt(userId), parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    logger.error('Error fetching jobs:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

/**
 * @route POST /api/jobs
 * @description Create a new job
 * @body {number} user_id - User ID
 * @body {string} name - Job name
 * @body {Array} items - Array of items to process
 */
router.post('/', async (req, res) => {
  try {
    const { user_id, name, items } = req.body;
    
    if (!user_id || !name || !items || !Array.isArray(items)) {
      return res.status(400).json({ message: 'Missing required fields' });
    }
    
    // Create the job
    const job = await createJob({
      user_id,
      name,
      items_total: items.length
    });
    
    // Create job items
    if (items.length > 0) {
      await createJobItems(job.id, items);
    }
    
    res.status(201).json(job);
  } catch (error) {
    logger.error('Error creating job:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

/**
 * @route GET /api/jobs/:id
 * @description Get a specific job by ID
 * @param {number} id - Job ID
 * @query {number} userId - User ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { userId } = req.query;
    
    if (!userId) {
      return res.status(400).json({ message: 'User ID is required' });
    }
    
    const job = await getJobById(parseInt(id), parseInt(userId));
    
    if (!job) {
      return res.status(404).json({ message: 'Job not found' });
    }
    
    res.json(job);
  } catch (error) {
    logger.error('Error fetching job:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

/**
 * @route PUT /api/jobs/:id
 * @description Update job status
 * @param {number} id - Job ID
 * @body {string} status - New status
 * @body {number} items_processed - Number of items processed
 * @body {number} items_failed - Number of items failed
 */
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { status, items_processed, items_failed } = req.body;
    
    if (!status) {
      return res.status(400).json({ message: 'Status is required' });
    }
    
    const validStatuses = ['pending', 'running', 'completed', 'failed'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ 
        message: 'Invalid status. Must be one of: ' + validStatuses.join(', ') 
      });
    }
    
    const updatedData = {};
    if (items_processed !== undefined) updatedData.items_processed = items_processed;
    if (items_failed !== undefined) updatedData.items_failed = items_failed;
    
    const job = await updateJobStatus(parseInt(id), status, updatedData);
    
    if (!job) {
      return res.status(404).json({ message: 'Job not found' });
    }
    
    res.json(job);
  } catch (error) {
    logger.error('Error updating job:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

/**
 * @route GET /api/jobs/:id/items
 * @description Get job items for a specific job
 * @param {number} id - Job ID
 * @query {number} page - Page number (default: 1)
 * @query {number} limit - Items per page (default: 50)
 */
router.get('/:id/items', async (req, res) => {
  try {
    const { id } = req.params;
    const { page = 1, limit = 50 } = req.query;
    
    const result = await getJobItems(parseInt(id), parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    logger.error('Error fetching job items:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Job status update handler for background processing
// This would be called by the image processing service
router.post('/update-status', async (req, res) => {
  try {
    const { jobId, status, itemId, itemStatus, errorMessage } = req.body;
    
    // Update specific item status if provided
    if (itemId && itemStatus) {
      const { updateJobItemStatus } = await import('../models/jobs.js');
      await updateJobItemStatus(itemId, itemStatus, errorMessage);
    }
    
    // Update overall job status if provided
    if (jobId && status) {
      await updateJobStatus(jobId, status);
    }
    
    res.json({ success: true });
  } catch (error) {
    logger.error('Error updating job/item status:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

/**
 * @route POST /api/jobs/:id/process
 * @description Start processing a job
 * @param {number} id - Job ID
 */
router.post('/:id/process', async (req, res) => {
  try {
    const { id } = req.params;
    const { processJob } = await import('../services/jobProcessor.js');
    
    // Start processing the job asynchronously
    processJob(parseInt(id)).catch(error => {
      logger.error(`Error in job processing for job ${id}:`, error);
    });
    
    res.json({ message: 'Job processing started', jobId: id });
  } catch (error) {
    logger.error('Error starting job processing:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
