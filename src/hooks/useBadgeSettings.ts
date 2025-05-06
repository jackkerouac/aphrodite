import { useState, useEffect } from 'react';

interface BadgeSettings {
  audio: {
    enabled: boolean;
    format: string;
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  };
  resolution: {
    enabled: boolean;
    format: string;
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  };
  review: {
    enabled: boolean;
    source: 'tmdb' | 'imdb' | 'rottentomatoes';
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  };
}

// Default settings
const defaultSettings: BadgeSettings = {
  audio: {
    enabled: true,
    format: 'Dolby Atmos',
    position: 'top-right',
  },
  resolution: {
    enabled: true,
    format: '4K',
    position: 'top-left',
  },
  review: {
    enabled: true,
    source: 'tmdb',
    position: 'bottom-left',
  },
};

export function useBadgeSettings() {
  const [badgeSettings, setBadgeSettings] = useState<BadgeSettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would load from database or localStorage
    // For now, we'll just use the defaults and set loading to false
    setIsLoading(false);
  }, []);

  // Toggle badge enabled state
  const toggleBadge = (badgeType: keyof BadgeSettings) => {
    setBadgeSettings((prev) => ({
      ...prev,
      [badgeType]: {
        ...prev[badgeType],
        enabled: !prev[badgeType].enabled,
      },
    }));
  };

  // Update badge settings
  const updateBadgeSetting = (
    badgeType: keyof BadgeSettings,
    key: string,
    value: any
  ) => {
    setBadgeSettings((prev) => ({
      ...prev,
      [badgeType]: {
        ...prev[badgeType],
        [key]: value,
      },
    }));
  };

  return {
    badgeSettings,
    isLoading,
    toggleBadge,
    updateBadgeSetting,
  };
}
