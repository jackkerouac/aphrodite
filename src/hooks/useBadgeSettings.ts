import { useState, useEffect } from 'react';
import { AudioBadgeSettings } from '@/components/badges/types/AudioBadge';
import { ResolutionBadgeSettings } from '@/components/badges/types/ResolutionBadge';
import { ReviewBadgeSettings, ReviewSource } from '@/components/badges/types/ReviewBadge';
import apiClient from '@/lib/api-client';
import { BadgePosition } from '@/components/badges/PositionSelector';

export type BadgeType = 'audio' | 'resolution' | 'review';

// Default settings for each badge type
const defaultAudioBadgeSettings: AudioBadgeSettings = {
  type: 'audio',
  size: 80,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  borderRadius: 5,
  textColor: '#FFFFFF',
  codecType: 'Dolby Atmos',
  fontSize: 24,
  position: BadgePosition.TopLeft,
  margin: 16,
};

const defaultResolutionBadgeSettings: ResolutionBadgeSettings = {
  type: 'resolution',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  borderRadius: 5,
  textColor: '#FFFFFF',
  resolutionType: '4K',
  fontSize: 36,
  position: BadgePosition.TopRight,
  margin: 16,
};

const defaultReviewBadgeSettings: ReviewBadgeSettings = {
  type: 'review',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  borderRadius: 5,
  textColor: '#FFFFFF',
  fontSize: 18,
  displayFormat: 'horizontal',
  maxSourcesToShow: 2,
  showDividers: true,
  sources: [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ],
  position: BadgePosition.BottomLeft,
  margin: 16,
};

/**
 * Get default settings for a specific badge type
 */
const getDefaultSettings = <T>(type: BadgeType): T => {
  switch (type) {
    case 'audio':
      return defaultAudioBadgeSettings as unknown as T;
    case 'resolution':
      return defaultResolutionBadgeSettings as unknown as T;
    case 'review':
      return defaultReviewBadgeSettings as unknown as T;
    default:
      return defaultAudioBadgeSettings as unknown as T;
  }
};

/**
 * Hook for managing badge settings
 * @param userId The user ID
 * @param type The badge type
 * @returns Object containing badge settings and functions to manage them
 */
