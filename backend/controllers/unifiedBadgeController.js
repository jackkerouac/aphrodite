import { 
  getBadgeSettingsByType, 
  getAllBadgeSettings, 
  upsertBadgeSettings, 
  deleteBadgeSettings 
} from '../models/unifiedBadgeSettings.js';
import logger from '../lib/logger.js';

/**
 * Get badge settings by type
 */
export const getBadgeSettings = async (req, res) => {
  try {
    const userId = req.params.userId;
    const badgeType = req.params.badgeType;
    
    if (!userId || !badgeType) {
      return res.status(400).json({
        success: false,
        message: 'User ID and badge type are required'
      });
    }
    
    if (!['audio', 'resolution', 'review'].includes(badgeType)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid badge type. Must be one of: audio, resolution, review'
      });
    }
    
    const badgeSettings = await getBadgeSettingsByType(userId, badgeType);
    
    if (!badgeSettings) {
      // Return default settings if none exist
      return res.status(200).json({
        success: true,
        data: getDefaultSettings(userId, badgeType)
      });
    }
    
    return res.status(200).json({
      success: true,
      data: badgeSettings
    });
  } catch (error) {
    logger.error(`Error getting badge settings: ${error.message}`);
    return res.status(500).json({
      success: false,
      message: 'Failed to get badge settings',
      error: error.message
    });
  }
};

/**
 * Get all badge settings for a user
 */
export const getAllBadgeSettingsForUser = async (req, res) => {
  try {
    const userId = req.params.userId;
    
    if (!userId) {
      return res.status(400).json({
        success: false,
        message: 'User ID is required'
      });
    }
    
    const badgeSettings = await getAllBadgeSettings(userId);
    
    // If user has no settings, return default settings for all badge types
    if (!badgeSettings || badgeSettings.length === 0) {
      const defaultSettings = [
        getDefaultSettings(userId, 'audio'),
        getDefaultSettings(userId, 'resolution'),
        getDefaultSettings(userId, 'review')
      ];
      
      return res.status(200).json({
        success: true,
        data: defaultSettings
      });
    }
    
    // Check if all badge types exist, add defaults for missing ones
    const audioSettings = badgeSettings.find(s => s.badge_type === 'audio');
    const resolutionSettings = badgeSettings.find(s => s.badge_type === 'resolution');
    const reviewSettings = badgeSettings.find(s => s.badge_type === 'review');
    
    const result = [...badgeSettings];
    
    if (!audioSettings) {
      result.push(getDefaultSettings(userId, 'audio'));
    }
    
    if (!resolutionSettings) {
      result.push(getDefaultSettings(userId, 'resolution'));
    }
    
    if (!reviewSettings) {
      result.push(getDefaultSettings(userId, 'review'));
    }
    
    return res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error(`Error getting all badge settings: ${error.message}`);
    return res.status(500).json({
      success: false,
      message: 'Failed to get all badge settings',
      error: error.message
    });
  }
};

/**
 * Save badge settings
 */
export const saveBadgeSettings = async (req, res) => {
  try {
    const userId = req.params.userId;
    const badgeType = req.params.badgeType;
    const settings = req.body;
    
    if (!userId || !badgeType) {
      return res.status(400).json({
        success: false,
        message: 'User ID and badge type are required'
      });
    }
    
    if (!['audio', 'resolution', 'review'].includes(badgeType)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid badge type. Must be one of: audio, resolution, review'
      });
    }
    
    // Ensure the user_id and badge_type are correctly set in the settings object
    settings.user_id = userId;
    settings.badge_type = badgeType;
    
    // Save the settings
    const savedSettings = await upsertBadgeSettings(settings);
    
    return res.status(200).json({
      success: true,
      data: savedSettings,
      message: `${badgeType} badge settings saved successfully`
    });
  } catch (error) {
    logger.error(`Error saving badge settings: ${error.message}`);
    return res.status(500).json({
      success: false,
      message: 'Failed to save badge settings',
      error: error.message
    });
  }
};

/**
 * Delete badge settings
 */
export const deleteBadgeSettingsHandler = async (req, res) => {
  try {
    const userId = req.params.userId;
    const badgeType = req.params.badgeType;
    
    if (!userId || !badgeType) {
      return res.status(400).json({
        success: false,
        message: 'User ID and badge type are required'
      });
    }
    
    if (!['audio', 'resolution', 'review'].includes(badgeType)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid badge type. Must be one of: audio, resolution, review'
      });
    }
    
    const result = await deleteBadgeSettings(userId, badgeType);
    
    if (!result) {
      return res.status(404).json({
        success: false,
        message: `No ${badgeType} badge settings found for user ID: ${userId}`
      });
    }
    
    return res.status(200).json({
      success: true,
      data: result,
      message: `${badgeType} badge settings deleted successfully`
    });
  } catch (error) {
    logger.error(`Error deleting badge settings: ${error.message}`);
    return res.status(500).json({
      success: false,
      message: 'Failed to delete badge settings',
      error: error.message
    });
  }
};

/**
 * Helper function to get default settings
 */
const getDefaultSettings = (userId, badgeType) => {
  const settings = {
    user_id: userId,
    badge_type: badgeType,
    badge_size: 100,
    edge_padding: 10,
    background_color: '#000000',
    background_opacity: 80,
    border_size: 2,
    border_color: '#FFFFFF',
    border_opacity: 80,
    border_radius: 5,
    border_width: 1,
    shadow_enabled: false,
    shadow_color: '#000000',
    shadow_blur: 10,
    shadow_offset_x: 0,
    shadow_offset_y: 0
  };
  
  // Add type-specific defaults
  switch (badgeType) {
    case 'audio':
      settings.badge_position = 'top-left';
      settings.properties = { codec_type: 'dolby_atmos' };
      break;
    case 'resolution':
      settings.badge_position = 'top-right';
      settings.properties = { resolution_type: '4k' };
      break;
    case 'review':
      settings.badge_position = 'bottom-left';
      settings.display_format = 'horizontal';
      settings.properties = { 
        review_sources: ['imdb', 'rotten_tomatoes'],
        score_type: 'percentage'
      };
      break;
  }
  
  return settings;
};
