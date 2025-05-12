import PosterProcessor from './services/badge-renderer/posterProcessor.js';
import fs from 'fs/promises';
import path from 'path';
import { pool as db } from './db.js';

/**
 * Test script to verify badge background colors are properly applied
 * This script will update badge settings in the database and then process posters
 */
async function testBadgeColors() {
  console.log('Testing badge background color handling...');
  
  try {
    // Create a PosterProcessor instance
    const processor = new PosterProcessor();
    await processor.init();
    
    // Use a sample poster for testing
    const tempDir = path.join(process.cwd(), 'temp');
    await fs.mkdir(tempDir, { recursive: true });
    
    const samplePosterPath = path.join(tempDir, 'test-color-poster.png');
    
    // Create a sample poster if it doesn't exist
    try {
      await fs.access(samplePosterPath);
    } catch (err) {
      // Create a basic 1000x1500 black poster
      const sharp = (await import('sharp')).default;
      await sharp({
        create: {
          width: 1000,
          height: 1500,
          channels: 4,
          background: { r: 0, g: 0, b: 0, alpha: 1 }
        }
      })
      .png()
      .toFile(samplePosterPath);
      console.log(`Created sample poster at ${samplePosterPath}`);
    }
    
    // Override database methods to provide test data for badges
    processor.getBadgeValue = (type, metadata) => {
      switch (type) {
        case 'resolution':
          return '1080p';
        case 'audio':
          return 'aac';
        case 'review':
          return metadata.scores || [];
        default:
          return null;
      }
    };
    
    processor.fetchItemMetadata = async () => {
      return {
        scores: [
          { name: 'IMDB', rating: 7.5, outOf: 10 },
          { name: 'RT', rating: 85, outOf: 100 }
        ],
        resolution: '1080p',
        audioFormat: 'aac'
      };
    };
    
    // Get the user ID for testing
    const userResult = await db.query('SELECT id FROM users LIMIT 1');
    if (userResult.rows.length === 0) {
      throw new Error('No users found in the database. Please create a user first.');
    }
    const userId = userResult.rows[0].id;
    console.log(`Using user ID ${userId} for testing`);
    
    // Update test badge settings
    await setupTestBadgeSettings(userId);
    
    // Instead of using getBadgeSettings from processor, create test badge configs directly
    const badgeConfigs = [
      // Audio badge with brand colors (should be blue)
      {
        enabled: true,
        settings: {
          type: 'audio',
          position: 'top-left',
          size: 100,
          fontFamily: 'Arial',
          textColor: '#FFFFFF',
          backgroundColor: '#000000', // This should be overridden by brand color
          use_brand_colors: true,
          borderRadius: 10,
          borderWidth: 1,
          borderColor: '#ffffff',
          borderOpacity: 0.9,
          shadowEnabled: false,
          padding: 20,
          margin: 20,
          transparency: 0.8,
          stackingOrder: 1
        },
        value: 'aac'
      },
      // Resolution badge with custom color (green)
      {
        enabled: true,
        settings: {
          type: 'resolution',
          position: 'top-right',
          size: 100,
          fontFamily: 'Arial',
          textColor: '#FFFFFF',
          backgroundColor: '#00AA00', // Custom green color
          use_brand_colors: false,
          borderRadius: 10,
          borderWidth: 1,
          borderColor: '#ffffff',
          borderOpacity: 0.9,
          shadowEnabled: false,
          padding: 20,
          margin: 20,
          transparency: 0.8,
          stackingOrder: 2
        },
        value: '1080p'
      },
      // Review badge with black background
      {
        enabled: true,
        settings: {
          type: 'review',
          position: 'bottom-left',
          size: 100,
          fontFamily: 'Arial',
          textColor: '#FFFFFF',
          backgroundColor: '#000000',
          borderRadius: 10,
          borderWidth: 1,
          borderColor: '#ffffff',
          borderOpacity: 0.9,
          shadowEnabled: false,
          padding: 20,
          margin: 20,
          transparency: 0.8,
          stackingOrder: 3,
          displayFormat: 'horizontal',
          maxSourcesToShow: 2
        },
        value: [
          { name: 'IMDB', rating: 7.5, outOf: 10 },
          { name: 'RT', rating: 85, outOf: 100 }
        ]
      }
    ];
    
    console.log('Using test badge configs:', JSON.stringify(badgeConfigs, null, 2));
    
    // Apply badges with canvas renderer
    const outputPath = path.join(tempDir, 'test-color-output.png');
    const modifiedPosterBuffer = await processor.applyBadgesWithCanvas(
      samplePosterPath, 
      badgeConfigs
    );
    
    // Save the result
    await fs.writeFile(outputPath, modifiedPosterBuffer);
    console.log(`Test completed. Output saved to ${outputPath}`);
    
    console.log('\nTest completed. Please check the output image to verify correct colors:');
    console.log('- Audio badge (top-left) should be BLUE (#2E51A2) - Brand color via use_brand_colors setting');
    console.log('- Resolution badge (top-right) should be GREEN (#00AA00) - This is a custom color');
    console.log('- Review badge (bottom) should be BLACK (#000000)');
    
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    // Close the database connection
    await db.end();
    console.log('Database connection closed');
  }
}

