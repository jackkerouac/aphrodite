import { pool } from './db.js';
import fs from 'fs';
import path from 'path';
import logger from './lib/logger.js';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function applyMigration() {
  try {
    logger.info('Starting unified_badge_settings table migration...');

    // Read the SQL file
    const sqlPath = path.join(__dirname, 'migrations', 'new', 'create_unified_badge_settings_table.sql');
    const sql = fs.readFileSync(sqlPath, 'utf8');

    // Apply the migration
    await pool.query(sql);

    logger.info('Migration completed successfully!');
    process.exit(0);
  } catch (error) {
    logger.error(`Migration failed: ${error.message}`);
    process.exit(1);
  }
}

// Run the migration
applyMigration();
