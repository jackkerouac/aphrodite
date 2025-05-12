/**
 * Migration Script to transfer data from old badge settings tables to the new unified_badge_settings table
 * 
 * This script:
 * 1. Gets all user IDs with existing badge settings
 * 2. For each user, migrates their audio, resolution, and review badge settings
 * 3. Logs the migration process
 */

import { pool } from '../../db.js';
import logger from '../../lib/logger.js';

async function migrateToUnifiedBadgeSettings() {
  const client = await pool.connect();
  
  try {
    logger.info('Starting migration to unified badge settings');
    
    // Begin a transaction
    await client.query('BEGIN');
    
    // First, check if the unified_badge_settings table exists
    const tableCheckResult = await client.query(`
      SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'unified_badge_settings'
      )
    `);
    
    if (!tableCheckResult.rows[0].exists) {
      logger.error('unified_badge_settings table does not exist. Please run the create_unified_badge_settings_table.sql migration first.');
      await client.query('ROLLBACK');
      return;
    }
    
    // Check if old tables exist
    const audioTableExists = await checkTableExists(client, 'audio_badge_settings');
    const resolutionTableExists = await checkTableExists(client, 'resolution_badge_settings');
    const reviewTableExists = await checkTableExists(client, 'review_badge_settings');
    
    // If none of the old tables exist, we can skip migration
    if (!audioTableExists && !resolutionTableExists && !reviewTableExists) {
      logger.info('No legacy badge settings tables found. No migration needed.');
      await client.query('COMMIT');
      return;
    }
    
    // Get all users with existing badge settings
    let userQuery = 'SELECT DISTINCT user_id FROM (';
    let unionParts = [];
    
    if (audioTableExists) {
      unionParts.push('SELECT user_id FROM audio_badge_settings');
    }
    
    if (resolutionTableExists) {
      unionParts.push('SELECT user_id FROM resolution_badge_settings');
    }
    
    if (reviewTableExists) {
      unionParts.push('SELECT user_id FROM review_badge_settings');
    }
    
    userQuery += unionParts.join(' UNION ') + ') as users';
    
    const userResult = await client.query(userQuery);
    
    const userIds = userResult.rows.map(row => row.user_id);
    logger.info(`Found ${userIds.length} users with existing badge settings to migrate`);
    
    // For each user, migrate their settings
    for (const userId of userIds) {
      logger.info(`Migrating badge settings for user ID: ${userId}`);
      
      // 1. Migrate Audio Badge Settings if the table exists
      if (audioTableExists) {
        await migrateAudioBadgeSettings(client, userId);
      }
      
      // 2. Migrate Resolution Badge Settings if the table exists
      if (resolutionTableExists) {
        await migrateResolutionBadgeSettings(client, userId);
      }
      
      // 3. Migrate Review Badge Settings if the table exists
      if (reviewTableExists) {
        await migrateReviewBadgeSettings(client, userId);
      }
    }
    
    // Commit the transaction
    await client.query('COMMIT');
    logger.info('Successfully migrated badge settings to the unified structure');
    
  } catch (error) {
    await client.query('ROLLBACK');
    logger.error(`Error during badge settings migration: ${error.message}`);
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Checks if a table exists in the database
 */
async function checkTableExists(client, tableName) {
  const result = await client.query(`
    SELECT EXISTS (
      SELECT 1 FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name = $1
    )
  `, [tableName]);
  
  return result.rows[0].exists;
}

/**
 * Migrates audio badge settings for a specific user
 */
async function migrateAudioBadgeSettings(client, userId) {
  try {
    // Check if audio badge settings exist for this user
    const audioBadgeResult = await client.query(
      'SELECT * FROM audio_badge_settings WHERE user_id = $1',
      [userId]
    );
    
    if (audioBadgeResult.rows.length === 0) {
      logger.info(`No audio badge settings found for user ID: ${userId}`);
      return;
    }
    
    const audioBadge = audioBadgeResult.rows[0];
    logger.info(`Found audio badge settings for user ID: ${userId}`);
    
    // Convert to the new unified format
    const badgeSize = Math.round((audioBadge.size || 0.1) * 1000) || 100; // Convert from old format to the new pixel-based format
    const position = audioBadge.position || 'top-left';
    const edgePadding = Math.round(audioBadge.margin) || 10;
    
    // Create properties object for audio-specific values
    const properties = {
      codec_type: audioBadge.codec_type || 'dolby_atmos'
    };
    
    // Convert opacity values from 0.0-1.0 to 0-100
    const backgroundOpacity = Math.round((audioBadge.background_opacity || audioBadge.background_transparency || 0.8) * 100);
    const borderOpacity = Math.round((audioBadge.border_opacity || audioBadge.border_transparency || 0.8) * 100);
    
    // Insert into unified_badge_settings
    await client.query(`
      INSERT INTO unified_badge_settings (
        user_id,
        badge_type,
        badge_size,
        edge_padding,
        badge_position,
        background_color,
        background_opacity,
        border_size,
        border_color,
        border_opacity,
        border_radius,
        border_width,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        properties
      ) VALUES (
        $1, 'audio', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
      )
      ON CONFLICT (user_id, badge_type) 
      DO UPDATE SET
        badge_size = EXCLUDED.badge_size,
        edge_padding = EXCLUDED.edge_padding,
        badge_position = EXCLUDED.badge_position,
        background_color = EXCLUDED.background_color,
        background_opacity = EXCLUDED.background_opacity,
        border_size = EXCLUDED.border_size,
        border_color = EXCLUDED.border_color,
        border_opacity = EXCLUDED.border_opacity,
        border_radius = EXCLUDED.border_radius,
        border_width = EXCLUDED.border_width,
        shadow_enabled = EXCLUDED.shadow_enabled,
        shadow_color = EXCLUDED.shadow_color,
        shadow_blur = EXCLUDED.shadow_blur,
        shadow_offset_x = EXCLUDED.shadow_offset_x,
        shadow_offset_y = EXCLUDED.shadow_offset_y,
        properties = EXCLUDED.properties,
        updated_at = CURRENT_TIMESTAMP
    `, [
      userId,
      badgeSize,
      edgePadding,
      position,
      audioBadge.background_color || '#000000',
      backgroundOpacity,
      audioBadge.border_width || 2,
      audioBadge.border_color || '#FFFFFF',
      borderOpacity,
      audioBadge.border_radius || 5,
      audioBadge.border_width || 1,
      audioBadge.shadow_enabled === true || audioBadge.shadow_toggle === true,
      audioBadge.shadow_color || '#000000',
      audioBadge.shadow_blur || audioBadge.shadow_blur_radius || 10,
      audioBadge.shadow_offset_x || 0,
      audioBadge.shadow_offset_y || 0,
      JSON.stringify(properties)
    ]);
    
    logger.info(`Successfully migrated audio badge settings for user ID: ${userId}`);
  } catch (error) {
    logger.error(`Error migrating audio badge settings for user ID ${userId}: ${error.message}`);
    throw error;
  }
}

/**
 * Migrates resolution badge settings for a specific user
 */
async function migrateResolutionBadgeSettings(client, userId) {
  try {
    // Check if resolution badge settings exist for this user
    const resolutionBadgeResult = await client.query(
      'SELECT * FROM resolution_badge_settings WHERE user_id = $1',
      [userId]
    );
    
    if (resolutionBadgeResult.rows.length === 0) {
      logger.info(`No resolution badge settings found for user ID: ${userId}`);
      return;
    }
    
    const resolutionBadge = resolutionBadgeResult.rows[0];
    logger.info(`Found resolution badge settings for user ID: ${userId}`);
    
    // Convert to the new unified format
    const badgeSize = Math.round((resolutionBadge.size || 0.1) * 1000) || 100; // Convert from old format to the new pixel-based format
    const position = resolutionBadge.position || 'top-right';
    const edgePadding = Math.round(resolutionBadge.margin) || 10;
    
    // Create properties object for resolution-specific values
    const properties = {
      resolution_type: resolutionBadge.resolution_type || '4k'
    };
    
    // Convert opacity values from 0.0-1.0 to 0-100
    const backgroundOpacity = Math.round((resolutionBadge.background_transparency || 0.7) * 100);
    const borderOpacity = Math.round((resolutionBadge.border_transparency || 0.9) * 100);
    
    // Insert into unified_badge_settings
    await client.query(`
      INSERT INTO unified_badge_settings (
        user_id,
        badge_type,
        badge_size,
        edge_padding,
        badge_position,
        background_color,
        background_opacity,
        border_size,
        border_color,
        border_opacity,
        border_radius,
        border_width,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        properties
      ) VALUES (
        $1, 'resolution', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
      )
      ON CONFLICT (user_id, badge_type) 
      DO UPDATE SET
        badge_size = EXCLUDED.badge_size,
        edge_padding = EXCLUDED.edge_padding,
        badge_position = EXCLUDED.badge_position,
        background_color = EXCLUDED.background_color,
        background_opacity = EXCLUDED.background_opacity,
        border_size = EXCLUDED.border_size,
        border_color = EXCLUDED.border_color,
        border_opacity = EXCLUDED.border_opacity,
        border_radius = EXCLUDED.border_radius,
        border_width = EXCLUDED.border_width,
        shadow_enabled = EXCLUDED.shadow_enabled,
        shadow_color = EXCLUDED.shadow_color,
        shadow_blur = EXCLUDED.shadow_blur,
        shadow_offset_x = EXCLUDED.shadow_offset_x,
        shadow_offset_y = EXCLUDED.shadow_offset_y,
        properties = EXCLUDED.properties,
        updated_at = CURRENT_TIMESTAMP
    `, [
      userId,
      badgeSize,
      edgePadding,
      position,
      resolutionBadge.background_color || '#ffffff',
      backgroundOpacity,
      resolutionBadge.border_width || 1,
      resolutionBadge.border_color || '#000000',
      borderOpacity,
      resolutionBadge.border_radius || 5,
      resolutionBadge.border_width || 1,
      resolutionBadge.shadow_toggle === true,
      resolutionBadge.shadow_color || '#000000',
      resolutionBadge.shadow_blur_radius || 5,
      resolutionBadge.shadow_offset_x || 0,
      resolutionBadge.shadow_offset_y || 0,
      JSON.stringify(properties)
    ]);
    
    logger.info(`Successfully migrated resolution badge settings for user ID: ${userId}`);
  } catch (error) {
    logger.error(`Error migrating resolution badge settings for user ID ${userId}: ${error.message}`);
    throw error;
  }
}

/**
 * Migrates review badge settings for a specific user
 */
async function migrateReviewBadgeSettings(client, userId) {
  try {
    // Check if review badge settings exist for this user
    const reviewBadgeResult = await client.query(
      'SELECT * FROM review_badge_settings WHERE user_id = $1',
      [userId]
    );
    
    if (reviewBadgeResult.rows.length === 0) {
      logger.info(`No review badge settings found for user ID: ${userId}`);
      return;
    }
    
    const reviewBadge = reviewBadgeResult.rows[0];
    logger.info(`Found review badge settings for user ID: ${userId}`);
    
    // Convert to the new unified format
    const badgeSize = Math.round((reviewBadge.size || 0.1) * 1000) || 100; // Convert from old format to the new pixel-based format
    const position = reviewBadge.position || 'bottom-left';
    const edgePadding = Math.round(reviewBadge.margin) || 10;
    const displayFormat = reviewBadge.display_format || 'horizontal';
    
    // Create properties object for review-specific values
    const properties = {
      review_sources: reviewBadge.review_sources || ['imdb', 'rotten_tomatoes'],
      score_type: reviewBadge.score_type || 'percentage'
    };
    
    // Convert opacity values from 0.0-1.0 to 0-100
    const backgroundOpacity = Math.round((reviewBadge.background_transparency || 0.7) * 100);
    const borderOpacity = Math.round((reviewBadge.border_transparency || 0.9) * 100);
    
    // Insert into unified_badge_settings
    await client.query(`
      INSERT INTO unified_badge_settings (
        user_id,
        badge_type,
        badge_size,
        edge_padding,
        badge_position,
        display_format,
        background_color,
        background_opacity,
        border_size,
        border_color,
        border_opacity,
        border_radius,
        border_width,
        shadow_enabled,
        shadow_color,
        shadow_blur,
        shadow_offset_x,
        shadow_offset_y,
        properties
      ) VALUES (
        $1, 'review', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
      )
      ON CONFLICT (user_id, badge_type) 
      DO UPDATE SET
        badge_size = EXCLUDED.badge_size,
        edge_padding = EXCLUDED.edge_padding,
        badge_position = EXCLUDED.badge_position,
        display_format = EXCLUDED.display_format,
        background_color = EXCLUDED.background_color,
        background_opacity = EXCLUDED.background_opacity,
        border_size = EXCLUDED.border_size,
        border_color = EXCLUDED.border_color,
        border_opacity = EXCLUDED.border_opacity,
        border_radius = EXCLUDED.border_radius,
        border_width = EXCLUDED.border_width,
        shadow_enabled = EXCLUDED.shadow_enabled,
        shadow_color = EXCLUDED.shadow_color,
        shadow_blur = EXCLUDED.shadow_blur,
        shadow_offset_x = EXCLUDED.shadow_offset_x,
        shadow_offset_y = EXCLUDED.shadow_offset_y,
        properties = EXCLUDED.properties,
        updated_at = CURRENT_TIMESTAMP
    `, [
      userId,
      badgeSize,
      edgePadding,
      position,
      displayFormat,
      reviewBadge.background_color || '#000000',
      backgroundOpacity,
      reviewBadge.border_width || 1,
      reviewBadge.border_color || '#FFFFFF',
      borderOpacity,
      reviewBadge.border_radius || 5,
      reviewBadge.border_width || 1,
      reviewBadge.shadow_toggle === true,
      reviewBadge.shadow_color || '#000000',
      reviewBadge.shadow_blur_radius || 5,
      reviewBadge.shadow_offset_x || 0,
      reviewBadge.shadow_offset_y || 0,
      JSON.stringify(properties)
    ]);
    
    logger.info(`Successfully migrated review badge settings for user ID: ${userId}`);
  } catch (error) {
    logger.error(`Error migrating review badge settings for user ID ${userId}: ${error.message}`);
    throw error;
  }
}

// Execute the migration if this file is run directly
if (process.argv[1] === new URL(import.meta.url).pathname) {
  logger.info('Running badge settings migration script');
  migrateToUnifiedBadgeSettings()
    .then(() => {
      logger.info('Badge settings migration completed successfully');
      process.exit(0);
    })
    .catch(err => {
      logger.error(`Badge settings migration failed: ${err.message}`);
      process.exit(1);
    });
} else {
  // Export for use in other scripts
  export { migrateToUnifiedBadgeSettings };
}
