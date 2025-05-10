import { useState, useEffect } from 'react';

// Default badge state key for localStorage
const STORAGE_KEY = 'badgePreviewSettings';

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

// Hook for managing badge display settings in preview
export const useBadgePreviewSettings = (): UseBadgePreviewSettingsReturn => {
  const [displaySettings, setDisplaySettings] = useState<BadgeDisplaySettings>(defaultDisplaySettings);
  const [loading, setLoading] = useState(true);

  // On initial load, get settings from the database and fallback to localStorage if needed
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        
        // Load from localStorage first for immediate UI response
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        let initialSettings = defaultDisplaySettings;
        
        if (savedSettings) {
          try {
            const parsedSettings = JSON.parse(savedSettings);
            if (parsedSettings && 
                typeof parsedSettings.showAudioBadge === 'boolean' &&
                typeof parsedSettings.showResolutionBadge === 'boolean' &&
                typeof parsedSettings.showReviewBadge === 'boolean') {
              initialSettings = parsedSettings;
              console.log('Loaded settings from localStorage:', parsedSettings);
            }
          } catch (parseError) {
            console.error('Failed to parse settings JSON', parseError);
          }
        }
        
        // Then try to load from the database (which should be the source of truth)
        try {
          const userId = '123'; // Hardcoded user ID
          const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
          
          // Fetch all badge settings in parallel
          const [audioResponse, resolutionResponse, reviewResponse] = await Promise.all([
            fetch(`${apiBaseUrl}/audio-badge-settings/${userId}`),
            fetch(`${apiBaseUrl}/resolution-badge-settings/${userId}`),
            fetch(`${apiBaseUrl}/review-badge-settings/${userId}`)
          ]);
          
          // Process audio badge settings
          if (audioResponse.ok) {
            const audioSettings = await audioResponse.json();
            if (audioSettings && typeof audioSettings.enabled === 'boolean') {
              initialSettings.showAudioBadge = audioSettings.enabled;
              console.log('Loaded audio badge enabled state from database:', audioSettings.enabled);
            }
          }
          
          // Process resolution badge settings
          if (resolutionResponse.ok) {
            const resolutionSettings = await resolutionResponse.json();
            if (resolutionSettings && typeof resolutionSettings.enabled === 'boolean') {
              initialSettings.showResolutionBadge = resolutionSettings.enabled;
              console.log('Loaded resolution badge enabled state from database:', resolutionSettings.enabled);
            }
          }
          
          // Process review badge settings
          if (reviewResponse.ok) {
            const reviewSettings = await reviewResponse.json();
            if (reviewSettings && typeof reviewSettings.enabled === 'boolean') {
              initialSettings.showReviewBadge = reviewSettings.enabled;
              console.log('Loaded review badge enabled state from database:', reviewSettings.enabled);
            }
          }
          
          // Update the UI with the combined settings
          setDisplaySettings(initialSettings);
          console.log('Final display settings after database load:', initialSettings);
          
        } catch (dbError) {
          console.error('Error loading settings from database:', dbError);
          setDisplaySettings(initialSettings);
        }
        
      } catch (error) {
        console.error('Error accessing localStorage:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadSettings();
  }, []);

  // Save settings to localStorage when they change
  useEffect(() => {
    if (!loading) {
      try {
        // Save to localStorage for persistence
        localStorage.setItem(STORAGE_KEY, JSON.stringify(displaySettings));
        console.log('Saved settings to localStorage:', displaySettings);
        
        // Also save to database if possible (simple direct API calls)
        const saveToDatabase = async () => {
          const userId = '123'; // Hardcoded user ID
          const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
          
          // Simple direct calls to update the database with the enabled state
          // These will fail silently if the settings don't exist yet
          try {
            // Audio badge enabled state
            const audioResponse = await fetch(`${apiBaseUrl}/audio-badge-settings/${userId}/enabled`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ enabled: displaySettings.showAudioBadge })
            });
            
            if (!audioResponse.ok) {
              console.error('Failed to update audio badge enabled state:', await audioResponse.text());
            } else {
              console.log('Audio badge enabled state updated successfully');
            }
            
            // Resolution badge enabled state
            const resolutionResponse = await fetch(`${apiBaseUrl}/resolution-badge-settings/${userId}/enabled`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ enabled: displaySettings.showResolutionBadge })
            });
            
            if (!resolutionResponse.ok) {
              console.error('Failed to update resolution badge enabled state:', await resolutionResponse.text());
            } else {
              console.log('Resolution badge enabled state updated successfully');
            }
            
            // Review badge enabled state
            const reviewResponse = await fetch(`${apiBaseUrl}/review-badge-settings/${userId}/enabled`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ enabled: displaySettings.showReviewBadge })
            });
            
            if (!reviewResponse.ok) {
              console.error('Failed to update review badge enabled state:', await reviewResponse.text());
            } else {
              console.log('Review badge enabled state updated successfully');
            }
            
            console.log('All badge enabled states sent to database');
          } catch (error) {
            console.error('Error saving enabled state to database:', error);
          }
        };
        
        saveToDatabase();
      } catch (error) {
        console.error('Error saving settings:', error);
      }
    }
  }, [displaySettings, loading]);

  const toggleBadge = (badgeName: keyof BadgeDisplaySettings) => {
    setDisplaySettings(prevSettings => {
      const currentValue = prevSettings[badgeName];
      const newSettings = {
        ...prevSettings,
        [badgeName]: !currentValue
      };
      
      console.log(`Toggling ${badgeName} from ${currentValue} to ${!currentValue}`);
      return newSettings;
    });
  };

  return {
    displaySettings,
    toggleBadge,
    loading
  };
};
