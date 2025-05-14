import { api } from '@/lib/api';
import {
  UnifiedBadgeSettings,
  AudioBadgeSettings,
  ResolutionBadgeSettings,
  ReviewBadgeSettings
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
      console.log(`Getting all badge settings for user ID: ${userId}`);
      const response = await api.get(`/api/v1/unified-badge-settings?user_id=${userId}`);
      
      // Just return what's in the database directly
      const data = response.data || [];
      console.log(`Retrieved ${data.length} badge settings from database`, 
        data.map((b: any) => `${b.badge_type}: size=${b.badge_size}, color=${b.background_color}`));
      return data;
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
      console.log(`Getting ${badgeType} badge settings for user ID: ${userId}`);
      const response = await api.get(`/api/v1/unified-badge-settings/${badgeType}?user_id=${userId}`);
      
      // Handle different response formats - some endpoints return {success: true, data: {...}}
      // while others return the data directly
      if (response.data && response.data.success && response.data.data) {
        console.log(`Retrieved ${badgeType} badge:`, response.data.data);
        return response.data.data;
      }
      
      // Handle direct response format
      console.log(`Retrieved ${badgeType} badge:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${badgeType} badge settings:`, error);
      throw error;
    }
  },
  
  /**
   * Save badge settings
   */
  save: async (settings: UnifiedBadgeSettings): Promise<UnifiedBadgeSettings> => {
    try {
      // Create a clean copy of the settings without any reference issues
      const cleanSettings = JSON.parse(JSON.stringify(settings));
      
      // Minimal validation: ensure badge_type is one of the allowed values
      if (!cleanSettings.badge_type || !['audio', 'resolution', 'review'].includes(cleanSettings.badge_type)) {
        throw new Error(`Invalid badge type: ${cleanSettings.badge_type}. Must be one of: audio, resolution, review`);
      }
      
      // Ensure user_id is present
      if (!cleanSettings.user_id) {
        cleanSettings.user_id = '1';
      }
      
      // Convert user_id to string for consistency
      cleanSettings.user_id = String(cleanSettings.user_id);
      
      console.log(`Saving ${cleanSettings.badge_type} badge settings:`, {
        badge_size: cleanSettings.badge_size,
        background_color: cleanSettings.background_color,
        position: cleanSettings.badge_position,
        display_format: cleanSettings.display_format
      });
      
      const endpoint = `/api/v1/unified-badge-settings/${cleanSettings.badge_type}`;
      const response = await api.post(endpoint, cleanSettings);
      
      console.log(`Successfully saved ${cleanSettings.badge_type} badge`);
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
      // Create clean copies of all settings
      const cleanSettings = settings.map(setting => {
        // Deep copy to avoid reference issues
        const cleanSetting = JSON.parse(JSON.stringify(setting));
        
        // Minimal validation: ensure badge_type is present and valid
        if (!cleanSetting.badge_type || !['audio', 'resolution', 'review'].includes(cleanSetting.badge_type)) {
          console.error(`Invalid badge type: ${cleanSetting.badge_type}. Skipping.`);
          return null;
        }
        
        // Ensure user_id is present
        if (!cleanSetting.user_id) {
          cleanSetting.user_id = '1';
        }
        
        // Convert user_id to string for consistency
        cleanSetting.user_id = String(cleanSetting.user_id);
        
        return cleanSetting;
      }).filter(Boolean); // Remove any null entries
      
      // Log what we're about to save
      console.log(`Saving ${cleanSettings.length} badge settings:`, 
        cleanSettings.map(b => `${b.badge_type}: size=${b.badge_size}, color=${b.background_color}`));
      
      // Save each badge individually for reliability
      const results = [];
      for (const badge of cleanSettings) {
        try {
          const result = await badgeSettingsApi.save(badge);
          results.push(result);
        } catch (error) {
          console.error(`Error saving ${badge.badge_type} badge:`, error);
          // Continue with other badges even if one fails
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
  }
};
