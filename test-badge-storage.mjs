/**
 * Test script to verify badge image storage is working correctly
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

// Test dummy image path (any small image will do)
const dummyImagePath = path.join(__dirname, 'src', 'assets', 'posters', 'dummy_poster_light.png');

async function testBadgeStorage() {
  const client = new Client(dbConfig);
  
  try {
    // Connect to the database
    await client.connect();
    console.log('✅ Connected to database');
    
    // Check if audio_badge_settings table exists
    const tableCheck = await client.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'audio_badge_settings'
      );
    `);
    
    if (!tableCheck.rows[0].exists) {
      console.error('❌ audio_badge_settings table does not exist');
      return;
    }
    
    console.log('✅ audio_badge_settings table exists');
    
    // Check if badge_image column exists
    const columnCheck = await client.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'audio_badge_settings'
        AND column_name = 'badge_image'
      );
    `);
    
    if (!columnCheck.rows[0].exists) {
      console.error('❌ badge_image column does not exist in audio_badge_settings table');
      return;
    }
    
    console.log('✅ badge_image column exists in audio_badge_settings table');
    
    // Check if we have settings for user 1
    const userCheck = await client.query(`
      SELECT * FROM audio_badge_settings
      WHERE user_id = 1;
    `);
    
    if (userCheck.rows.length === 0) {
      console.log('⚠️ No settings found for user ID 1, creating default settings');
      
      // Create default settings
      await client.query(`
        INSERT INTO audio_badge_settings (
          user_id, size, margin, position, audio_codec_type,
          background_color, background_transparency, 
          border_radius, border_width, border_color, border_transparency,
          shadow_toggle, shadow_color, shadow_blur_radius, shadow_offset_x, shadow_offset_y,
          z_index
        ) VALUES (
          1, 100, 10, 'top-right', 'dolby_atmos',
          '#000000', 0.8, 
          4, 1, '#ffffff', 0.8,
          FALSE, '#000000', 5, 0, 0,
          1
        );
      `);
      
      console.log('✅ Created default settings for user ID 1');
    } else {
      console.log('✅ Found settings for user ID 1');
    }
    
    // Read test image
    let imageBuffer;
    try {
      imageBuffer = fs.readFileSync(dummyImagePath);
      console.log(`✅ Read test image from ${dummyImagePath}, size: ${imageBuffer.length} bytes`);
    } catch (err) {
      console.error(`❌ Error reading test image from ${dummyImagePath}: ${err.message}`);
      return;
    }
    
    // Save test image to database
    await client.query(`
      UPDATE audio_badge_settings
      SET badge_image = $1,
          last_generated_at = CURRENT_TIMESTAMP
      WHERE user_id = 1;
    `, [imageBuffer]);
    
    console.log('✅ Saved test image to database for user ID 1');
    
    // Read the image back to confirm it was saved correctly
    const imageCheck = await client.query(`
      SELECT badge_image
      FROM audio_badge_settings
      WHERE user_id = 1;
    `);
    
    if (!imageCheck.rows[0] || !imageCheck.rows[0].badge_image) {
      console.error('❌ Failed to retrieve test image from database');
      return;
    }
    
    const retrievedImage = imageCheck.rows[0].badge_image;
    console.log(`✅ Retrieved test image from database, size: ${retrievedImage.length} bytes`);
    
    // Compare image sizes
    if (imageBuffer.length === retrievedImage.length) {
      console.log('✅ TEST PASSED: Image sizes match');
    } else {
      console.error(`❌ TEST FAILED: Image sizes don't match. Original: ${imageBuffer.length}, Retrieved: ${retrievedImage.length}`);
    }
    
    // Save the retrieved image to verify visually if needed
    const outputPath = path.join(__dirname, 'test-output-badge.png');
    fs.writeFileSync(outputPath, retrievedImage);
    console.log(`✅ Saved retrieved image to ${outputPath} for visual verification`);
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    // Close database connection
    await client.end();
    console.log('🔌 Database connection closed');
  }
}

// Run the test
testBadgeStorage().catch(console.error);
