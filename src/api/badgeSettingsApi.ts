import { api } from '@/lib/api';
import {
  UnifiedBadgeSettings,
  AudioBadgeSettings,
  ResolutionBadgeSettings,
  ReviewBadgeSettings,
  DEFAULT_AUDIO_BADGE_SETTINGS,
  DEFAULT_RESOLUTION_BADGE_SETTINGS,
  DEFAULT_REVIEW_BADGE_SETTINGS
} from '@/types/unifiedBadgeSettings';

/**
 * Create a clean badge object without any prototype issues
 * This ensures all the badge objects have the expected structure
 * DO NOT override existing values with defaults - only provide defaults for missing properties
 */
const createCleanBadgeObject = (badgeType: 'audio' | 'resolution' | 'review', userId: string | number, properties: any, existingBadge?: any): UnifiedBadgeSettings => {
  // Create base object depending on badge type with sensible defaults
  // These will only be used if the existing badge doesn't have these properties
  let defaultValues: any = {
    user_id: String(userId),
    badge_type: badgeType,
    badge_size: badgeType === 'audio' ? 200 : badgeType === 'resolution' ? 194 : 231, // Match preview default sizes
    edge_padding: 30, // Larger padding for better appearance
    background_color: badgeType === 'audio' ? '#05ed2e' : badgeType === 'resolution' ? '#e220e8' : '#d12125', // Custom colors
    background_opacity: 80,
    border_size: 2,
    border_color: '#FFFFFF',
    border_opacity: 80,
    border_radius: badgeType === 'review' ? 13 : 10,
    border_width: 1,
    shadow_enabled: badgeType !== 'review', // No shadow for review badges
    shadow_color: '#000000',
    shadow_blur: badgeType === 'review' ? 10 : 8,
    shadow_offset_x: badgeType === 'review' ? 0 : 2,
    shadow_offset_y: badgeType === 'review' ? 0 : 2,
    properties: {}
  };
  
  // Add type-specific default properties
  switch (badgeType) {
    case 'audio':
      defaultValues.badge_position = 'top-left';
      defaultValues.properties = { codec_type: 'dolby_atmos' };
      break;
    case 'resolution':
      defaultValues.badge_position = 'top-right';
      defaultValues.properties = { resolution_type: '4k' };
      break;
    case 'review':
      defaultValues.badge_position = 'bottom-left';
      defaultValues.properties = { 
        review_sources: ['imdb', 'rotten_tomatoes'],
        score_type: 'percentage'
      };
      defaultValues.display_format = 'vertical'; // Vertical looks better for reviews
      break;
  }
  
  // If we have an existing badge, use its values and only fill in missing properties
  if (existingBadge) {
    // Start with the defaults
    const mergedBadge = { ...defaultValues };
    
    // Override with existing badge properties (don't lose any custom settings)
    Object.entries(existingBadge).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        (mergedBadge as any)[key] = value;
      }
    });
    
    // Ensure badge_type is correct
    mergedBadge.badge_type = badgeType;
    
    // Ensure properties are merged correctly (don't lose custom property settings)
    if (existingBadge.properties) {
      mergedBadge.properties = {
        ...defaultValues.properties,
        ...existingBadge.properties
      };
    }
    
    console.log(`Using enhanced badge for ${badgeType}:`, {
      badge_size: mergedBadge.badge_size,
      background_color: mergedBadge.background_color,
      display_format: mergedBadge.display_format
    });
    
    return mergedBadge;
  }
  
  // If no existing badge, return the defaults
  return defaultValues;
};

/**
 * API endpoints for badge settings
 */
