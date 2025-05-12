import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { usePreviewState, BadgeType, BADGE_TYPES } from '../usePreviewState';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value.toString();
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    store
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('usePreviewState', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => usePreviewState());

    expect(result.current.theme).toBe('light');
    expect(result.current.visibleBadges).toEqual(BADGE_TYPES);
    expect(result.current.highlightedBadge).toBeNull();
  });

  it('should initialize with provided values', () => {
    const { result } = renderHook(() => usePreviewState({
      initialTheme: 'dark',
      initialVisibleBadges: ['audio'],
      initialHighlightedBadge: 'resolution'
    }));

    expect(result.current.theme).toBe('dark');
    expect(result.current.visibleBadges).toEqual(['audio']);
    expect(result.current.highlightedBadge).toBe('resolution');
  });

  it('should toggle theme', () => {
    const { result } = renderHook(() => usePreviewState());

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('dark');

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('light');
  });

  it('should set theme directly', () => {
    const { result } = renderHook(() => usePreviewState());

    act(() => {
      result.current.setTheme('dark');
    });

    expect(result.current.theme).toBe('dark');
  });

  it('should toggle badge visibility', () => {
    const { result } = renderHook(() => usePreviewState());

    // All badges should be visible initially
    expect(result.current.visibleBadges).toContain('audio');
    
    // Toggle 'audio' badge off
    act(() => {
      result.current.toggleBadgeVisibility('audio');
    });

    expect(result.current.visibleBadges).not.toContain('audio');
    expect(result.current.isVisible('audio')).toBe(false);
    
    // Toggle 'audio' badge on again
    act(() => {
      result.current.toggleBadgeVisibility('audio');
    });

    expect(result.current.visibleBadges).toContain('audio');
    expect(result.current.isVisible('audio')).toBe(true);
  });

  it('should set badge visibility directly', () => {
    const { result } = renderHook(() => usePreviewState());

    // Hide 'resolution' badge
    act(() => {
      result.current.setBadgeVisibility('resolution', false);
    });

    expect(result.current.visibleBadges).not.toContain('resolution');
    
    // Show 'resolution' badge
    act(() => {
      result.current.setBadgeVisibility('resolution', true);
    });

    expect(result.current.visibleBadges).toContain('resolution');
  });

  it('should set highlighted badge', () => {
    const { result } = renderHook(() => usePreviewState());

    // Initially, no badge is highlighted
    expect(result.current.highlightedBadge).toBeNull();
    
    // Highlight 'audio' badge
    act(() => {
      result.current.setHighlightedBadge('audio');
    });

    expect(result.current.highlightedBadge).toBe('audio');
    expect(result.current.isHighlighted('audio')).toBe(true);
    expect(result.current.isHighlighted('resolution')).toBe(false);
    
    // Change highlighted badge
    act(() => {
      result.current.setHighlightedBadge('resolution');
    });

    expect(result.current.highlightedBadge).toBe('resolution');
    expect(result.current.isHighlighted('audio')).toBe(false);
    expect(result.current.isHighlighted('resolution')).toBe(true);
    
    // Clear highlighted badge
    act(() => {
      result.current.setHighlightedBadge(null);
    });

    expect(result.current.highlightedBadge).toBeNull();
  });

  it('should reset state to defaults', () => {
    const { result } = renderHook(() => usePreviewState({
      initialTheme: 'light',
      initialVisibleBadges: BADGE_TYPES,
      initialHighlightedBadge: null
    }));

    // Change some state
    act(() => {
      result.current.setTheme('dark');
      result.current.setBadgeVisibility('audio', false);
      result.current.setHighlightedBadge('resolution');
    });

    expect(result.current.theme).toBe('dark');
    expect(result.current.visibleBadges).not.toContain('audio');
    expect(result.current.highlightedBadge).toBe('resolution');
    
    // Reset state
    act(() => {
      result.current.resetState();
    });

    // Should be back to defaults
    expect(result.current.theme).toBe('light');
    expect(result.current.visibleBadges).toEqual(BADGE_TYPES);
    expect(result.current.highlightedBadge).toBeNull();
  });

  it('should call onHighlightChange when highlighted badge changes', () => {
    const onHighlightChange = vi.fn();
    const { result } = renderHook(() => usePreviewState({
      onHighlightChange
    }));

    // Should have been called once with null on mount
    expect(onHighlightChange).toHaveBeenCalledTimes(1);
    expect(onHighlightChange).toHaveBeenCalledWith(null);
    
    // Change highlighted badge
    act(() => {
      result.current.setHighlightedBadge('audio');
    });

    // Should have been called again with 'audio'
    expect(onHighlightChange).toHaveBeenCalledTimes(2);
    expect(onHighlightChange).toHaveBeenCalledWith('audio');
  });

  it('should persist preferences to localStorage when enabled', () => {
    const { result } = renderHook(() => usePreviewState({
      persistPreferences: true
    }));

    // Change theme
    act(() => {
      result.current.setTheme('dark');
    });

    // Change visibility
    act(() => {
      result.current.setBadgeVisibility('audio', false);
    });

    // Check localStorage calls
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'aphrodite_preview_theme',
      'dark'
    );
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'aphrodite_preview_visible_badges',
      JSON.stringify(['resolution', 'review'])
    );
  });

  it('should load preferences from localStorage when available', () => {
    // Set up localStorage with some pre-existing values
    localStorageMock.setItem('aphrodite_preview_theme', 'dark');
    localStorageMock.setItem('aphrodite_preview_visible_badges', JSON.stringify(['audio']));

    const { result } = renderHook(() => usePreviewState({
      persistPreferences: true
    }));

    // Should use the values from localStorage
    expect(result.current.theme).toBe('dark');
    expect(result.current.visibleBadges).toEqual(['audio']);
  });

  it('should not persist preferences when disabled', () => {
    const { result } = renderHook(() => usePreviewState({
      persistPreferences: false
    }));

    // Change theme
    act(() => {
      result.current.setTheme('dark');
    });

    // Change visibility
    act(() => {
      result.current.setBadgeVisibility('audio', false);
    });

    // Should not have called localStorage setItem
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
  });
});