/**
 * Set up test badge settings in the database
 */
async function setupTestBadgeSettings(userId) {
  console.log('Setting up test badge settings...');
  
  // First check if audio badge settings exist for this user
  const audioCheckQuery = `SELECT id FROM audio_badge_settings WHERE user_id = $1`;
  const audioCheck = await db.query(audioCheckQuery, [userId]);
  
  // Setup audio badge with brand colors (blue)
  if (audioCheck.rows.length === 0) {
    // Insert new record
    const audioInsertQuery = `
      INSERT INTO audio_badge_settings (
        user_id, enabled, position, size, text_color, background_color, 
        background_opacity, border_radius, border_width, border_color, 
        border_opacity, use_brand_colors, margin, z_index, created_at, updated_at
      ) VALUES (
        $1, true, 'top-left', 100, '#FFFFFF', '#000000', 
        0.8, 10, 1, '#FFFFFF', 0.9, true, 20, 1, NOW(), NOW()
      )
      RETURNING id
    `;
    const audioResult = await db.query(audioInsertQuery, [userId]);
    console.log(`Audio badge settings created: ID ${audioResult.rows[0].id}`);
  } else {
    // Update existing record
    const audioUpdateQuery = `
      UPDATE audio_badge_settings 
      SET enabled = true, 
          position = 'top-left',
          size = 100,
          background_color = '#000000',
          use_brand_colors = true,
          updated_at = NOW()
      WHERE user_id = $1
      RETURNING id
    `;
    const audioResult = await db.query(audioUpdateQuery, [userId]);
    console.log(`Audio badge settings updated: ID ${audioResult.rows[0].id}`);
  }
  
  // Check for resolution badge settings
  const resolutionCheckQuery = `SELECT id FROM resolution_badge_settings WHERE user_id = $1`;
  const resolutionCheck = await db.query(resolutionCheckQuery, [userId]);
  
  // Setup resolution badge with custom color (green)
  if (resolutionCheck.rows.length === 0) {
    // Insert new record
    const resolutionInsertQuery = `
      INSERT INTO resolution_badge_settings (
        user_id, enabled, position, size, text_color, background_color, 
        background_opacity, border_radius, border_width, border_color, 
        border_opacity, use_brand_colors, margin, z_index, created_at, updated_at
      ) VALUES (
        $1, true, 'top-right', 100, '#FFFFFF', '#00AA00', 
        0.8, 10, 1, '#FFFFFF', 0.9, false, 20, 2, NOW(), NOW()
      )
      RETURNING id
    `;
    const resolutionResult = await db.query(resolutionInsertQuery, [userId]);
    console.log(`Resolution badge settings created: ID ${resolutionResult.rows[0].id}`);
  } else {
    // Update existing record
    const resolutionUpdateQuery = `
      UPDATE resolution_badge_settings 
      SET enabled = true, 
          position = 'top-right',
          size = 100,
          background_color = '#00AA00',
          use_brand_colors = false,
          updated_at = NOW()
      WHERE user_id = $1
      RETURNING id
    `;
    const resolutionResult = await db.query(resolutionUpdateQuery, [userId]);
    console.log(`Resolution badge settings updated: ID ${resolutionResult.rows[0].id}`);
  }
  
  // Check for review badge settings
  const reviewCheckQuery = `SELECT id FROM review_badge_settings WHERE user_id = $1`;
  const reviewCheck = await db.query(reviewCheckQuery, [userId]);
  
  // Setup review badge with default color (black)
  if (reviewCheck.rows.length === 0) {
    // Insert new record
    const reviewInsertQuery = `
      INSERT INTO review_badge_settings (
        user_id, enabled, position, size, text_color, background_color, 
        background_opacity, border_radius, border_width, border_color, 
        border_opacity, margin, z_index, created_at, updated_at, 
        badge_layout, max_sources_to_show
      ) VALUES (
        $1, true, 'bottom-left', 100, '#FFFFFF', '#000000', 
        0.8, 10, 1, '#FFFFFF', 0.9, 20, 3, NOW(), NOW(),
        'horizontal', 2
      )
      RETURNING id
    `;
    const reviewResult = await db.query(reviewInsertQuery, [userId]);
    console.log(`Review badge settings created: ID ${reviewResult.rows[0].id}`);
  } else {
    // Update existing record
    const reviewUpdateQuery = `
      UPDATE review_badge_settings 
      SET enabled = true, 
          position = 'bottom-left',
          size = 100,
          background_color = '#000000',
          updated_at = NOW()
      WHERE user_id = $1
      RETURNING id
    `;
    const reviewResult = await db.query(reviewUpdateQuery, [userId]);
    console.log(`Review badge settings updated: ID ${reviewResult.rows[0].id}`);
  }
}

// Run the test
testBadgeColors().catch(err => {
  console.error('Failed to run tests:', err);
  process.exit(1);
});