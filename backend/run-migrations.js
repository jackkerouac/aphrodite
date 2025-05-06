import { pool } from './db.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './lib/logger.js';

// Get the current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define migrations directory
const migrationsDir = path.join(__dirname, 'migrations');

// Function to run a single migration file
async function runMigration(filePath) {
  const sql = fs.readFileSync(filePath, 'utf8');
  logger.info(`Running migration: ${path.basename(filePath)}`);
  
  try {
    await pool.query(sql);
    logger.info(`✅ Successfully ran migration: ${path.basename(filePath)}`);
    return true;
  } catch (error) {
    logger.error(`❌ Error running migration ${path.basename(filePath)}: ${error.message}`);
    return false;
  }
}

// Function to run all migrations
async function runAllMigrations() {
  try {
    // Create migrations table if it doesn't exist
    await pool.query(`
      CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // Get all SQL files in the migrations directory
    const files = fs.readdirSync(migrationsDir)
      .filter(file => file.endsWith('.sql'))
      .sort(); // Sort to ensure migrations run in order by filename
    
    if (files.length === 0) {
      logger.info('No migration files found');
      return;
    }
    
    // Get already applied migrations
    const { rows: appliedMigrations } = await pool.query('SELECT name FROM migrations');
    const appliedMigrationNames = appliedMigrations.map(m => m.name);
    
    // Filter out already applied migrations
    const pendingMigrations = files.filter(file => !appliedMigrationNames.includes(file));
    
    if (pendingMigrations.length === 0) {
      logger.info('All migrations have already been applied');
      return;
    }
    
    logger.info(`Found ${pendingMigrations.length} pending migrations`);
    
    // Run each pending migration
    for (const file of pendingMigrations) {
      const filePath = path.join(migrationsDir, file);
      const success = await runMigration(filePath);
      
      if (success) {
        // Record successful migration
        await pool.query('INSERT INTO migrations (name) VALUES ($1)', [file]);
        logger.info(`Recorded migration: ${file}`);
      } else {
        logger.error(`Failed to apply migration: ${file}`);
        // Stop processing further migrations after a failure
        break;
      }
    }
    
    logger.info('Migration process completed');
  } catch (error) {
    logger.error(`Error in migration process: ${error.message}`);
  } finally {
    await pool.end();
  }
}

// Run migrations
runAllMigrations();
