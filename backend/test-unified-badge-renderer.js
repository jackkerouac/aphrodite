import UnifiedPosterProcessor from './services/unified-badge-renderer/unifiedPosterProcessor.js';
import logger from './lib/logger.js';
import { pool as db } from './db.js';

async function testUnifiedBadgeRenderer() {
  try {
    console.log('Testing Unified Badge Renderer...');
    
    // Initialize the processor
    const processor = new UnifiedPosterProcessor();
    await processor.init();
    
    // Get a user ID for testing
    const userResult = await db.query('SELECT id FROM users LIMIT 1');
    if (userResult.rows.length === 0) {
      throw new Error('No users found in database');
    }
    const userId = userResult.rows[0].id;
    
    // Get a Jellyfin item ID for testing
    const itemResult = await db.query(`
      SELECT jellyfin_id FROM jellyfin_items 
      WHERE media_type = 'Movie' 
      LIMIT 1
    `);
    if (itemResult.rows.length === 0) {
      throw new Error('No Jellyfin items found in database');
    }
    const jellyfinItemId = itemResult.rows[0].jellyfin_id;
    
    // Create a test job
    const jobResult = await db.query(`
      INSERT INTO jobs (user_id, name, status, items_total, items_processed, items_failed, created_at, updated_at)
      VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      RETURNING id
    `, [userId, 'Test Badge Rendering Job', 'pending', 1, 0, 0]);
    
    const jobId = jobResult.rows[0].id;
    
    // Create a test job item
    const itemQuery = `
      INSERT INTO job_items (job_id, jellyfin_item_id, title, status, created_at, updated_at)
      VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      RETURNING id
    `;
    
    const itemValues = [
      jobId,
      jellyfinItemId,
      'Test Item',
      'pending'
    ];
    
    const jobItemResult = await db.query(itemQuery, itemValues);
    const jobItemId = jobItemResult.rows[0].id;
    
    // Process the item
    const result = await processor.processItem(
      { id: jobItemId, job_id: jobId, jellyfin_item_id: jellyfinItemId, title: 'Test Item' },
      jobId,
      userId
    );
    
    console.log('Processing result:', result);
    
    if (result.success) {
      console.log('✅ Test successful! The unified badge renderer is working properly.');
    } else {
      console.log('❌ Test failed. Check the error for details.');
    }
    
    // Clean up
    await db.query('DELETE FROM job_items WHERE id = $1', [jobItemId]);
    await db.query('DELETE FROM jobs WHERE id = $1', [jobId]);
    
    // Close the database connection
    await db.end();
  } catch (error) {
    console.error('Error testing unified badge renderer:', error);
  }
}

// Run the test
testUnifiedBadgeRenderer();
