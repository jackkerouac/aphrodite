import dotenv from 'dotenv';
import pg from 'pg';
const { Pool } = pg;

// Load environment variables
dotenv.config();

// Database connection
const pool = new Pool({
  user: process.env.PG_USER || 'aphrodite',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DATABASE || 'aphrodite',
  password: process.env.PG_PASSWORD || 'aphrodite_secure_password',
  port: process.env.PG_PORT || 5432,
});

// Create the necessary tables if they don't exist
async function createTables() {
  try {
    console.log('Creating database tables if they don\'t exist...');
    
    // Start a transaction
    await pool.query('BEGIN');
    
    // Check if users table exists, create it if not
    const usersCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'users'
      )
    `);
    
    if (!usersCheck.rows[0].exists) {
      console.log('Creating users table...');
      await pool.query(`
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Insert a test user
      await pool.query(`
        INSERT INTO users (id, username, email, password_hash) 
        VALUES (1, 'testuser', 'test@example.com', 'hashed_password') 
        ON CONFLICT (id) DO NOTHING
      `);
    }
    
    // Create the update_modified_column function if it doesn't exist
    const functionCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM pg_proc 
        WHERE proname = 'update_modified_column'
      )
    `);
    
    if (!functionCheck.rows[0].exists) {
      console.log('Creating update_modified_column function...');
      await pool.query(`
        CREATE OR REPLACE FUNCTION update_modified_column()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated_at = now();
           RETURN NEW;
        END;
        $$ language 'plpgsql'
      `);
    }
    
    // Create jellyfin_settings table if it doesn't exist
    const jellyfinCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'jellyfin_settings'
      )
    `);
    
    if (!jellyfinCheck.rows[0].exists) {
      console.log('Creating jellyfin_settings table...');
      await pool.query(`
        CREATE TABLE jellyfin_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            jellyfin_url VARCHAR(255) NOT NULL,
            jellyfin_api_key VARCHAR(255) NOT NULL,
            jellyfin_user_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
      `);
      
      await pool.query(`
        CREATE TRIGGER update_jellyfin_settings_modtime
        BEFORE UPDATE ON jellyfin_settings
        FOR EACH ROW EXECUTE FUNCTION update_modified_column()
      `);
    }
    
    // Create omdb_settings table if it doesn't exist
    const omdbCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'omdb_settings'
      )
    `);
    
    if (!omdbCheck.rows[0].exists) {
      console.log('Creating omdb_settings table...');
      await pool.query(`
        CREATE TABLE omdb_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            api_key VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
      `);
      
      await pool.query(`
        CREATE TRIGGER update_omdb_settings_modtime
        BEFORE UPDATE ON omdb_settings
        FOR EACH ROW EXECUTE FUNCTION update_modified_column()
      `);
    }
    
    // Create tmdb_settings table if it doesn't exist
    const tmdbCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'tmdb_settings'
      )
    `);
    
    if (!tmdbCheck.rows[0].exists) {
      console.log('Creating tmdb_settings table...');
      await pool.query(`
        CREATE TABLE tmdb_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            api_key VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
      `);
      
      await pool.query(`
        CREATE TRIGGER update_tmdb_settings_modtime
        BEFORE UPDATE ON tmdb_settings
        FOR EACH ROW EXECUTE FUNCTION update_modified_column()
      `);
    }
    
    // Create tvdb_settings table if it doesn't exist
    const tvdbCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'tvdb_settings'
      )
    `);
    
    if (!tvdbCheck.rows[0].exists) {
      console.log('Creating tvdb_settings table...');
      await pool.query(`
        CREATE TABLE tvdb_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            api_key VARCHAR(255) NOT NULL,
            pin VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
      `);
      
      await pool.query(`
        CREATE TRIGGER update_tvdb_settings_modtime
        BEFORE UPDATE ON tvdb_settings
        FOR EACH ROW EXECUTE FUNCTION update_modified_column()
      `);
    }
    
    // Commit the transaction
    await pool.query('COMMIT');
    
    console.log('All tables created successfully!');
  } catch (error) {
    // Rollback the transaction in case of error
    await pool.query('ROLLBACK');
    console.error('Error creating tables:', error);
  } finally {
    // Close the pool
    await pool.end();
  }
}

// Run the function
createTables();
