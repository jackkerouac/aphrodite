import { useState, useCallback } from 'react';

/**
 * Options for the usePreviewState hook
 */
interface UsePreviewStateOptions {
  initialTheme?: 'light' | 'dark';
  initialVisibleBadges?: string[];
}

/**
 * Return type for the usePreviewState hook
 */
interface UsePreviewStateResult {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  
  visibleBadges: string[];
  toggleBadgeVisibility: (badgeType: string) => void;
  setBadgeVisibility: (badgeType: string, isVisible: boolean) => void;
  
  isHighlighted: (badgeType: string) => boolean;
  setHighlightedBadge: (badgeType: string | null) => void;
  highlightedBadge: string | null;
}

/**
 * Custom hook for managing preview state (theme, badge visibility, highlighting)
 */
export const usePreviewState = (
  options: UsePreviewStateOptions = {}
): UsePreviewStateResult => {
  const { 
    initialTheme = 'light',
    initialVisibleBadges = ['audio', 'resolution', 'review']
  } = options;

  // Theme state
  const [theme, setThemeState] = useState<'light' | 'dark'>(initialTheme);
  
  // Visible badges state
  const [visibleBadges, setVisibleBadges] = useState<string[]>(initialVisibleBadges);
  
  // Highlighted badge state (for active editing)
  const [highlightedBadge, setHighlightedBadge] = useState<string | null>(null);

  // Toggle theme
  const toggleTheme = useCallback(() => {
    setThemeState(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  }, []);

  // Set theme explicitly
  const setTheme = useCallback((newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
  }, []);

  // Toggle badge visibility
  const toggleBadgeVisibility = useCallback((badgeType: string) => {
    setVisibleBadges(prevVisible => {
      if (prevVisible.includes(badgeType)) {
        return prevVisible.filter(type => type !== badgeType);
      } else {
        return [...prevVisible, badgeType];
      }
    });
  }, []);

  // Set badge visibility explicitly
  const setBadgeVisibility = useCallback((badgeType: string, isVisible: boolean) => {
    setVisibleBadges(prevVisible => {
      if (isVisible && !prevVisible.includes(badgeType)) {
        return [...prevVisible, badgeType];
      } else if (!isVisible && prevVisible.includes(badgeType)) {
        return prevVisible.filter(type => type !== badgeType);
      }
      return prevVisible;
    });
  }, []);

  // Check if a badge is highlighted
  const isHighlighted = useCallback((badgeType: string) => {
    return highlightedBadge === badgeType;
  }, [highlightedBadge]);

  return {
    theme,
    toggleTheme,
    setTheme,
    visibleBadges,
    toggleBadgeVisibility,
    setBadgeVisibility,
    isHighlighted,
    setHighlightedBadge,
    highlightedBadge
  };
};

export default usePreviewState;
