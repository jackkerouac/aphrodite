import pg from 'pg';
import dotenv from 'dotenv';
dotenv.config();

export const pool = new pg.Pool({
  user: process.env.PG_USER || 'aphrodite',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DATABASE || 'aphrodite',
  password: process.env.PG_PASSWORD || 'aphrodite_secure_password',
  port: process.env.PG_PORT || 5432,
});
