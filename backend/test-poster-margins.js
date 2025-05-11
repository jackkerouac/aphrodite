import pg from 'pg';
const { Pool } = pg;
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
config({ path: join(dirname(__dirname), '.env') });

// Create connection pool
const pool = new Pool({
  host: process.env.PG_HOST,
  port: process.env.PG_PORT,
  database: process.env.PG_DATABASE,
  user: process.env.PG_USER,
  password: process.env.PG_PASSWORD
});

async function checkBadgeSettings() {
  try {
    console.log('Checking badge settings in database...\n');
    
    // Check resolution badge settings
    const resolutionQuery = `
      SELECT 
        margin,
        position,
        size
      FROM resolution_badge_settings
      WHERE user_id = 1 AND enabled = true
    `;
    const resolutionResult = await pool.query(resolutionQuery);
    console.log('Resolution badge settings:');
    console.log(resolutionResult.rows[0]);
    
    // Check audio badge settings  
    const audioQuery = `
      SELECT 
        margin,
        position,
        size
      FROM audio_badge_settings
      WHERE user_id = 1 AND enabled = true
    `;
    const audioResult = await pool.query(audioQuery);
    console.log('\nAudio badge settings:');
    console.log(audioResult.rows[0]);
    
    // Check review badge settings
    const reviewQuery = `
      SELECT 
        margin,
        position,
        size
      FROM review_badge_settings
      WHERE user_id = 1 AND enabled = true
    `;
    const reviewResult = await pool.query(reviewQuery);
    console.log('\nReview badge settings:');
    console.log(reviewResult.rows[0]);
    
  } catch (error) {
    console.error('Error checking settings:', error);
  } finally {
    await pool.end();
  }
}

// Run the check
checkBadgeSettings();