export const badgeSettingsApi = {
  /**
   * Get all badge settings for a user
   */
  getAll: async (userId: string | number = '1'): Promise<UnifiedBadgeSettings[]> => {
    try {
      const response = await api.get(`/api/v1/unified-badge-settings?user_id=${userId}`);
      
      // Transform response to ensure all required badge types exist
      const data = response.data || [];
      const audioBadge = data.find((badge: UnifiedBadgeSettings) => badge.badge_type === 'audio');
      const resolutionBadge = data.find((badge: UnifiedBadgeSettings) => badge.badge_type === 'resolution');
      const reviewBadge = data.find((badge: UnifiedBadgeSettings) => badge.badge_type === 'review');
      
      const result: UnifiedBadgeSettings[] = [];
      
      // Add found badges or defaults
      if (audioBadge) {
        result.push(audioBadge as AudioBadgeSettings);
      } else {
        result.push({
          ...DEFAULT_AUDIO_BADGE_SETTINGS,
          user_id: userId
        });
      }
      
      if (resolutionBadge) {
        result.push(resolutionBadge as ResolutionBadgeSettings);
      } else {
        result.push({
          ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
          user_id: userId
        });
      }
      
      if (reviewBadge) {
        result.push(reviewBadge as ReviewBadgeSettings);
      } else {
        result.push({
          ...DEFAULT_REVIEW_BADGE_SETTINGS,
          user_id: userId
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error fetching badge settings:', error);
      throw error;
    }
  },
  
  /**
   * Get badge settings by type
   */
  getByType: async (badgeType: string, userId: string | number = '1'): Promise<UnifiedBadgeSettings> => {
    try {
      console.log(`Direct API call - Getting ${badgeType} badge settings for user ID: ${userId}`);
      const response = await api.get(`/api/v1/unified-badge-settings/${badgeType}?user_id=${userId}`);
      console.log(`Direct API call - Raw response for ${badgeType} badge:`, response);
      
      // Handle different response formats - some endpoints return {success: true, data: {...}}
      // while others return the data directly
      if (response.data && response.data.success && response.data.data) {
        console.log(`Direct API call - Extracted ${badgeType} badge data:`, response.data.data);
        console.log(`Direct API call - Badge size is:`, response.data.data.badge_size);
        return response.data.data;
      }
      
      // Handle direct response format
      console.log(`Direct API call - Standard response for ${badgeType} badge:`, response.data);
      if (response.data) {
        console.log(`Direct API call - Badge size is:`, response.data.badge_size);
        return response.data;
      }
      
      // If we get here, something is wrong with the response
      console.error(`Direct API call - Unexpected response format for ${badgeType} badge:`, response);
      throw new Error(`Unexpected response format for ${badgeType} badge`);
    } catch (error) {
      console.error(`Error fetching ${badgeType} badge settings:`, error);
      
      // Return default settings based on badge type
      let defaultSettings: UnifiedBadgeSettings;
      
      switch (badgeType) {
        case 'audio':
          defaultSettings = {
            ...DEFAULT_AUDIO_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        case 'resolution':
          defaultSettings = {
            ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        case 'review':
          defaultSettings = {
            ...DEFAULT_REVIEW_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        default:
          throw new Error(`Invalid badge type: ${badgeType}`);
      }
      
      return defaultSettings;
    }
  },
  
  /**
   * Save badge settings
   */
  save: async (settings: UnifiedBadgeSettings): Promise<UnifiedBadgeSettings> => {
    try {
      // Ensure we're working with a clean copy of the settings
      const inputSettings = JSON.parse(JSON.stringify(settings)) as UnifiedBadgeSettings;
      
      // Validate settings object and ensure badge type
      if (!inputSettings.badge_type) {
        throw new Error('Badge type is required');
      }
      
      if (!inputSettings.user_id) {
        inputSettings.user_id = '1';
      }
      
      // Force the badge_type to be one of the allowed values as a string
      inputSettings.badge_type = String(inputSettings.badge_type).toLowerCase();
      
      // Check if badge_type is one of the allowed values
      if (!['audio', 'resolution', 'review'].includes(inputSettings.badge_type)) {
        throw new Error(`Invalid badge type: ${inputSettings.badge_type}. Must be one of: audio, resolution, review`);
      }
      
      // Use our enhanced helper function to create a clean badge object that preserves values
      // from the original badge and only fills in missing properties with defaults
      const validatedSettings = createCleanBadgeObject(
        inputSettings.badge_type as 'audio' | 'resolution' | 'review',
        inputSettings.user_id,
        inputSettings.properties || {},
        inputSettings // Pass the original badge to preserve its values
      );
      
      // Convert user_id to string
      validatedSettings.user_id = String(validatedSettings.user_id);
      
      console.log(`Saving ${validatedSettings.badge_type} badge settings with size ${validatedSettings.badge_size} and color ${validatedSettings.background_color}:`, validatedSettings);
      
      // Try to save with a dedicated endpoint for each badge type
      const endpoint = `/api/v1/unified-badge-settings/${validatedSettings.badge_type}`;
      console.log(`Using API endpoint: ${endpoint}`);
      
      try {
        const response = await api.post(endpoint, validatedSettings);
        return response.data;
      } catch (error) {
        console.error(`Error with first save attempt for ${validatedSettings.badge_type} badge:`, error);
        
        // If that fails, try a more generic approach
        console.log('Trying alternative save approach...');
        const alternativeResponse = await api.post('/api/v1/unified-badge-settings', validatedSettings);
        return alternativeResponse.data;
      }
    } catch (error) {
      console.error('Error saving badge settings:', error);
      throw error;
    }
  },
  
  /**
   * Save multiple badge settings at once
   */
  saveAll: async (settings: UnifiedBadgeSettings[]): Promise<UnifiedBadgeSettings[]> => {
    try {
      // Validate settings objects and ensure badge types are correctly set
      const validatedSettings = settings.map(setting => {
        // Make a deep copy to avoid reference issues
        let validSetting = JSON.parse(JSON.stringify(setting));
        
        // Ensure badge_type is one of the allowed values
        if (!validSetting.badge_type || 
            !['audio', 'resolution', 'review'].includes(validSetting.badge_type)) {
          console.error(`Invalid badge_type in settings:`, validSetting);
          // Try to determine badge type from properties
          if (validSetting.hasOwnProperty('properties')) {
            const props = validSetting.properties as any;
            if (props && props.hasOwnProperty('codec_type')) {
              validSetting.badge_type = 'audio';
            } else if (props && props.hasOwnProperty('resolution_type')) {
              validSetting.badge_type = 'resolution';
            } else if (props && props.hasOwnProperty('review_sources')) {
              validSetting.badge_type = 'review';
            } else {
              // Can't determine badge type, use a default based on other properties
              if (validSetting.hasOwnProperty('display_format')) {
                validSetting.badge_type = 'review';
              } else {
                console.error('Could not determine badge type from properties');
                throw new Error('Badge type is required and must be one of: audio, resolution, review');
              }
            }
          } else {
            throw new Error('Badge type is required and must be one of: audio, resolution, review');
          }
        }
        
        // Use our enhanced helper function to create a clean badge object that preserves values
        // from the original badge and only fills in missing properties with defaults
        const cleanBadge = createCleanBadgeObject(
          validSetting.badge_type as 'audio' | 'resolution' | 'review',
          validSetting.user_id || '1',
          validSetting.properties || {},
          validSetting // Pass the original badge to preserve its values
        );
        
        console.log(`Processed badge settings for saveAll: ${cleanBadge.badge_type}`, {
          badge_size: cleanBadge.badge_size,
          background_color: cleanBadge.background_color,
          display_format: cleanBadge.display_format
        });
        
        return cleanBadge;
      });
      
      // Try to save each badge individually instead of using batch
      console.log('Attempting to save badges individually instead of batch');
      const results = [];
      
      for (const badge of validatedSettings) {
        try {
          const result = await badgeSettingsApi.save(badge);
          results.push(result);
        } catch (error) {
          console.error(`Error saving ${badge.badge_type} badge:`, error);
          // Continue with other badges even if one fails
        }
      }
      
      // Only try batch save if individual saves didn't work
      if (results.length === 0) {
        // Log the validated settings before sending
        console.log('Falling back to batch save, sending validated badge settings to API:', validatedSettings);
        
        // Convert to a plain object to avoid prototype issues
        const plainSettings = JSON.parse(JSON.stringify(validatedSettings));
        
        try {
          // First try using individual endpoints
          const response = await api.post('/api/v1/unified-badge-settings/batch', plainSettings);
          return response.data;
        } catch (batchError) {
          console.error('Error with batch save:', batchError);
          throw batchError;
        }
      }
      
      return results;
    } catch (error) {
      console.error('Error saving badge settings:', error);
      throw error;
    }
  },
  
  /**
   * Delete badge settings
   */
  delete: async (badgeType: string, userId: string | number = '1'): Promise<void> => {
    try {
      await api.delete(`/api/v1/unified-badge-settings/${badgeType}?user_id=${userId}`);
    } catch (error) {
      console.error(`Error deleting ${badgeType} badge settings:`, error);
      throw error;
    }
  },
  
  /**
   * Reset badge settings to defaults
   */
  reset: async (badgeType: string, userId: string | number = '1'): Promise<UnifiedBadgeSettings> => {
    try {
      // First delete existing settings
      await badgeSettingsApi.delete(badgeType, userId);
      
      // Then return default settings based on badge type
      let defaultSettings: UnifiedBadgeSettings;
      
      switch (badgeType) {
        case 'audio':
          defaultSettings = {
            ...DEFAULT_AUDIO_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        case 'resolution':
          defaultSettings = {
            ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        case 'review':
          defaultSettings = {
            ...DEFAULT_REVIEW_BADGE_SETTINGS,
            user_id: userId
          };
          break;
        default:
          throw new Error(`Invalid badge type: ${badgeType}`);
      }
      
      // Save the default settings
      return await badgeSettingsApi.save(defaultSettings);
    } catch (error) {
      console.error(`Error resetting ${badgeType} badge settings:`, error);
      throw error;
    }
  }
};
