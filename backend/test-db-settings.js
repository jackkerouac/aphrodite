import pkg from 'pg';
const { Pool } = pkg;
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

async function checkDatabaseSettings() {
  try {
    // Check Jellyfin settings in the database
    console.log('Checking database settings...\n');
    
    const query = 'SELECT * FROM jellyfin_settings';
    const result = await pool.query(query);
    
    if (result.rows.length > 0) {
      const settings = result.rows[0];
      console.log('Jellyfin Settings from Database:');
      console.log(`URL: ${settings.url}`);
      console.log(`Token: ${settings.token}`);
      console.log(`Token Length: ${settings.token ? settings.token.length : 0}`);
      
      // Show first and last few characters of the token
      if (settings.token) {
        console.log(`Token preview: ${settings.token.slice(0, 8)}...${settings.token.slice(-8)}`);
      }
      
      // Check if this matches our working API key
      const workingKey = 'd66524acc5d544d591e0cbbabff6053c';
      if (settings.token === workingKey) {
        console.log('\n✓ Database token matches the working API key!');
      } else {
        console.log('\n✗ Database token does NOT match the working API key!');
        console.log(`Working key: ${workingKey}`);
        console.log(`DB key:      ${settings.token}`);
      }
    } else {
      console.log('No Jellyfin settings found in database');
    }
    
  } catch (error) {
    console.error('Error checking settings:', error);
  } finally {
    await pool.end();
  }
}

// Run the check
checkDatabaseSettings();
