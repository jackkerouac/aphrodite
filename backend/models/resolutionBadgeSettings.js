import { pool } from '../db.js';
import logger from '../lib/logger.js';

// Get resolution badge settings by user ID
export const getResolutionBadgeSettingsByUserId = async (userId) => {
  try {
    logger.info(`Getting resolution badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `SELECT * FROM resolution_badge_settings WHERE user_id = $1`,
      [userId]
    );
    
    if (result.rows.length === 0) {
      logger.info(`No resolution badge settings found for user ID: ${userId}`);
      return null;
    }
    
    logger.info(`Found resolution badge settings for user ID: ${userId}`);
    return result.rows[0];
  } catch (error) {
    logger.error(`Error getting resolution badge settings: ${error.message}`);
    throw error;
  }
};

// Save or update resolution badge settings
export const upsertResolutionBadgeSettings = async (settings) => {
  try {
    logger.info(`Saving resolution badge settings for user ID: ${settings.user_id}`);
    
    // Check if settings already exist for this user
    const existingSettings = await getResolutionBadgeSettingsByUserId(settings.user_id);
    
    if (existingSettings) {
      // Update existing settings
      logger.info(`Updating existing resolution badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `UPDATE resolution_badge_settings SET 
          size = $1,
          margin = $2,
          position = $3,
          resolution_type = $4,
          background_color = $5,
          background_transparency = $6,
          border_radius = $7,
          border_width = $8,
          border_color = $9,
          border_transparency = $10,
          shadow_toggle = $11,
          shadow_color = $12,
          shadow_blur_radius = $13,
          shadow_offset_x = $14,
          shadow_offset_y = $15,
          z_index = $16
        WHERE user_id = $17
        RETURNING *`,
        [
          settings.size,
          settings.margin,
          settings.position,
          settings.resolution_type,
          settings.background_color,
          settings.background_transparency,
          settings.border_radius,
          settings.border_width, 
          settings.border_color,
          settings.border_transparency,
          settings.shadow_toggle,
          settings.shadow_color,
          settings.shadow_blur_radius,
          settings.shadow_offset_x,
          settings.shadow_offset_y,
          settings.z_index,
          settings.user_id
        ]
      );
      
      logger.info(`Successfully updated resolution badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    } else {
      // Insert new settings
      logger.info(`Creating new resolution badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `INSERT INTO resolution_badge_settings (
          user_id,
          size,
          margin,
          position,
          resolution_type,
          background_color,
          background_transparency,
          border_radius,
          border_width,
          border_color,
          border_transparency,
          shadow_toggle,
          shadow_color,
          shadow_blur_radius,
          shadow_offset_x,
          shadow_offset_y,
          z_index
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
        RETURNING *`,
        [
          settings.user_id,
          settings.size,
          settings.margin,
          settings.position,
          settings.resolution_type,
          settings.background_color,
          settings.background_transparency,
          settings.border_radius,
          settings.border_width,
          settings.border_color,
          settings.border_transparency,
          settings.shadow_toggle,
          settings.shadow_color,
          settings.shadow_blur_radius,
          settings.shadow_offset_x,
          settings.shadow_offset_y,
          settings.z_index
        ]
      );
      
      logger.info(`Successfully created resolution badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    }
  } catch (error) {
    logger.error(`Error saving resolution badge settings: ${error.message}`);
    throw error;
  }
};
