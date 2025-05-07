/**
 * Script to run the database migration for adding badge image fields
 * ES Module version
 */

import pkg from 'pg';
const { Client } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Get directory name in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// PostgreSQL connection details
const dbConfig = {
  user: process.env.PG_USER || 'aphrodite',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DATABASE || 'aphrodite',
  password: process.env.PG_PASSWORD || 'aphrodite_secure_password',
  port: process.env.PG_PORT || 5432,
};

console.log('💾 Database connection config:', {
  ...dbConfig,
  password: '***', // Don't log the actual password
});

// Path to migration file
const migrationFile = path.join(__dirname, 'backend', 'migrations', '20250507_add_badge_image_fields.sql');

async function runMigration() {
  const client = new Client(dbConfig);
  
  try {
    // Read migration SQL
    const sql = fs.readFileSync(migrationFile, 'utf8');
    
    console.log(`📃 Read migration file: ${migrationFile}`);
    
    // Connect to the database
    await client.connect();
    console.log('✅ Connected to database');
    
    // Execute the migration
    console.log('🔄 Running migration...');
    await client.query(sql);
    console.log('✅ Migration completed successfully');
    
    // Record the migration in the migrations table if it exists
    try {
      // Check if migrations table exists
      const checkTableResult = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public' 
          AND table_name = 'migrations'
        );
      `);
      
      if (checkTableResult.rows[0].exists) {
        // Record the migration
        await client.query(`
          INSERT INTO migrations (name, applied_at)
          VALUES ($1, CURRENT_TIMESTAMP)
          ON CONFLICT (name) DO NOTHING;
        `, [path.basename(migrationFile)]);
        console.log('✅ Migration recorded in migrations table');
      }
    } catch (err) {
      console.log('ℹ️ No migrations table found or could not record migration');
    }
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    // Close database connection
    await client.end();
    console.log('🔌 Database connection closed');
  }
}

// Run the migration
runMigration().catch(console.error);
