import { pool } from '../db.js';
import logger from '../lib/logger.js';

// Get audio badge settings by user ID
export const getAudioBadgeSettingsByUserId = async (userId) => {
  try {
    logger.info(`Getting audio badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `SELECT * FROM audio_badge_settings WHERE user_id = $1`,
      [userId]
    );
    
    if (result.rows.length === 0) {
      logger.info(`No audio badge settings found for user ID: ${userId}`);
      return null;
    }
    
    logger.info(`Found audio badge settings for user ID: ${userId}`);
    return result.rows[0];
  } catch (error) {
    logger.error(`Error getting audio badge settings: ${error.message}`);
    throw error;
  }
};

// Save or update audio badge settings
export const upsertAudioBadgeSettings = async (settings) => {
  try {
    logger.info(`Saving audio badge settings for user ID: ${settings.user_id}`);
    
    // Check if settings already exist for this user
    const existingSettings = await getAudioBadgeSettingsByUserId(settings.user_id);
    
    if (existingSettings) {
      // Update existing settings
      logger.info(`Updating existing audio badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `UPDATE audio_badge_settings SET 
          size = $1,
          margin = $2,
          position = $3,
          codec_type = $4,
          background_color = $5,
          background_opacity = $6,
          border_radius = $7,
          border_width = $8,
          border_color = $9,
          border_opacity = $10,
          shadow_enabled = $11,
          shadow_color = $12,
          shadow_blur = $13,
          shadow_offset_x = $14,
          shadow_offset_y = $15,
          z_index = $16,
          badge_image = $17,
          enabled = $18,
          updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $19
        RETURNING *`,
        [
          settings.size,
          settings.margin,
          settings.position,
          settings.codec_type || settings.audio_codec_type,
          settings.background_color,
          settings.background_opacity || settings.background_transparency,
          settings.border_radius,
          settings.border_width, 
          settings.border_color,
          settings.border_opacity || settings.border_transparency,
          settings.shadow_enabled || settings.shadow_toggle,
          settings.shadow_color,
          settings.shadow_blur || settings.shadow_blur_radius,
          settings.shadow_offset_x,
          settings.shadow_offset_y,
          settings.z_index,
          settings.badge_image || null,
          settings.enabled !== undefined ? settings.enabled : true,
          settings.user_id
        ]
      );
      
      logger.info(`Successfully updated audio badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    } else {
      // Insert new settings
      logger.info(`Creating new audio badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `INSERT INTO audio_badge_settings (
          user_id,
          size,
          margin,
          position,
          codec_type,
          background_color,
          background_opacity,
          border_radius,
          border_width,
          border_color,
          border_opacity,
          shadow_enabled,
          shadow_color,
          shadow_blur,
          shadow_offset_x,
          shadow_offset_y,
          z_index,
          badge_image,
          enabled,
          created_at,
          updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *`,
        [
          settings.user_id,
          settings.size,
          settings.margin,
          settings.position,
          settings.codec_type || settings.audio_codec_type,
          settings.background_color,
          settings.background_opacity || settings.background_transparency,
          settings.border_radius,
          settings.border_width,
          settings.border_color,
          settings.border_opacity || settings.border_transparency,
          settings.shadow_enabled || settings.shadow_toggle,
          settings.shadow_color,
          settings.shadow_blur || settings.shadow_blur_radius,
          settings.shadow_offset_x,
          settings.shadow_offset_y,
          settings.z_index,
          settings.badge_image || null,
          settings.enabled !== undefined ? settings.enabled : true
        ]
      );
      
      logger.info(`Successfully created audio badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    }
  } catch (error) {
    logger.error(`Error saving audio badge settings: ${error.message}`);
    throw error;
  }
};
