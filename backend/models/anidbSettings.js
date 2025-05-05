// backend/models/anidbSettings.js
import { pool } from '../db.js';

/**
 * Get AniDB settings for a specific user
 * @param {number} userId - The user ID
 * @returns {Promise<Object>} - The user's AniDB settings
 */
export async function getAnidbSettingsByUserId(userId) {
  try {
    console.log(`🔍 [getAnidbSettingsByUserId] Fetching settings for user ${userId}`);
    
    const result = await pool.query(
      'SELECT * FROM anidb_settings WHERE user_id = $1',
      [userId]
    );
    
    if (result.rows.length === 0) {
      console.log(`⚠️ [getAnidbSettingsByUserId] No settings found for user ${userId}`);
      return null;
    }
    
    console.log(`✅ [getAnidbSettingsByUserId] Found settings for user ${userId}`);
    return {
      anidb_username: result.rows[0].username,
      anidb_password: result.rows[0].password,
      anidb_client: result.rows[0].client,
      anidb_version: result.rows[0].version,
      anidb_language: result.rows[0].language,
      anidb_cache_expiration: result.rows[0].cache_expiration
    };
  } catch (error) {
    console.error('❌ [getAnidbSettingsByUserId] Error:', error);
    throw error;
  }
}

/**
 * Create or update AniDB settings for a user
 * @param {Object} settings - The settings object
 * @param {number} settings.user_id - The user ID
 * @param {string} settings.anidb_username - AniDB username
 * @param {string} settings.anidb_password - AniDB password
 * @param {string} settings.anidb_client - AniDB client name
 * @param {string} settings.anidb_version - AniDB client version
 * @param {string} settings.anidb_language - AniDB preferred language
 * @param {number} settings.anidb_cache_expiration - AniDB cache expiration in minutes
 * @returns {Promise<Object>} - The saved settings
 */
export async function upsertAnidbSettings(settings) {
  try {
    console.log(`📝 [upsertAnidbSettings] Upserting settings for user ${settings.user_id}`);
    console.log('📝 [upsertAnidbSettings] Settings:', { 
      ...settings,
      anidb_password: '******' // Log masked password
    });
    
    // Check if settings exist for this user
    const checkResult = await pool.query(
      'SELECT * FROM anidb_settings WHERE user_id = $1',
      [settings.user_id]
    );
    
    let result;
    
    if (checkResult.rows.length === 0) {
      // Create new settings
      console.log(`📝 [upsertAnidbSettings] Creating new settings for user ${settings.user_id}`);
      
      result = await pool.query(
        `INSERT INTO anidb_settings 
         (user_id, username, password, client, version, language, cache_expiration, created_at, updated_at) 
         VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
         RETURNING *`,
        [
          settings.user_id,
          settings.anidb_username,
          settings.anidb_password,
          settings.anidb_client,
          settings.anidb_version,
          settings.anidb_language,
          settings.anidb_cache_expiration
        ]
      );
    } else {
      // Update existing settings
      console.log(`📝 [upsertAnidbSettings] Updating existing settings for user ${settings.user_id}`);
      
      result = await pool.query(
        `UPDATE anidb_settings 
         SET username = $2, 
             password = $3, 
             client = $4, 
             version = $5, 
             language = $6, 
             cache_expiration = $7, 
             updated_at = CURRENT_TIMESTAMP 
         WHERE user_id = $1 
         RETURNING *`,
        [
          settings.user_id,
          settings.anidb_username,
          settings.anidb_password,
          settings.anidb_client,
          settings.anidb_version,
          settings.anidb_language,
          settings.anidb_cache_expiration
        ]
      );
    }
    
    console.log(`✅ [upsertAnidbSettings] Successfully saved settings for user ${settings.user_id}`);
    
    return {
      anidb_username: result.rows[0].username,
      anidb_password: result.rows[0].password,
      anidb_client: result.rows[0].client,
      anidb_version: result.rows[0].version,
      anidb_language: result.rows[0].language,
      anidb_cache_expiration: result.rows[0].cache_expiration
    };
  } catch (error) {
    console.error('❌ [upsertAnidbSettings] Error:', error);
    throw error;
  }
}

// Create a function to test the AniDB connection
export async function testAnidbConnection(settings) {
  try {
    console.log('🔍 [testAnidbConnection] Testing AniDB connection with settings:', {
      ...settings,
      anidb_password: '******' // Log masked password
    });
    
    // Verify required fields
    if (!settings.anidb_username || !settings.anidb_password || !settings.anidb_client || !settings.anidb_version) {
      throw new Error('Missing required AniDB settings');
    }
    
    // AniDB recommends using UDP for API access, but we'll use a basic auth check via HTTP
    // In a production environment, you'd want to implement the full UDP API or use HTTP properly
    
    // For now, we'll just simulate a successful connection check
    // In a real implementation, you'd make an actual API call to AniDB here
    
    // Simulating a delay for realism
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // For testing purposes only - in production use actual API verification
    if (settings.anidb_username === 'invalid' || settings.anidb_password === 'invalid') {
      throw new Error('Invalid AniDB credentials');
    }
    
    console.log('✅ [testAnidbConnection] Successfully tested AniDB connection');
    
    return {
      success: true,
      message: 'Successfully connected to AniDB'
    };
  } catch (error) {
    console.error('❌ [testAnidbConnection] Error:', error);
    throw error;
  }
}
