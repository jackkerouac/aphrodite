// Test script to diagnose black badge issue
import { pool } from './backend/db.js';

async function testBadgeBlackIssue() {
  try {
    console.log('Testing black badge issue...');
    
    // User ID for testing
    const userId = 1;
    
    // Function to check for duplicate badge settings in the database
    async function checkDuplicateBadges() {
      const query = `
        SELECT 
          user_id, 
          badge_type, 
          COUNT(*) as count
        FROM unified_badge_settings
        GROUP BY user_id, badge_type
        HAVING COUNT(*) > 1
      `;
      
      const result = await pool.query(query);
      
      if (result.rows.length > 0) {
        console.log('\n=== DUPLICATE BADGE SETTINGS FOUND ===');
        console.log(JSON.stringify(result.rows, null, 2));
        return true;
      } else {
        console.log('No duplicate badge settings found.');
        return false;
      }
    }
    
    // Function to check badge settings
    async function checkBadgeSettings() {
      const query = `
        SELECT 
          id,
          user_id,
          badge_type,
          badge_size,
          background_color,
          properties,
          created_at
        FROM unified_badge_settings
        WHERE user_id = $1
        ORDER BY badge_type, created_at
      `;
      
      const result = await pool.query(query, [userId]);
      console.log('\n=== CURRENT BADGE SETTINGS ===');
      console.log(JSON.stringify(result.rows, null, 2));
      
      return result.rows;
    }
    
    // Check if we have any duplicate badges
    const hasDuplicates = await checkDuplicateBadges();
    
    // Get current badge settings
    const badgeSettings = await checkBadgeSettings();
    
    // Check for black badges
    const blackBadges = badgeSettings.filter(badge => 
      badge.background_color === '#000000' || badge.background_color === 'black');
    
    if (blackBadges.length > 0) {
      console.log('\n=== BLACK BADGES FOUND ===');
      console.log(JSON.stringify(blackBadges, null, 2));
    } else {
      console.log('No black badges found.');
    }
    
    // If duplicates are found, offer to fix
    if (hasDuplicates) {
      console.log('\n=== FIXING DUPLICATE BADGES ===');
      
      // Create a map of badge types to keep track of which ones we've processed
      const processedBadges = new Map();
      
      for (const badge of badgeSettings) {
        const key = `${badge.user_id}-${badge.badge_type}`;
        
        if (!processedBadges.has(key)) {
          // Keep the first badge for each type
          processedBadges.set(key, badge.id);
        } else {
          // Delete duplicate badges
          console.log(`Deleting duplicate badge: ID ${badge.id}, Type: ${badge.badge_type}`);
          await pool.query('DELETE FROM unified_badge_settings WHERE id = $1', [badge.id]);
        }
      }
      
      console.log('Duplicate badges have been removed.');
      
      // Verify our fix
      await checkDuplicateBadges();
      await checkBadgeSettings();
    }
    
  } catch (error) {
    console.error('Error in test:', error);
  } finally {
    await pool.end();
  }
}

// Run the test
testBadgeBlackIssue();
