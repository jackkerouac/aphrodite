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
    logger.info(`Size value being saved: ${settings.size}, Type: ${typeof settings.size}`);
    logger.info(`Full settings object: ${JSON.stringify(settings, null, 2)}`);
    
    // Explicitly log the background color for debugging
    logger.info(`Background color in settings: ${settings.background_color}`);
    logger.info(`Background color field from UI: ${settings.backgroundColor}`);
    
    // Ensure numeric fields are properly parsed
    // We need to convert explicitly to ensure consistency
    const parsedSettings = {
      ...settings,
      size: parseInt(String(settings.size), 10) || 100, // Use parseInt and provide a fallback
      margin: Number(settings.margin) || 10,
      background_opacity: Number(settings.background_opacity || settings.background_transparency || 0.8),
      border_radius: Number(settings.border_radius || 0),
      border_width: Number(settings.border_width || 0),
      border_opacity: Number(settings.border_opacity || settings.border_transparency || 0.8),
      // Ensure background color is properly handled
      background_color: settings.background_color || settings.backgroundColor || '#000000',
      shadow_color: settings.shadow_color || '#000000',
      shadow_blur: Number(settings.shadow_blur || settings.shadow_blur_radius || 0),
      // Ensure shadow_enabled is an explicit boolean (not null or undefined)
      shadow_enabled: settings.shadow_enabled !== null && settings.shadow_enabled !== undefined ? 
                    Boolean(settings.shadow_enabled) : 
                    (settings.shadow_toggle !== null && settings.shadow_toggle !== undefined ? 
                     Boolean(settings.shadow_toggle) : false),
      shadow_offset_x: Number(settings.shadow_offset_x || 0),
      shadow_offset_y: Number(settings.shadow_offset_y || 0),
      z_index: Number(settings.z_index || 1),
      font_size: settings.font_size !== undefined ? Number(settings.font_size) : 24,
    };
    
    logger.info(`After explicit conversion, size = ${parsedSettings.size}`);
    
    // Add detailed validation to catch any null values
    const requiredFields = [
      'size', 'margin', 'position', 'codec_type', 'background_color', 'background_opacity',
      'border_radius', 'border_width', 'border_color', 'border_opacity',
      'shadow_enabled', 'shadow_color', 'shadow_blur', 'shadow_offset_x', 'shadow_offset_y',
      'z_index'
    ];
    
    // Log validation warnings for missing fields
    for (const field of requiredFields) {
      if (parsedSettings[field] === undefined || parsedSettings[field] === null) {
        logger.warn(`Warning: Required field '${field}' is ${parsedSettings[field] === undefined ? 'undefined' : 'null'} in audio badge settings`);
        // Set default values for any missing fields
        switch (field) {
          case 'shadow_enabled':
            parsedSettings[field] = false;
            break;
          case 'shadow_color':
            parsedSettings[field] = '#000000';
            break;
          case 'shadow_blur':
          case 'shadow_offset_x':
          case 'shadow_offset_y':
            parsedSettings[field] = 0;
            break;
          case 'position':
            parsedSettings[field] = 'top-left';
            break;
          case 'codec_type':
            parsedSettings[field] = 'dolby_atmos';
            break;
          case 'background_color':
          case 'border_color':
            parsedSettings[field] = '#000000';
            break;
          default:
            parsedSettings[field] = 0;
        }
        logger.info(`Setting default value for '${field}': ${parsedSettings[field]}`);
      }
    }
    
    // Final check to explicitly ensure shadow_enabled is not null
    if (parsedSettings.shadow_enabled === null || parsedSettings.shadow_enabled === undefined) {
      logger.warn('shadow_enabled is null or undefined after all processing - forcing to false');
      parsedSettings.shadow_enabled = false;
    }
    
    logger.info(`Final shadow_enabled value: ${parsedSettings.shadow_enabled}`);
    
    // Check if settings already exist for this user
    const existingSettings = await getAudioBadgeSettingsByUserId(settings.user_id);
    
    if (existingSettings) {
      // Update existing settings
      logger.info(`Updating existing audio badge settings for user ID: ${settings.user_id}`);
      
      logger.info(`Executing UPDATE with shadow_enabled=${parsedSettings.shadow_enabled} (type: ${typeof parsedSettings.shadow_enabled})`);
      logger.info('Shadow enabled parameter value: ' + (parsedSettings.shadow_enabled === true ? 'true' : 'false'));
      
      
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
          shadow_enabled = $11::boolean,
          shadow_color = $12,
          shadow_blur = $13,
          shadow_offset_x = $14,
          shadow_offset_y = $15,
          z_index = $16,
          badge_image = $17,
          enabled = $18,
          use_brand_colors = $19,
          updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $20
        RETURNING *`,
        [
          parsedSettings.size,
          parsedSettings.margin,
          parsedSettings.position,
          parsedSettings.codec_type || parsedSettings.audio_codec_type,
          parsedSettings.background_color,
          parsedSettings.background_opacity || parsedSettings.background_transparency,
          parsedSettings.border_radius,
          parsedSettings.border_width, 
          parsedSettings.border_color,
          parsedSettings.border_opacity || parsedSettings.border_transparency,
          parsedSettings.shadow_enabled, // Explicitly pass user-selected value
          parsedSettings.shadow_color,
          parsedSettings.shadow_blur || parsedSettings.shadow_blur_radius,
          parsedSettings.shadow_offset_x,
          parsedSettings.shadow_offset_y,
          parsedSettings.z_index,
          parsedSettings.badge_image || null,
          parsedSettings.enabled !== undefined ? parsedSettings.enabled : true,
          parsedSettings.use_brand_colors !== undefined ? parsedSettings.use_brand_colors : true,
          parsedSettings.user_id
        ]
      );
      
      logger.info(`Successfully updated audio badge settings for user ID: ${settings.user_id}`);
      return result.rows[0];
    } else {
      // Insert new settings
      logger.info(`Creating new audio badge settings for user ID: ${settings.user_id}`);
      
      logger.info(`Executing INSERT with shadow_enabled=${parsedSettings.shadow_enabled} (type: ${typeof parsedSettings.shadow_enabled})`);
      logger.info('Shadow enabled parameter value: ' + (parsedSettings.shadow_enabled === true ? 'true' : 'false'));
      
      
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
          use_brand_colors,
          created_at,
          updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::boolean, $12, $13, $14, $15, $16, $17, $18, $19, $20, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *`,
        [
          parsedSettings.user_id,
          parsedSettings.size,
          parsedSettings.margin,
          parsedSettings.position,
          parsedSettings.codec_type || parsedSettings.audio_codec_type,
          parsedSettings.background_color,
          parsedSettings.background_opacity || parsedSettings.background_transparency,
          parsedSettings.border_radius,
          parsedSettings.border_width,
          parsedSettings.border_color,
          parsedSettings.border_opacity || parsedSettings.border_transparency,
          parsedSettings.shadow_enabled, // Make sure this is explicitly a boolean
          parsedSettings.shadow_color,
          parsedSettings.shadow_blur || parsedSettings.shadow_blur_radius,
          parsedSettings.shadow_offset_x,
          parsedSettings.shadow_offset_y,
          parsedSettings.z_index,
          parsedSettings.badge_image || null,
          parsedSettings.enabled !== undefined ? parsedSettings.enabled : true,
          parsedSettings.use_brand_colors !== undefined ? parsedSettings.use_brand_colors : true
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
