import express from 'express';
import pg from 'pg';

const { Pool } = pg;
const router = express.Router();

// Health check endpoint
router.get('/', async (req, res) => {
  try {
    // Basic health check
    const health = {
      status: 'UP',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0'
    };

    // Check database connection
    const pool = new Pool({
      user: process.env.PG_USER,
      host: process.env.PG_HOST,
      database: process.env.PG_DATABASE,
      password: process.env.PG_PASSWORD,
      port: process.env.PG_PORT,
    });

    try {
      const result = await pool.query('SELECT NOW()');
      health.database = {
        status: 'UP',
        timestamp: result.rows[0].now
      };
    } catch (dbError) {
      health.database = {
        status: 'DOWN',
        error: dbError.message
      };
      health.status = 'DEGRADED';
    } finally {
      await pool.end();
    }

    res.status(health.status === 'UP' ? 200 : 503).json(health);
  } catch (error) {
    res.status(503).json({
      status: 'DOWN',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

export default router;
