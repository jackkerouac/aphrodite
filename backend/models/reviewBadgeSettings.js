import { pool } from '../db.js';
import logger from '../lib/logger.js';

// Get review badge settings by user ID
export const getReviewBadgeSettingsByUserId = async (userId) => {
  try {
    logger.info(`Getting review badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `SELECT * FROM review_badge_settings WHERE user_id = $1`,
      [userId]
    );
    
    if (result.rows.length === 0) {
      logger.info(`No review badge settings found for user ID: ${userId}`);
      return null;
    }
    
    logger.info(`Found review badge settings for user ID: ${userId}`);
    return result.rows[0];
  } catch (error) {
    logger.error(`Error getting review badge settings: ${error.message}`);
    throw error;
  }
};

// Save or update review badge settings
export const upsertReviewBadgeSettings = async (settings) => {
  try {
    logger.info(`Saving review badge settings for user ID: ${settings.user_id}`);
    
    // Check if settings already exist for this user
    const existingSettings = await getReviewBadgeSettingsByUserId(settings.user_id);
    
    if (existingSettings) {
      // Update existing settings
      logger.info(`Updating existing review badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `UPDATE review_badge_settings SET 
          size = $1,
          margin = $2,
          background_color = $3,
          background_transparency = $4,
          border_radius = $5,
          border_width = $6,
          border_color = $7,
          border_transparency = $8,
          shadow_toggle = $9,
          shadow_color = $10,
          shadow_blur_radius = $11,
          shadow_offset_x = $12,
          shadow_offset_y = $13,
          z_index = $14,
          position = $15,
          badge_layout = $16,
          display_sources = $17,
          source_order = $18,
          show_logo = $19,
          logo_size = $20,
          logo_position = $21,
          logo_text_spacing = $22,
          score_format = $23,
          spacing = $24,
          font_family = $25,
          font_size = $26,
          font_weight = $27,
          text_color = $28,
          text_transparency = $29
        WHERE user_id = $30
        RETURNING *`,
        [
          settings.size,
          settings.margin,
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
          settings.position,
          settings.badge_layout,
          settings.display_sources,
          settings.source_order,
          settings.show_logo,
          settings.logo_size,
          settings.logo_position,
          settings.logo_text_spacing,
          settings.score_format,
          settings.spacing,
          settings.font_family,
          settings.font_size,
          settings.font_weight,
          settings.text_color,
          settings.text_transparency,
          settings.user_id
        ]
      );
      
      logger.info(`Successfully updated review badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    } else {
      // Insert new settings
      logger.info(`Creating new review badge settings for user ID: ${settings.user_id}`);
      
      const result = await pool.query(
        `INSERT INTO review_badge_settings (
          user_id,
          size,
          margin,
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
          z_index,
          position,
          badge_layout,
          display_sources,
          source_order,
          show_logo,
          logo_size,
          logo_position,
          logo_text_spacing,
          score_format,
          spacing,
          font_family,
          font_size,
          font_weight,
          text_color,
          text_transparency
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30)
        RETURNING *`,
        [
          settings.user_id,
          settings.size,
          settings.margin,
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
          settings.position,
          settings.badge_layout,
          settings.display_sources,
          settings.source_order,
          settings.show_logo,
          settings.logo_size,
          settings.logo_position,
          settings.logo_text_spacing,
          settings.score_format,
          settings.spacing,
          settings.font_family,
          settings.font_size,
          settings.font_weight,
          settings.text_color,
          settings.text_transparency
        ]
      );
      
      logger.info(`Successfully created review badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    }
  } catch (error) {
    logger.error(`Error saving review badge settings: ${error.message}`);
    throw error;
  }
};
