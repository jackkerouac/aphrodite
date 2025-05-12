import { pool } from '../db.js';
import logger from '../lib/logger.js';

/**
 * Get badge settings by user ID and badge type
 */
export const getBadgeSettingsByType = async (userId, badgeType) => {
  try {
    logger.info(`Getting ${badgeType} badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `SELECT * FROM unified_badge_settings WHERE user_id = $1 AND badge_type = $2`,
      [userId, badgeType]
    );
    
    if (result.rows.length === 0) {
      logger.info(`No ${badgeType} badge settings found for user ID: ${userId}`);
      return null;
    }
    
    // Parse properties JSON
    const badgeSettings = result.rows[0];
    if (badgeSettings.properties && typeof badgeSettings.properties === 'string') {
      try {
        badgeSettings.properties = JSON.parse(badgeSettings.properties);
      } catch (parseError) {
        logger.warn(`Error parsing properties JSON for ${badgeType} badge settings: ${parseError.message}`);
        badgeSettings.properties = {};
      }
    }
    
    logger.info(`Found ${badgeType} badge settings for user ID: ${userId}`);
    return badgeSettings;
  } catch (error) {
    logger.error(`Error getting ${badgeType} badge settings: ${error.message}`);
    throw error;
  }
};

/**
 * Get all badge settings for a user
 */
export const getAllBadgeSettings = async (userId) => {
  try {
    logger.info(`Getting all badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `SELECT * FROM unified_badge_settings WHERE user_id = $1`,
      [userId]
    );
    
    // Parse properties JSON for each badge setting
    const badgeSettings = result.rows.map(row => {
      if (row.properties && typeof row.properties === 'string') {
        try {
          row.properties = JSON.parse(row.properties);
        } catch (parseError) {
          logger.warn(`Error parsing properties JSON for ${row.badge_type} badge settings: ${parseError.message}`);
          row.properties = {};
        }
      }
      return row;
    });
    
    logger.info(`Found ${badgeSettings.length} badge settings for user ID: ${userId}`);
    return badgeSettings;
  } catch (error) {
    logger.error(`Error getting all badge settings: ${error.message}`);
    throw error;
  }
};

/**
 * Save or update badge settings
 */
export const upsertBadgeSettings = async (settings) => {
  try {
    logger.info(`Saving ${settings.badge_type} badge settings for user ID: ${settings.user_id}`);
    
    // Ensure all necessary properties are present
    const validatedSettings = validateBadgeSettings(settings);
    
    // Convert properties to JSON string if it's an object
    if (validatedSettings.properties && typeof validatedSettings.properties === 'object') {
      validatedSettings.properties = JSON.stringify(validatedSettings.properties);
    }
    
    // Determine if this is an update or insert
    const existingSettings = await getBadgeSettingsByType(settings.user_id, settings.badge_type);
    
    if (existingSettings) {
      // Update existing settings
      logger.info(`Updating existing ${settings.badge_type} badge settings for user ID: ${settings.user_id}`);
      
      // Build dynamic query based on available fields
      const updateFields = [];
      const queryParams = [];
      let paramIndex = 1;
      
      // Add each field that exists in the settings object
      for (const [key, value] of Object.entries(validatedSettings)) {
        // Skip user_id and badge_type as they are used for the WHERE clause
        if (key !== 'user_id' && key !== 'badge_type' && key !== 'id' && value !== undefined) {
          updateFields.push(`${key} = $${paramIndex}`);
          queryParams.push(value);
          paramIndex++;
        }
      }
      
      // Add updated_at timestamp
      updateFields.push(`updated_at = CURRENT_TIMESTAMP`);
      
      // Add WHERE clause parameters
      queryParams.push(settings.user_id);
      queryParams.push(settings.badge_type);
      
      const query = `
        UPDATE unified_badge_settings 
        SET ${updateFields.join(', ')}
        WHERE user_id = $${paramIndex} AND badge_type = $${paramIndex + 1}
        RETURNING *
      `;
      
      const result = await pool.query(query, queryParams);
      
      logger.info(`Successfully updated ${settings.badge_type} badge settings for user ID: ${settings.user_id}`);
      return parseDbResult(result.rows[0]);
    } else {
      // Insert new settings
      logger.info(`Creating new ${settings.badge_type} badge settings for user ID: ${settings.user_id}`);
      
      // Build dynamic query based on available fields
      const fields = [];
      const placeholders = [];
      const queryParams = [];
      let paramIndex = 1;
      
      // Add each field that exists in the settings object
      for (const [key, value] of Object.entries(validatedSettings)) {
        if (key !== 'id' && value !== undefined) {
          fields.push(key);
          placeholders.push(`$${paramIndex}`);
          queryParams.push(value);
          paramIndex++;
        }
      }
      
      const query = `
        INSERT INTO unified_badge_settings (
          ${fields.join(', ')},
          created_at,
          updated_at
        ) VALUES (
          ${placeholders.join(', ')},
          CURRENT_TIMESTAMP,
          CURRENT_TIMESTAMP
        )
        RETURNING *
      `;
      
      const result = await pool.query(query, queryParams);
      
      logger.info(`Successfully created ${settings.badge_type} badge settings for user ID: ${settings.user_id}`);
      return parseDbResult(result.rows[0]);
    }
  } catch (error) {
    logger.error(`Error saving ${settings.badge_type} badge settings: ${error.message}`);
    throw error;
  }
};

