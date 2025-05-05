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

async function testDatabaseConnection() {
  try {
    console.log('Testing database connection...');
    console.log('Connection parameters:');
    console.log(`  Host: ${process.env.PG_HOST || 'localhost'}`);
    console.log(`  Database: ${process.env.PG_DATABASE || 'aphrodite'}`);
    console.log(`  User: ${process.env.PG_USER || 'aphrodite'}`);
    console.log(`  Port: ${process.env.PG_PORT || 5432}`);
    console.log('Connecting...');
    
    // Test connection
    const res = await pool.query('SELECT NOW()');
    console.log('Connection successful!');
    console.log(`Current database time: ${res.rows[0].now}`);
    
    // Test for tables existence
    console.log('\nChecking for required tables...');
    
    const tables = [
      'users',
      'jellyfin_settings',
      'omdb_settings',
      'tmdb_settings',
      'tvdb_settings'
    ];
    
    for (const table of tables) {
      const tableCheck = await pool.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public' 
          AND table_name = $1
        )
      `, [table]);
      
      if (tableCheck.rows[0].exists) {
        console.log(`  ✅ Table '${table}' exists`);
      } else {
        console.log(`  ❌ Table '${table}' does not exist`);
      }
    }
    
    // Check for test user
    console.log('\nChecking for test user...');
    const userCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM users WHERE id = 1
      )
    `);
    
    if (userCheck.rows[0].exists) {
      const user = await pool.query('SELECT id, username, email FROM users WHERE id = 1');
      console.log(`  ✅ Test user exists: ${user.rows[0].username} (${user.rows[0].email})`);
    } else {
      console.log('  ❌ Test user does not exist');
    }
    
    console.log('\nDatabase check complete.');
  } catch (error) {
    console.error('Database connection error:', error);
    console.log('\nTroubleshooting tips:');
    console.log('1. Make sure PostgreSQL is running');
    console.log('2. Check that your database credentials in .env file are correct');
    console.log('3. Ensure the database "aphrodite" exists');
    console.log('4. Confirm the user has proper permissions');
    console.log('\nTo create the required database and user, follow these steps:');
    console.log('1. Connect to PostgreSQL: psql -U postgres');
    console.log('2. Create the database: CREATE DATABASE aphrodite;');
    console.log('3. Create the user: CREATE USER aphrodite WITH ENCRYPTED PASSWORD \'aphrodite_secure_password\';');
    console.log('4. Grant privileges: GRANT ALL PRIVILEGES ON DATABASE aphrodite TO aphrodite;');
    console.log('5. Exit psql and run the setup script: npm run setup-db');
  } finally {
    await pool.end();
  }
}

testDatabaseConnection();
