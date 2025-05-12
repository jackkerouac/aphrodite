import { renderHook, act } from '@testing-library/react-hooks';
import { usePreviewState } from '@/hooks/usePreviewState';

describe('usePreviewState', () => {
  it('initializes with default values', () => {
    const { result } = renderHook(() => usePreviewState());
    
    // Check default initial values
    expect(result.current.theme).toBe('light');
    expect(result.current.visibleBadges).toEqual(['audio', 'resolution', 'review']);
    expect(result.current.highlightedBadge).toBeNull();
  });
  
  it('initializes with provided values', () => {
    const { result } = renderHook(() => usePreviewState({
      initialTheme: 'dark',
      initialVisibleBadges: ['audio', 'resolution']
    }));
    
    // Check custom initial values
    expect(result.current.theme).toBe('dark');
    expect(result.current.visibleBadges).toEqual(['audio', 'resolution']);
  });
  
  it('toggles theme correctly', () => {
    const { result } = renderHook(() => usePreviewState({ initialTheme: 'light' }));
    
    // Toggle theme from light to dark
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('dark');
    
    // Toggle theme from dark to light
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('light');
  });
  
  it('sets theme explicitly', () => {
    const { result } = renderHook(() => usePreviewState({ initialTheme: 'light' }));
    
    // Set theme to dark
    act(() => {
      result.current.setTheme('dark');
    });
    expect(result.current.theme).toBe('dark');
    
    // Set theme to light
    act(() => {
      result.current.setTheme('light');
    });
    expect(result.current.theme).toBe('light');
  });
  
  it('toggles badge visibility correctly', () => {
    const { result } = renderHook(() => usePreviewState({
      initialVisibleBadges: ['audio', 'resolution']
    }));
    
    // Toggle resolution (should remove it)
    act(() => {
      result.current.toggleBadgeVisibility('resolution');
    });
    expect(result.current.visibleBadges).toEqual(['audio']);
    
    // Toggle review (should add it)
    act(() => {
      result.current.toggleBadgeVisibility('review');
    });
    expect(result.current.visibleBadges).toEqual(['audio', 'review']);
  });
  
  it('sets badge visibility explicitly', () => {
    const { result } = renderHook(() => usePreviewState({
      initialVisibleBadges: ['audio', 'resolution']
    }));
    
    // Hide audio
    act(() => {
      result.current.setBadgeVisibility('audio', false);
    });
    expect(result.current.visibleBadges).toEqual(['resolution']);
    
    // Show review
    act(() => {
      result.current.setBadgeVisibility('review', true);
    });
    expect(result.current.visibleBadges).toEqual(['resolution', 'review']);
    
    // Try to show resolution again (already visible, should have no effect)
    act(() => {
      result.current.setBadgeVisibility('resolution', true);
    });
    expect(result.current.visibleBadges).toEqual(['resolution', 'review']);
  });
  
  it('manages highlighted badge correctly', () => {
    const { result } = renderHook(() => usePreviewState());
    
    // Set highlighted badge
    act(() => {
      result.current.setHighlightedBadge('audio');
    });
    expect(result.current.highlightedBadge).toBe('audio');
    expect(result.current.isHighlighted('audio')).toBe(true);
    expect(result.current.isHighlighted('resolution')).toBe(false);
    
    // Clear highlighted badge
    act(() => {
      result.current.setHighlightedBadge(null);
    });
    expect(result.current.highlightedBadge).toBeNull();
    expect(result.current.isHighlighted('audio')).toBe(false);
  });
});