/**
 * Delete badge settings by user ID and badge type
 */
export const deleteBadgeSettings = async (userId, badgeType) => {
  try {
    logger.info(`Deleting ${badgeType} badge settings for user ID: ${userId}`);
    
    const result = await pool.query(
      `DELETE FROM unified_badge_settings WHERE user_id = $1 AND badge_type = $2 RETURNING *`,
      [userId, badgeType]
    );
    
    if (result.rows.length === 0) {
      logger.info(`No ${badgeType} badge settings found to delete for user ID: ${userId}`);
      return null;
    }
    
    logger.info(`Successfully deleted ${badgeType} badge settings for user ID: ${userId}`);
    return parseDbResult(result.rows[0]);
  } catch (error) {
    logger.error(`Error deleting ${badgeType} badge settings: ${error.message}`);
    throw error;
  }
};

/**
 * Helper function to validate badge settings
 */
const validateBadgeSettings = (settings) => {
  // Create a new object with validated values
  const validated = {
    user_id: settings.user_id,
    badge_type: settings.badge_type
  };
  
  // Validate general settings
  validated.badge_size = settings.badge_size !== undefined ? Number(settings.badge_size) : 100;
  validated.edge_padding = settings.edge_padding !== undefined ? Number(settings.edge_padding) : 10;
  validated.badge_position = settings.badge_position || getDefaultPosition(settings.badge_type);
  
  // For review badges only
  if (settings.badge_type === 'review' && settings.display_format) {
    validated.display_format = settings.display_format;
  }
  
  // Validate background settings
  validated.background_color = settings.background_color || '#000000';
  validated.background_opacity = settings.background_opacity !== undefined ? Number(settings.background_opacity) : 80;
  
  // Validate border settings
  validated.border_size = settings.border_size !== undefined ? Number(settings.border_size) : 2;
  validated.border_color = settings.border_color || '#FFFFFF';
  validated.border_opacity = settings.border_opacity !== undefined ? Number(settings.border_opacity) : 80;
  validated.border_radius = settings.border_radius !== undefined ? Number(settings.border_radius) : 5;
  validated.border_width = settings.border_width !== undefined ? Number(settings.border_width) : 1;
  
  // Validate shadow settings
  validated.shadow_enabled = settings.shadow_enabled !== undefined ? Boolean(settings.shadow_enabled) : false;
  validated.shadow_color = settings.shadow_color || '#000000';
  validated.shadow_blur = settings.shadow_blur !== undefined ? Number(settings.shadow_blur) : 10;
  validated.shadow_offset_x = settings.shadow_offset_x !== undefined ? Number(settings.shadow_offset_x) : 0;
  validated.shadow_offset_y = settings.shadow_offset_y !== undefined ? Number(settings.shadow_offset_y) : 0;
  
  // Validate properties
  if (settings.properties) {
    validated.properties = settings.properties;
  } else {
    // Set default properties based on badge type
    validated.properties = getDefaultProperties(settings.badge_type);
  }
  
  return validated;
};

/**
 * Helper to get default position based on badge type
 */
const getDefaultPosition = (badgeType) => {
  switch (badgeType) {
    case 'audio':
      return 'top-left';
    case 'resolution':
      return 'top-right';
    case 'review':
      return 'bottom-left';
    default:
      return 'top-left';
  }
};

/**
 * Helper to get default properties based on badge type
 */
const getDefaultProperties = (badgeType) => {
  switch (badgeType) {
    case 'audio':
      return { codec_type: 'dolby_atmos' };
    case 'resolution':
      return { resolution_type: '4k' };
    case 'review':
      return { 
        review_sources: ['imdb', 'rotten_tomatoes'],
        score_type: 'percentage'
      };
    default:
      return {};
  }
};

/**
 * Helper to parse database result
 */
const parseDbResult = (row) => {
  if (!row) return null;
  
  // Parse the properties JSON if it exists
  if (row.properties && typeof row.properties === 'string') {
    try {
      row.properties = JSON.parse(row.properties);
    } catch (error) {
      logger.warn(`Error parsing properties JSON: ${error.message}`);
      row.properties = {};
    }
  }
  
  return row;
};
