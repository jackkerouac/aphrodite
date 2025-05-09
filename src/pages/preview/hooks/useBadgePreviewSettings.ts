import { useState, useEffect } from 'react';

// Type definition for badge display settings
export interface BadgeDisplaySettings {
  showAudioBadge: boolean;
  showResolutionBadge: boolean;
  showReviewBadge: boolean;
}

// Type definition for hook return
export interface UseBadgePreviewSettingsReturn {
  displaySettings: BadgeDisplaySettings;
  toggleBadge: (badgeName: keyof BadgeDisplaySettings) => void;
  loading: boolean;
}

// Default settings
const defaultDisplaySettings: BadgeDisplaySettings = {
  showAudioBadge: true,
  showResolutionBadge: true,
  showReviewBadge: true
};

// Key for localStorage
const STORAGE_KEY = 'badgePreviewSettings';

// Hook for managing badge display settings in preview
export const useBadgePreviewSettings = (): UseBadgePreviewSettingsReturn => {
  const [displaySettings, setDisplaySettings] = useState<BadgeDisplaySettings>(defaultDisplaySettings);
  const [loading, setLoading] = useState(true);

  // Complete rewrite of localStorage handling
  useEffect(() => {
    const loadSettings = () => {
      try {
        setLoading(true);
        // Clear any potentially corrupted settings
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
          try {
            const parsedSettings = JSON.parse(savedSettings);
            // Validate that all expected keys exist
            if (parsedSettings && 
                typeof parsedSettings.showAudioBadge === 'boolean' &&
                typeof parsedSettings.showResolutionBadge === 'boolean' &&
                typeof parsedSettings.showReviewBadge === 'boolean') {
              setDisplaySettings(parsedSettings);
              console.log('Loaded settings:', parsedSettings);
            } else {
              console.warn('Invalid settings format in localStorage, using defaults');
              // Use defaults but don't save yet to avoid overwriting
              setDisplaySettings(defaultDisplaySettings);
            }
          } catch (parseError) {
            console.error('Failed to parse settings JSON', parseError);
            setDisplaySettings(defaultDisplaySettings);
          }
        } else {
          // First time user, use defaults
          console.log('No saved settings found, using defaults');
          setDisplaySettings(defaultDisplaySettings);
          // Save defaults immediately
          localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultDisplaySettings));
        }
      } catch (error) {
        console.error('Error accessing localStorage:', error);
        setDisplaySettings(defaultDisplaySettings);
      } finally {
        setLoading(false);
      }
    };
    
    loadSettings();
  }, []);
  
  // Save settings to localStorage when they change, but only after initial load
  useEffect(() => {
    if (!loading) {
      try {
        console.log('Saving settings to localStorage:', displaySettings);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(displaySettings));
      } catch (error) {
        console.error('Error saving badge preview settings to localStorage:', error);
      }
    }
  }, [displaySettings, loading]);

  // Completely rewritten toggle function to ensure atomic updates
  const toggleBadge = (badgeName: keyof BadgeDisplaySettings) => {
    // Force immediate update with functional setState
    setDisplaySettings(prevSettings => {
      // Get the current value to toggle
      const currentValue = prevSettings[badgeName];
      // Create new state object with the toggled value
      const newSettings = {
        ...prevSettings,
        [badgeName]: !currentValue
      };
      
      // Log the change for debugging
      console.log(`Toggling ${badgeName} from ${currentValue} to ${!currentValue}`);
      console.log('New display settings:', newSettings);
      
      // Return the new state object
      return newSettings;
    });
  };

  return {
    displaySettings,
    toggleBadge,
    loading
  };
};
