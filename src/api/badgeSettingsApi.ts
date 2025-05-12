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
      const response = await api.get(`/api/v1/unified-badge-settings/${badgeType}?user_id=${userId}`);
      return response.data;
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
      // Validate settings object
      if (!settings.badge_type) {
        throw new Error('Badge type is required');
      }
      
      if (!settings.user_id) {
        throw new Error('User ID is required');
      }
      
      const response = await api.post(`/api/v1/unified-badge-settings/${settings.badge_type}`, settings);
      return response.data;
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
      // Validate settings objects
      for (const setting of settings) {
        if (!setting.badge_type) {
          throw new Error('Badge type is required for all settings');
        }
        
        if (!setting.user_id) {
          throw new Error('User ID is required for all settings');
        }
      }
      
      const response = await api.post('/api/v1/unified-badge-settings/batch', settings);
      return response.data;
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
