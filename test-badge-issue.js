import { pool } from './backend/db.js';
import PosterProcessor from './backend/services/badge-renderer/posterProcessor.js';
import MetadataService from './backend/services/badge-renderer/metadataService.js';

async function testBadgeIssue() {
  try {
    console.log('Testing badge issue...');
    
    // Test with user ID 1
    const userId = 1;
    
    // Check which badges are enabled
    const badgeSettingsQuery = `
      SELECT 
        'resolution' as type,
        enabled,
        position,
        font_family,
        font_size,
        text_color,
        z_index as stacking_order
      FROM resolution_badge_settings
      WHERE user_id = $1
      UNION ALL
      SELECT 
        'review' as type,
        enabled,
        position,
        font_family,
        font_size,
        text_color,
        z_index as stacking_order
      FROM review_badge_settings
      WHERE user_id = $1;
    `;
    
    const settingsResult = await pool.query(badgeSettingsQuery, [userId]);
    console.log('\n=== Badge Settings ===');
    console.log(JSON.stringify(settingsResult.rows, null, 2));
    
    // Get a sample item from jellyfin
    const itemQuery = `
      SELECT *
      FROM job_items
      LIMIT 1;
    `;
    
    const itemResult = await pool.query(itemQuery);
    const item = itemResult.rows[0];
    console.log('\n=== Sample Item ===');
    console.log(JSON.stringify(item, null, 2));
    
    if (item) {
      // Initialize services
      const posterProcessor = new PosterProcessor();
      const metadataService = new MetadataService();
      
      // Fetch metadata
      const metadataItem = {
        jellyfin_id: item.jellyfin_item_id,
        media_type: 'Movie'
      };
      
      console.log('\n=== Fetching Metadata ===');
      const metadata = await metadataService.fetchItemMetadata(metadataItem, userId);
      console.log(JSON.stringify(metadata, null, 2));
      
      // Get badge settings with values
      console.log('\n=== Badge Settings with Values ===');
      const badgeSettings = await posterProcessor.getBadgeSettings(userId, item);
      console.log(JSON.stringify(badgeSettings, null, 2));
      
      // Check which badges have values
      console.log('\n=== Badge Analysis ===');
      badgeSettings.forEach(badge => {
        console.log(`${badge.settings.type}: enabled=${badge.enabled}, value=${badge.value}, stackingOrder=${badge.settings.stackingOrder}`);
      });
    }
    
  } catch (error) {
    console.error('Error in test:', error);
  } finally {
    await pool.end();
  }
}

testBadgeIssue();
