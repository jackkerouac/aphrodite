import { pool } from '../db.js';

// Get all jobs with pagination
export async function getJobs(userId, page = 1, limit = 10) {
  const offset = (page - 1) * limit;
  
  const countResult = await pool.query(
    'SELECT COUNT(*) FROM jobs WHERE user_id = $1',
    [userId]
  );
  
  const result = await pool.query(
    `SELECT *
     FROM jobs
     WHERE user_id = $1
     ORDER BY created_at DESC
     LIMIT $2 OFFSET $3`,
    [userId, limit, offset]
  );
  
  return {
    jobs: result.rows,
    total: parseInt(countResult.rows[0].count),
    page,
    limit,
    totalPages: Math.ceil(parseInt(countResult.rows[0].count) / limit)
  };
}

// Get a specific job by ID
export async function getJobById(jobId, userId) {
  const result = await pool.query(
    'SELECT * FROM jobs WHERE id = $1 AND user_id = $2',
    [jobId, userId]
  );
  
  return result.rows[0] || null;
}

// Create a new job
export async function createJob(jobData) {
  const { user_id, name, items_total } = jobData;
  
  try {
    console.log('Creating job with data:', { user_id, name, items_total });
    
    const result = await pool.query(
      `INSERT INTO jobs (user_id, name, items_total, status)
       VALUES ($1, $2, $3, 'pending')
       RETURNING *`,
      [user_id, name, items_total]
    );
    
    console.log('Job created successfully:', result.rows[0]);
    return result.rows[0];
  } catch (error) {
    console.error('Database error in createJob:', error);
    throw error;
  }
}

// Update job status
export async function updateJobStatus(jobId, status, updatedData = {}) {
  let query = 'UPDATE jobs SET status = $1, updated_at = NOW()';
  const params = [status];
  let paramIndex = 2;
  
  if (status === 'completed') {
    query += ', completed_at = NOW()';
  }
  
  if (updatedData.items_processed !== undefined) {
    query += `, items_processed = $${paramIndex}`;
    params.push(updatedData.items_processed);
    paramIndex++;
  }
  
  if (updatedData.items_failed !== undefined) {
    query += `, items_failed = $${paramIndex}`;
    params.push(updatedData.items_failed);
    paramIndex++;
  }
  
  query += ` WHERE id = $${paramIndex} RETURNING *`;
  params.push(jobId);
  
  const result = await pool.query(query, params);
  return result.rows[0];
}

// Get job items for a specific job
export async function getJobItems(jobId, page = 1, limit = 50) {
  const offset = (page - 1) * limit;
  
  const countResult = await pool.query(
    'SELECT COUNT(*) FROM job_items WHERE job_id = $1',
    [jobId]
  );
  
  const result = await pool.query(
    `SELECT *
     FROM job_items
     WHERE job_id = $1
     ORDER BY created_at ASC
     LIMIT $2 OFFSET $3`,
    [jobId, limit, offset]
  );
  
  return {
    items: result.rows,
    total: parseInt(countResult.rows[0].count),
    page,
    limit,
    totalPages: Math.ceil(parseInt(countResult.rows[0].count) / limit)
  };
}

// Create job items
export async function createJobItems(jobId, items) {
  if (!items.length) return [];
  
  try {
    console.log('Creating job items for job:', jobId);
    console.log('Items to create:', items);
    
    const values = items.map((item, index) => {
      const offset = index * 3;
      return `($${offset + 1}, $${offset + 2}, $${offset + 3})`;
    }).join(', ');
    
    const params = items.flatMap(item => [jobId, item.jellyfin_item_id, item.title]);
    
    const query = `
      INSERT INTO job_items (job_id, jellyfin_item_id, title)
      VALUES ${values}
      RETURNING *`;
    
    console.log('Query:', query);
    console.log('Params:', params);
    
    const result = await pool.query(query, params);
    console.log('Job items created successfully:', result.rows.length);
    return result.rows;
  } catch (error) {
    console.error('Database error in createJobItems:', error);
    throw error;
  }
}

// Update job item status
export async function updateJobItemStatus(itemId, status, errorMessage = null) {
  const query = errorMessage 
    ? `UPDATE job_items 
       SET status = $1, error_message = $2, updated_at = NOW()
       WHERE id = $3
       RETURNING *`
    : `UPDATE job_items 
       SET status = $1, updated_at = NOW()
       WHERE id = $2
       RETURNING *`;
  
  const params = errorMessage ? [status, errorMessage, itemId] : [status, itemId];
  
  const result = await pool.query(query, params);
  return result.rows[0];
}
