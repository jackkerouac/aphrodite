import { pool } from './../db.js';

// GET /api/jobs
export const getJobs = async (req, res) => {
  try {
    const jobs = await pool.query('SELECT * FROM jobs');
    res.json(jobs.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to retrieve jobs' });
  }
};

// POST /api/jobs
export const createJob = async (req, res) => {
  try {
    const { user_id, name } = req.body;
    const newJob = await pool.query(
      'INSERT INTO jobs (user_id, name) VALUES ($1, $2) RETURNING *',
      [user_id, name]
    );
    res.json(newJob.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to create job' });
  }
};

// GET /api/jobs/:id
export const getJob = async (req, res) => {
  try {
    const { id } = req.params;
    const job = await pool.query('SELECT * FROM jobs WHERE id = $1', [id]);
    if (job.rows.length === 0) {
      return res.status(404).json({ error: 'Job not found' });
    }
    res.json(job.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to retrieve job' });
  }
};

// PUT /api/jobs/:id
export const updateJob = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    const updatedJob = await pool.query(
      'UPDATE jobs SET status = $1 WHERE id = $2 RETURNING *',
      [status, id]
    );
    if (updatedJob.rows.length === 0) {
      return res.status(404).json({ error: 'Job not found' });
    }
    res.json(updatedJob.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to update job' });
  }
};

// GET /api/jobs/:id/items
export const getJobItems = async (req, res) => {
  try {
    const { id } = req.params;
    const jobItems = await pool.query('SELECT * FROM job_items WHERE job_id = $1', [id]);
    res.json(jobItems.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to retrieve job items' });
  }
};