export const useBadgeSettings = <T>(
  userId: string,
  type: BadgeType
) => {
  const [badgeSettings, setBadgeSettings] = useState<T>(getDefaultSettings<T>(type));
  const [isLoading, setIsLoading] = useState(true);

  // Load settings from API first, then fall back to local storage
  useEffect(() => {
    // Keep track of mounted status to prevent updates after unmount
    let isMounted = true;
    // Create a unique cache key
    const settingsKey = `badgeSettings-${userId}-${type}`;
    
    const loadSettings = async () => {
      setIsLoading(true);
      try {
        // First try to load from API
        let fetchedSettings = null;
        
        try {
          console.log(`Attempting to load ${type} badge settings from API for user ${userId}`);
          if (type === 'audio') {
            fetchedSettings = await apiClient.audioBadge.getSettings(userId);
          } else if (type === 'resolution') {
            fetchedSettings = await apiClient.resolutionBadge.getSettings(userId);
          } else if (type === 'review') {
            fetchedSettings = await apiClient.reviewBadge.getSettings(userId);
          }
          
          if (fetchedSettings) {
            console.log(`Successfully loaded ${type} badge settings from API:`, fetchedSettings);
            
            // Convert snake_case to camelCase for frontend use
            const convertedSettings: any = {};
            // First copy all properties as-is
            Object.keys(fetchedSettings).forEach(key => {
              convertedSettings[key] = fetchedSettings[key];
            });
            
            // Then map specific snake_case properties to camelCase
            if (type === 'audio') {
              convertedSettings.codecType = fetchedSettings.codec_type || fetchedSettings.audio_codec_type;
              convertedSettings.backgroundColor = fetchedSettings.background_color;
              convertedSettings.backgroundOpacity = fetchedSettings.background_opacity || fetchedSettings.background_transparency;
              convertedSettings.borderRadius = fetchedSettings.border_radius;
              convertedSettings.borderWidth = fetchedSettings.border_width;
              convertedSettings.borderColor = fetchedSettings.border_color;
              convertedSettings.borderOpacity = fetchedSettings.border_opacity || fetchedSettings.border_transparency;
              convertedSettings.shadowEnabled = fetchedSettings.shadow_enabled || fetchedSettings.shadow_toggle;
              convertedSettings.shadowColor = fetchedSettings.shadow_color;
              convertedSettings.shadowBlur = fetchedSettings.shadow_blur || fetchedSettings.shadow_blur_radius;
              convertedSettings.shadowOffsetX = fetchedSettings.shadow_offset_x;
              convertedSettings.shadowOffsetY = fetchedSettings.shadow_offset_y;
              convertedSettings.zIndex = fetchedSettings.z_index;
              convertedSettings.textColor = fetchedSettings.text_color;
              convertedSettings.fontFamily = fetchedSettings.font_family;
              convertedSettings.fontSize = fetchedSettings.font_size;
              convertedSettings.useBrandColors = fetchedSettings.use_brand_colors;
            } else if (type === 'resolution') {
              convertedSettings.resolutionType = fetchedSettings.resolution_type;
              convertedSettings.backgroundColor = fetchedSettings.background_color;
              convertedSettings.backgroundOpacity = fetchedSettings.background_opacity || fetchedSettings.background_transparency;
              convertedSettings.borderRadius = fetchedSettings.border_radius;
              convertedSettings.borderWidth = fetchedSettings.border_width;
              convertedSettings.borderColor = fetchedSettings.border_color;
              convertedSettings.borderOpacity = fetchedSettings.border_opacity || fetchedSettings.border_transparency;
              convertedSettings.shadowEnabled = fetchedSettings.shadow_enabled || fetchedSettings.shadow_toggle;
              convertedSettings.shadowColor = fetchedSettings.shadow_color;
              convertedSettings.shadowBlur = fetchedSettings.shadow_blur || fetchedSettings.shadow_blur_radius;
              convertedSettings.shadowOffsetX = fetchedSettings.shadow_offset_x;
              convertedSettings.shadowOffsetY = fetchedSettings.shadow_offset_y;
              convertedSettings.zIndex = fetchedSettings.z_index;
              convertedSettings.textColor = fetchedSettings.text_color;
              convertedSettings.fontFamily = fetchedSettings.font_family;
              convertedSettings.fontSize = fetchedSettings.font_size;
              convertedSettings.useBrandColors = fetchedSettings.use_brand_colors;
            } else if (type === 'review') {
              convertedSettings.displayFormat = fetchedSettings.badge_layout; 
              convertedSettings.displaySources = fetchedSettings.display_sources;
              convertedSettings.sourceOrder = fetchedSettings.source_order;
              convertedSettings.showLogo = fetchedSettings.show_logo;
              convertedSettings.logoSize = fetchedSettings.logo_size;
              convertedSettings.logoPosition = fetchedSettings.logo_position;
              convertedSettings.logoTextSpacing = fetchedSettings.logo_text_spacing;
              convertedSettings.scoreFormat = fetchedSettings.score_format;
              convertedSettings.backgroundColor = fetchedSettings.background_color;
              convertedSettings.backgroundOpacity = fetchedSettings.background_opacity || fetchedSettings.background_transparency;
              convertedSettings.borderRadius = fetchedSettings.border_radius;
              convertedSettings.borderWidth = fetchedSettings.border_width;
              convertedSettings.borderColor = fetchedSettings.border_color;
              convertedSettings.borderOpacity = fetchedSettings.border_opacity || fetchedSettings.border_transparency;
              convertedSettings.shadowEnabled = fetchedSettings.shadow_enabled || fetchedSettings.shadow_toggle;
              convertedSettings.shadowColor = fetchedSettings.shadow_color;
              convertedSettings.shadowBlur = fetchedSettings.shadow_blur || fetchedSettings.shadow_blur_radius;
              convertedSettings.shadowOffsetX = fetchedSettings.shadow_offset_x;
              convertedSettings.shadowOffsetY = fetchedSettings.shadow_offset_y;
              convertedSettings.zIndex = fetchedSettings.z_index;
              convertedSettings.fontFamily = fetchedSettings.font_family;
              convertedSettings.fontSize = fetchedSettings.font_size;
              convertedSettings.fontWeight = fetchedSettings.font_weight;
              convertedSettings.textColor = fetchedSettings.text_color;
              convertedSettings.textOpacity = fetchedSettings.text_opacity || fetchedSettings.text_transparency;
              convertedSettings.maxSourcesToShow = fetchedSettings.max_sources_to_show;
              convertedSettings.useBrandColors = fetchedSettings.use_brand_colors;
            }
            
            // Handle position conversion - from string to enum
            if (typeof fetchedSettings.position === 'string') {
              // Convert position from snake-case string to BadgePosition enum
              const positionStr = fetchedSettings.position;
              const formattedPosition = positionStr
                .split('-')
                .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
                .join('');
                
              // Find the matching BadgePosition value
              convertedSettings.position = BadgePosition[formattedPosition as keyof typeof BadgePosition] || 
                                         (type === 'audio' ? BadgePosition.TopLeft : 
                                         (type === 'resolution' ? BadgePosition.TopRight : BadgePosition.BottomLeft));
            }
            
            // Make sure to include type
            convertedSettings.type = type;
            
            console.log(`Converted API settings to frontend format:`, convertedSettings);
            
            // Update local storage with the latest API settings
            localStorage.setItem(settingsKey, JSON.stringify(convertedSettings));
            
            // Default settings for merging to ensure all properties exist
            const defaultSettings = getDefaultSettings<T>(type);
            
            // Only update state if component is still mounted
            if (isMounted) {
              setBadgeSettings({ ...defaultSettings, ...convertedSettings as unknown as T });
              setIsLoading(false);
              return; // Success - no need to proceed further
            }
          }
        } catch (apiError) {
          console.warn(`Could not load ${type} badge settings from API:`, apiError);
          // Continue to local storage as fallback
        }
      } catch (error) {
        console.error(`Error loading ${type} badge settings:`, error);
        // If the API call failed or didn't return valid settings, try localStorage as fallback
        const savedSettings = localStorage.getItem(settingsKey);
        
        // Only update state if component is still mounted
        if (!isMounted) return;
        
        if (savedSettings) {
          try {
            const parsedSettings = JSON.parse(savedSettings);
            
            // Validate that the saved settings have the correct type
            if (parsedSettings.type && parsedSettings.type !== type) {
              console.warn(`Saved settings had incorrect type: ${parsedSettings.type}, expected: ${type}. Using defaults.`);
              const defaultSettings = getDefaultSettings<T>(type);
              setBadgeSettings(defaultSettings);
              // Save correct defaults to localStorage
              localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
              return;
            }
            
            // Merge with default settings to ensure all properties exist
            const defaultSettings = getDefaultSettings<T>(type);
            setBadgeSettings({ ...defaultSettings, ...parsedSettings });
          } catch (parseError) {
            console.error(`Error parsing ${type} badge settings from localStorage:`, parseError);
            // Use default settings if parsing fails
            const defaultSettings = getDefaultSettings<T>(type);
            setBadgeSettings(defaultSettings);
            // Save default settings to localStorage
            localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
          }
        } else {
          // If not found in localStorage either, use default settings
          const defaultSettings = getDefaultSettings<T>(type);
          setBadgeSettings(defaultSettings);
          // Save default settings to localStorage for future use
          localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
        }
      } finally {
        // Only update loading state if component is still mounted
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadSettings();
    
    // Cleanup function to prevent state updates after unmounting
    return () => {
      isMounted = false;
    };
  }, [userId, type]);

  /**
   * Save badge settings with immediate UI update and API persistence
   */
  const saveBadgeSettings = async (newSettings: T) => {
    console.log(`saveBadgeSettings called for ${type} with:`, newSettings);
    
    if (type === 'audio') {
      // Special debug for background color
      console.log('Audio badge background color before save:', 
                 (newSettings as any).backgroundColor, 
                 'Type:', typeof (newSettings as any).backgroundColor);
    }
    
    try {
      // Create a unique key for the settings
      const settingsKey = `badgeSettings-${userId}-${type}`;
      
      // Ensure the type field matches the badge type to prevent cross-contamination
      const settingsWithCorrectType = {
        ...newSettings,
        type: type // Force the correct type
      };
      
      // Make sure to include default settings for any missing properties
      const defaultSettings = getDefaultSettings<T>(type);
      const mergedSettings = { ...defaultSettings, ...settingsWithCorrectType };
      
      console.log(`Settings after merging with defaults:`, mergedSettings);
      
      // Update state IMMEDIATELY for responsive UI
      setBadgeSettings(mergedSettings);
      
      // Save to local storage immediately for real-time updates
      try {
        console.log(`Saving settings to localStorage with key: ${settingsKey}`);
        localStorage.setItem(settingsKey, JSON.stringify(mergedSettings));
        
        // Also save to backend API
        console.log(`Saving ${type} badge settings to backend API`);
        const apiSettings = { ...mergedSettings };
        
        // Map fields to match API expectations
        let savedToApi = false;
        
        // Explicit handling for the background color
        if (apiSettings.backgroundColor) {
          apiSettings.background_color = apiSettings.backgroundColor;
          console.log(`Explicitly mapping backgroundColor (${apiSettings.backgroundColor}) to background_color`);
        }
        
        try {
          if (type === 'audio') {
            console.log('Audio badge settings being sent to API:');
            console.log('- backgroundColor:', apiSettings.backgroundColor);
            console.log('- background_color:', apiSettings.background_color);
            console.log('- Size:', apiSettings.size);
            await apiClient.audioBadge.saveSettings(apiSettings, userId);
            savedToApi = true;
          } else if (type === 'resolution') {
            await apiClient.resolutionBadge.saveSettings(apiSettings, userId);
            savedToApi = true;
          } else if (type === 'review') {
            await apiClient.reviewBadge.saveSettings(apiSettings, userId);
            savedToApi = true;
          }
          
          console.log(`Successfully saved ${type} badge settings to backend API`);
        } catch (apiError) {
          console.error(`Error saving ${type} badge settings to API:`, apiError);
          // If API save fails but localStorage succeeds, we'll at least have the visual updates
          if (!savedToApi) {
            console.warn(`Settings were saved to localStorage but not to the backend API. Changes may not persist across sessions.`);
          }
        }
      } catch (storageError) {
        console.error(`Error saving ${type} badge settings to localStorage:`, storageError);
      }
      
      return true;
    } catch (error) {
      console.error(`Error saving ${type} badge settings:`, error);
      return false;
    }
  };

  /**
   * Reset badge settings to defaults
   */
  const resetBadgeSettings = () => {
    const defaultSettings = getDefaultSettings<T>(type);
    saveBadgeSettings(defaultSettings);
    return defaultSettings;
  };

  return { 
    badgeSettings, 
    saveBadgeSettings, 
    resetBadgeSettings,
    isLoading
  };
};
