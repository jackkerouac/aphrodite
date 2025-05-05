import pg from 'pg';
import dotenv from 'dotenv';
dotenv.config();

// Print DB connection info for debugging
const dbConfig = {
  user: process.env.PG_USER || 'aphrodite',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DATABASE || 'aphrodite',
  password: process.env.PG_PASSWORD ? '***' : 'aphrodite_secure_password',  // Hide actual password
  port: process.env.PG_PORT || 5432,
};

console.log('💾 Database connection config:', {
  ...dbConfig,
  password: '***', // Don't log the actual password
});

export const pool = new pg.Pool({
  user: process.env.PG_USER || 'aphrodite',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DATABASE || 'aphrodite',
  password: process.env.PG_PASSWORD || 'aphrodite_secure_password',
  port: process.env.PG_PORT || 5432,
});

// Test the connection
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Database connection error:', err);
  } else {
    console.log(`✅ Database connected successfully at ${res.rows[0].now}`);
  }
});
