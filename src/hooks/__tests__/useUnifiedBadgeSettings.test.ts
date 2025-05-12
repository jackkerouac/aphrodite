import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import { vi } from 'vitest';

import { useUnifiedBadgeSettings } from '../useUnifiedBadgeSettings';
import { badgeSettingsApi } from '@/api/badgeSettingsApi';
import {
  AudioBadgeSettings,
  ResolutionBadgeSettings,
  ReviewBadgeSettings
} from '@/types/unifiedBadgeSettings';

// Mock the badgeSettingsApi
vi.mock('@/api/badgeSettingsApi', () => ({
  badgeSettingsApi: {
    getAll: vi.fn(),
    getByType: vi.fn(),
    save: vi.fn(),
    saveAll: vi.fn(),
    delete: vi.fn(),
    reset: vi.fn()
  }
}));

// Mock the toast notifications
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}));

// Setup a QueryClient wrapper for tests
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('useUnifiedBadgeSettings', () => {
  // Sample badge settings for tests
  const mockAudioBadge: AudioBadgeSettings = {
    user_id: '1',
    badge_type: 'audio',
    badge_size: 100,
    edge_padding: 10,
    badge_position: 'top-left',
    background_color: '#000000',
    background_opacity: 80,
    border_size: 2,
    border_color: '#FFFFFF',
    border_opacity: 80,
    border_radius: 5,
    border_width: 1,
    shadow_enabled: false,
    shadow_color: '#000000',
    shadow_blur: 10,
    shadow_offset_x: 0,
    shadow_offset_y: 0,
    properties: {
      codec_type: 'dolby_atmos'
    }
  };

  const mockResolutionBadge: ResolutionBadgeSettings = {
    user_id: '1',
    badge_type: 'resolution',
    badge_size: 120,
    edge_padding: 15,
    badge_position: 'top-right',
    background_color: '#111111',
    background_opacity: 70,
    border_size: 3,
    border_color: '#EEEEEE',
    border_opacity: 90,
    border_radius: 8,
    border_width: 2,
    shadow_enabled: true,
    shadow_color: '#333333',
    shadow_blur: 15,
    shadow_offset_x: 2,
    shadow_offset_y: 2,
    properties: {
      resolution_type: '4k'
    }
  };

  const mockReviewBadge: ReviewBadgeSettings = {
    user_id: '1',
    badge_type: 'review',
    badge_size: 80,
    edge_padding: 8,
    badge_position: 'bottom-left',
    background_color: '#222222',
    background_opacity: 60,
    border_size: 1,
    border_color: '#DDDDDD',
    border_opacity: 75,
    border_radius: 4,
    border_width: 1,
    shadow_enabled: false,
    shadow_color: '#000000',
    shadow_blur: 5,
    shadow_offset_x: 1,
    shadow_offset_y: 1,
    display_format: 'horizontal',
    properties: {
      review_sources: ['imdb', 'rotten_tomatoes'],
      score_type: 'percentage'
    }
  };

  const mockAllBadges = [
    mockAudioBadge,
    mockResolutionBadge,
    mockReviewBadge
  ];

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
    
    // Setup default mock implementations
    (badgeSettingsApi.getAll as vi.Mock).mockResolvedValue(mockAllBadges);
    (badgeSettingsApi.save as vi.Mock).mockImplementation((settings) => Promise.resolve(settings));
    (badgeSettingsApi.saveAll as vi.Mock).mockImplementation((settings) => Promise.resolve(settings));
  });

  it('should load badge settings on init', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    // Check that the API was called
    expect(badgeSettingsApi.getAll).toHaveBeenCalledWith('1');
    
    // Check that the hook returns the correct badge settings
    expect(result.current.audioBadge).toEqual(mockAudioBadge);
    expect(result.current.resolutionBadge).toEqual(mockResolutionBadge);
    expect(result.current.reviewBadge).toEqual(mockReviewBadge);
  });

  it('should update audio badge settings', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const updatedSettings = {
      badge_size: 150,
      background_color: '#FF0000'
    };

    // Update settings
    act(() => {
      result.current.updateAudioBadge(updatedSettings);
    });

    // Check that the settings were updated
    expect(result.current.audioBadge?.badge_size).toBe(150);
    expect(result.current.audioBadge?.background_color).toBe('#FF0000');
    expect(result.current.hasUnsavedChanges).toBe(true);
  });

  it('should save audio badge settings', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Update settings
    act(() => {
      result.current.updateAudioBadge({ badge_size: 150 });
    });

    // Save settings
    await act(async () => {
      await result.current.saveAudioBadge();
    });

    // Check that save was called with the correct settings
    expect(badgeSettingsApi.save).toHaveBeenCalledWith(
      expect.objectContaining({
        badge_type: 'audio',
        badge_size: 150
      })
    );

    // Check that hasUnsavedChanges is reset
    expect(result.current.hasUnsavedChanges).toBe(false);
  });

  it('should save all badge settings', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Update multiple badges
    act(() => {
      result.current.updateAudioBadge({ badge_size: 150 });
      result.current.updateResolutionBadge({ background_color: '#FF0000' });
    });

    // Save all settings
    await act(async () => {
      await result.current.saveAllBadges();
    });

    // Check that saveAll was called with the correct settings
    expect(badgeSettingsApi.saveAll).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({
          badge_type: 'audio',
          badge_size: 150
        }),
        expect.objectContaining({
          badge_type: 'resolution',
          background_color: '#FF0000'
        }),
        expect.objectContaining({
          badge_type: 'review'
        })
      ])
    );

    // Check that hasUnsavedChanges is reset
    expect(result.current.hasUnsavedChanges).toBe(false);
  });

  it('should reset badge settings to defaults', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Update settings
    act(() => {
      result.current.updateAudioBadge({ badge_size: 150 });
    });

    // Reset settings
    act(() => {
      result.current.resetAudioBadge();
    });

    // Check that settings were reset to defaults with the correct user_id
    expect(result.current.audioBadge?.badge_size).toBe(100); // Default value
    expect(result.current.audioBadge?.user_id).toBe('1');
    expect(result.current.hasUnsavedChanges).toBe(true);
  });

  it('should handle API errors gracefully', async () => {
    // Setup error response
    (badgeSettingsApi.getAll as vi.Mock).mockRejectedValue(new Error('API error'));

    const { result } = renderHook(() => useUnifiedBadgeSettings(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should have an error state
    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe('API error');

    // Should still have default badge settings
    expect(result.current.audioBadge).toBeDefined();
    expect(result.current.resolutionBadge).toBeDefined();
    expect(result.current.reviewBadge).toBeDefined();
  });

  it('should use custom user ID when provided', async () => {
    const { result } = renderHook(() => useUnifiedBadgeSettings({ userId: '2' }), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Check that the API was called with the custom user ID
    expect(badgeSettingsApi.getAll).toHaveBeenCalledWith('2');

    // Update and save settings
    act(() => {
      result.current.updateAudioBadge({ badge_size: 150 });
    });

    await act(async () => {
      await result.current.saveAudioBadge();
    });

    // Check that save was called with the correct user ID
    expect(badgeSettingsApi.save).toHaveBeenCalledWith(
      expect.objectContaining({
        user_id: '2'
      })
    );
  });
});
