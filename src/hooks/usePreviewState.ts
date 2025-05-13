import { useState, useCallback, useEffect } from 'react';

// Types of badges
export const BADGE_TYPES = ['audio', 'resolution', 'review'] as const;
export type BadgeType = typeof BADGE_TYPES[number];

/**
 * Options for the usePreviewState hook
 */
interface UsePreviewStateOptions {
  initialTheme?: 'light' | 'dark';
  initialVisibleBadges?: BadgeType[];
  initialHighlightedBadge?: BadgeType | null;
  onHighlightChange?: (badgeType: BadgeType | null) => void;
  persistPreferences?: boolean;
}

/**
 * Return type for the usePreviewState hook
 */
interface UsePreviewStateResult {
  // Theme state
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  
  // Badge visibility
  visibleBadges: BadgeType[];
  toggleBadgeVisibility: (badgeType: BadgeType) => void;
  setBadgeVisibility: (badgeType: BadgeType, isVisible: boolean) => void;
  isVisible: (badgeType: BadgeType) => boolean;
  
  // Badge highlighting (for active editing)
  isHighlighted: (badgeType: BadgeType) => boolean;
  setHighlightedBadge: (badgeType: BadgeType | null) => void;
  highlightedBadge: BadgeType | null;
  
  // Reset state
  resetState: () => void;
}

// Local storage keys
const STORAGE_KEY_PREFIX = 'aphrodite_preview_';
const THEME_STORAGE_KEY = `${STORAGE_KEY_PREFIX}theme`;
const VISIBLE_BADGES_STORAGE_KEY = `${STORAGE_KEY_PREFIX}visible_badges`;

/**
 * Custom hook for managing preview state (theme, badge visibility, highlighting)
 * with persistence to localStorage
 */
export const usePreviewState = (
  options: UsePreviewStateOptions = {}
): UsePreviewStateResult => {
  const { 
    initialTheme = 'light',
    initialVisibleBadges = BADGE_TYPES,
    initialHighlightedBadge = null,
    onHighlightChange = undefined,
    persistPreferences = true
  } = options;

  // Load theme preference from storage or use initial value
  const loadTheme = useCallback((): 'light' | 'dark' => {
    if (!persistPreferences) return initialTheme;
    
    try {
      const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      return (storedTheme === 'light' || storedTheme === 'dark') 
        ? storedTheme 
        : initialTheme;
    } catch (error) {
      console.error('Error loading theme preference from localStorage:', error);
      return initialTheme;
    }
  }, [initialTheme, persistPreferences]);

  // Load visible badges preference from storage or use initial value
  const loadVisibleBadges = useCallback((): BadgeType[] => {
    if (!persistPreferences) return initialVisibleBadges;
    
    try {
      const storedVisibleBadges = localStorage.getItem(VISIBLE_BADGES_STORAGE_KEY);
      
      if (storedVisibleBadges) {
        const parsed = JSON.parse(storedVisibleBadges);
        
        // Validate that parsed data is an array of valid badge types
        if (Array.isArray(parsed) && parsed.every(type => BADGE_TYPES.includes(type as BadgeType))) {
          return parsed as BadgeType[];
        }
      }
      
      return initialVisibleBadges;
    } catch (error) {
      console.error('Error loading visible badges preference from localStorage:', error);
      return initialVisibleBadges;
    }
  }, [initialVisibleBadges, persistPreferences]);

  // Theme state
  const [theme, setThemeState] = useState<'light' | 'dark'>(loadTheme);
  
  // Visible badges state
  const [visibleBadges, setVisibleBadges] = useState<BadgeType[]>(loadVisibleBadges);
  
  // Highlighted badge state (for active editing)
  const [highlightedBadge, setHighlightedBadgeState] = useState<BadgeType | null>(initialHighlightedBadge);
  
  // Force reload preferences from localStorage on mount or when dependencies change
  useEffect(() => {
    setThemeState(loadTheme());
    setVisibleBadges(loadVisibleBadges());
  }, [loadTheme, loadVisibleBadges]);

  // Save preferences to localStorage when they change
  useEffect(() => {
    if (!persistPreferences) return;
    
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
      console.error('Error saving theme preference to localStorage:', error);
    }
  }, [theme, persistPreferences]);

  useEffect(() => {
    if (!persistPreferences) return;
    
    try {
      localStorage.setItem(VISIBLE_BADGES_STORAGE_KEY, JSON.stringify(visibleBadges));
    } catch (error) {
      console.error('Error saving visible badges preference to localStorage:', error);
    }
  }, [visibleBadges, persistPreferences]);

  // Invoke callback when highlighted badge changes
  useEffect(() => {
    if (onHighlightChange) {
      onHighlightChange(highlightedBadge);
    }
  }, [highlightedBadge, onHighlightChange]);

  // Toggle theme
  const toggleTheme = useCallback(() => {
    setThemeState(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  }, []);

  // Set theme explicitly
  const setTheme = useCallback((newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
  }, []);

  // Toggle badge visibility
  const toggleBadgeVisibility = useCallback((badgeType: BadgeType) => {
    setVisibleBadges(prevVisible => {
      if (prevVisible.includes(badgeType)) {
        return prevVisible.filter(type => type !== badgeType);
      } else {
        return [...prevVisible, badgeType];
      }
    });
  }, []);

  // Set badge visibility explicitly
  const setBadgeVisibility = useCallback((badgeType: BadgeType, isVisible: boolean) => {
    setVisibleBadges(prevVisible => {
      if (isVisible && !prevVisible.includes(badgeType)) {
        return [...prevVisible, badgeType];
      } else if (!isVisible && prevVisible.includes(badgeType)) {
        return prevVisible.filter(type => type !== badgeType);
      }
      return prevVisible;
    });
  }, []);

  // Check if a badge is visible
  const isVisible = useCallback((badgeType: BadgeType) => {
    return visibleBadges.includes(badgeType);
  }, [visibleBadges]);

  // Check if a badge is highlighted
  const isHighlighted = useCallback((badgeType: BadgeType) => {
    return highlightedBadge === badgeType;
  }, [highlightedBadge]);

  // Set highlighted badge
  const setHighlightedBadge = useCallback((badgeType: BadgeType | null) => {
    setHighlightedBadgeState(badgeType);
  }, []);

  // Reset state to defaults
  const resetState = useCallback(() => {
    setThemeState(initialTheme);
    setVisibleBadges(initialVisibleBadges);
    setHighlightedBadgeState(initialHighlightedBadge);
  }, [initialTheme, initialVisibleBadges, initialHighlightedBadge]);

  return {
    theme,
    toggleTheme,
    setTheme,
    visibleBadges,
    toggleBadgeVisibility,
    setBadgeVisibility,
    isVisible,
    isHighlighted,
    setHighlightedBadge,
    highlightedBadge,
    resetState
  };
};

export default usePreviewState;

// Add a cleanup utility function to help with debugging
export const clearPreviewStateStorage = () => {
  try {
    localStorage.removeItem(THEME_STORAGE_KEY);
    localStorage.removeItem(VISIBLE_BADGES_STORAGE_KEY);
    return true;
  } catch (error) {
    console.error('Error clearing preview state storage:', error);
    return false;
  }
};
