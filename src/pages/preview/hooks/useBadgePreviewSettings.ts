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

// Hook for managing badge display settings in preview
export const useBadgePreviewSettings = (): UseBadgePreviewSettingsReturn => {
  const [displaySettings, setDisplaySettings] = useState<BadgeDisplaySettings>(defaultDisplaySettings);
  const [loading, setLoading] = useState(true);

  // Load settings from localStorage if available
  useEffect(() => {
    try {
      setLoading(true);
      const savedSettings = localStorage.getItem('badgePreviewSettings');
      if (savedSettings) {
        setDisplaySettings(JSON.parse(savedSettings));
      }
    } catch (error) {
      console.error('Error loading badge preview settings from localStorage:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save settings to localStorage when they change
  useEffect(() => {
    try {
      if (!loading) {
        localStorage.setItem('badgePreviewSettings', JSON.stringify(displaySettings));
      }
    } catch (error) {
      console.error('Error saving badge preview settings to localStorage:', error);
    }
  }, [displaySettings, loading]);

  // Function to toggle a badge's visibility
  const toggleBadge = (badgeName: keyof BadgeDisplaySettings) => {
    setDisplaySettings(prev => ({
      ...prev,
      [badgeName]: !prev[badgeName]
    }));
  };

  return {
    displaySettings,
    toggleBadge,
    loading
  };
};
