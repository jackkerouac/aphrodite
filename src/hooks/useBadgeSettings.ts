import { useState, useEffect } from 'react';
import { AudioBadgeSettings } from '@/components/badges/types/AudioBadge';
import { ResolutionBadgeSettings } from '@/components/badges/types/ResolutionBadge';
import { ReviewBadgeSettings, ReviewSource } from '@/components/badges/types/ReviewBadge';

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
  position: {
    percentX: 5,
    percentY: 5,
  },
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
  position: {
    percentX: 5,
    percentY: 15,
  },
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
  position: {
    percentX: 5,
    percentY: 25,
  },
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

  // Load settings from local storage or API with a memoized getter
  useEffect(() => {
    // Keep track of mounted status to prevent updates after unmount
    let isMounted = true;
    // Create a unique cache key
    const settingsKey = `badgeSettings-${userId}-${type}`;
    
    const loadSettings = async () => {
      setIsLoading(true);
      try {
        // Try to load from local storage first
        const savedSettings = localStorage.getItem(settingsKey);
        
        // Only update state if component is still mounted
        if (!isMounted) return;
        
        if (savedSettings) {
          try {
            const parsedSettings = JSON.parse(savedSettings);
            
            // No need to constrain the size anymore since badge size is now determined by the codec image
            // The size property is still kept for backward compatibility but isn't used for audio badges
            
            // Merge with default settings to ensure all properties exist
            const defaultSettings = getDefaultSettings<T>(type);
            setBadgeSettings({ ...defaultSettings, ...parsedSettings });
          } catch (parseError) {
            console.error(`Error parsing ${type} badge settings:`, parseError);
            // Use default settings if parsing fails
            const defaultSettings = getDefaultSettings<T>(type);
            setBadgeSettings(defaultSettings);
            // Save default settings to localStorage
            localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
          }
        } else {
          // If not found in local storage, use default settings
          const defaultSettings = getDefaultSettings<T>(type);
          setBadgeSettings(defaultSettings);
          // Save default settings to localStorage for future use
          localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
        }
      } catch (error) {
        console.error(`Error loading ${type} badge settings:`, error);
        // Fall back to default settings if component is still mounted
        if (isMounted) {
          const defaultSettings = getDefaultSettings<T>(type);
          setBadgeSettings(defaultSettings);
          // Try to save default settings to localStorage
          try {
            localStorage.setItem(settingsKey, JSON.stringify(defaultSettings));
          } catch (saveError) {
            console.error(`Error saving default ${type} badge settings:`, saveError);
          }
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
   * Save badge settings with immediate UI update
   */
  const saveBadgeSettings = async (newSettings: T) => {
    console.log(`saveBadgeSettings called for ${type} with:`, newSettings);
    try {
      // Create a unique key for the settings
      const settingsKey = `badgeSettings-${userId}-${type}`;
      
      // Make sure to include default settings for any missing properties
      const defaultSettings = getDefaultSettings<T>(type);
      const mergedSettings = { ...defaultSettings, ...newSettings };
      
      console.log(`Settings after merging with defaults:`, mergedSettings);
      
      // Update state IMMEDIATELY for responsive UI
      setBadgeSettings(mergedSettings);
      
      // Save to local storage immediately for real-time updates
      try {
        console.log(`Saving settings to localStorage with key: ${settingsKey}`);
        localStorage.setItem(settingsKey, JSON.stringify(mergedSettings));
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
