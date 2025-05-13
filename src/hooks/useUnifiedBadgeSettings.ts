// E:\programming\aphrodite\src\hooks\useUnifiedBadgeSettings.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback, useMemo, useEffect } from 'react';
import { toast } from 'sonner';

import { badgeSettingsApi } from '@/api/badgeSettingsApi';
import {
  UnifiedBadgeSettings,
  AudioBadgeSettings,
  ResolutionBadgeSettings,
  ReviewBadgeSettings,
  DEFAULT_AUDIO_BADGE_SETTINGS,
  DEFAULT_RESOLUTION_BADGE_SETTINGS,
  DEFAULT_REVIEW_BADGE_SETTINGS
} from '@/types/unifiedBadgeSettings';

// Type for tracking unsaved changes
type UnsavedChanges = {
  audio: boolean;
  resolution: boolean;
  review: boolean;
};

interface UseUnifiedBadgeSettingsOptions {
  userId?: string | number;
  autoSave?: boolean;
  autoSaveDelay?: number;
}

interface UseUnifiedBadgeSettingsResult {
  // Badge data
  audioBadge: AudioBadgeSettings | null;
  resolutionBadge: ResolutionBadgeSettings | null;
  reviewBadge: ReviewBadgeSettings | null;
  // Status
  isLoading: boolean;
  isSaving: boolean;
  error: Error | null;
  // Badge-specific update functions
  updateAudioBadge: (settings: Partial<AudioBadgeSettings>) => void;
  updateResolutionBadge: (settings: Partial<ResolutionBadgeSettings>) => void;
  updateReviewBadge: (settings: Partial<ReviewBadgeSettings>) => void;
  // Complete update functions
  setAudioBadge: (settings: AudioBadgeSettings | null) => void;
  setResolutionBadge: (settings: ResolutionBadgeSettings | null) => void;
  setReviewBadge: (settings: ReviewBadgeSettings | null) => void;

  // Save functions
  saveAudioBadge: () => Promise<void>;
  saveResolutionBadge: () => Promise<void>;
  saveReviewBadge: () => Promise<void>;
  saveAllBadges: () => Promise<void>;

  // Reset functions
  resetAudioBadge: () => void;
  resetResolutionBadge: () => void;
  resetReviewBadge: () => void;
  resetAllBadges: () => void;

  // Unsaved changes tracking
  hasUnsavedChanges: boolean;
  lastSaved: Date | null;
  // Refresh data
  refetchBadgeSettings: () => Promise<void>;
}

// Query keys for React Query
export const badgeSettingsKeys = {
  all: ['badgeSettings'] as const,
  byUser: (userId: string | number) => [...badgeSettingsKeys.all, 'user', userId] as const,
  byType: (userId: string | number, type: string) => [...badgeSettingsKeys.byUser(userId), type] as const,
};

/**
 * Custom hook for managing unified badge settings with React Query
 */
export const useUnifiedBadgeSettings = (
  options: UseUnifiedBadgeSettingsOptions = {}
): UseUnifiedBadgeSettingsResult => {
  const {
    userId = '1',
    autoSave = false,
    autoSaveDelay = 2000
  } = options;
  const queryClient = useQueryClient();

  // State for storing badge settings
  const [localAudioBadge, setLocalAudioBadge] = useState<AudioBadgeSettings | null>(null);
  const [localResolutionBadge, setLocalResolutionBadge] = useState<ResolutionBadgeSettings | null>(null);
  const [localReviewBadge, setLocalReviewBadge] = useState<ReviewBadgeSettings | null>(null);

  // State for tracking unsaved changes
  const [unsavedChanges, setUnsavedChanges] = useState<UnsavedChanges>({
    audio: false,
    resolution: false,
    review: false
  });

  // State for tracking last saved time
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save debounce timer
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);

  // Query for fetching badge settings
  const {
    data: badgeSettings,
    isLoading,
    error: fetchError,
    refetch
  } = useQuery({
    queryKey: badgeSettingsKeys.byUser(userId),
    queryFn: () => badgeSettingsApi.getAll(userId),
    onSuccess: (data) => {
      console.log("useQuery onSuccess data received:", data); // <-- We NEED to see this log!

      // Find each badge type in the data
      const audio = data.find((badge) => badge.badge_type === 'audio') as AudioBadgeSettings;
      const resolution = data.find((badge) => badge.badge_type === 'resolution') as ResolutionBadgeSettings;
      const review = data.find((badge) => badge.badge_type === 'review') as ReviewBadgeSettings;

      // Always set local state from fetched data on initial load or successful refetch.
      // The 'unsavedChanges' flag should only be set by user interaction.
      setLocalAudioBadge(audio || null);
      setLocalResolutionBadge(resolution || null);
      setLocalReviewBadge(review || null);

      // Reset unsaved changes to false after loading data
      setUnsavedChanges({
        audio: false,
        resolution: false,
        review: false
      });
      setLastSaved(new Date()); // Data is now up-to-date with "saved" data
    },
    onError: (error) => { // <--- This onError callback is also crucial for debugging
      console.error("useQuery onError:", error);
      toast.error(`Error fetching badge settings: ${error.message}`);
    }
  });

  // This useEffect logs the direct state of the useQuery result (data, loading, error)
  useEffect(() => { // <--- IMPORTANT: Added this useEffect
      console.log("useQuery state update - isLoading:", isLoading, "data:", badgeSettings, "error:", fetchError);
  }, [isLoading, badgeSettings, fetchError]);


  // Mutation for saving audio badge settings
  const audioMutation = useMutation({
    mutationFn: (settings: AudioBadgeSettings) => badgeSettingsApi.save(settings),
    onSuccess: (savedSettings) => {
      // Update cache with the saved settings
      queryClient.setQueryData(
        badgeSettingsKeys.byType(userId, 'audio'),
        savedSettings
      );

      // Update the full cache
      queryClient.setQueryData(
        badgeSettingsKeys.byUser(userId),
        (oldData: UnifiedBadgeSettings[] | undefined) => {
          if (!oldData) return [savedSettings];

          return oldData.map(badge =>
            badge.badge_type === 'audio' ? savedSettings : badge
          );
        }
      );

      // Reset unsaved changes flag
      setUnsavedChanges(prev => ({
        ...prev,
        audio: false
      }));

      // Update last saved timestamp
      setLastSaved(new Date());
      // Show success toast
      toast.success('Audio badge settings saved successfully');
    },
    onError: (error) => {
      console.error('Error saving audio badge settings:', error);
      toast.error('Failed to save audio badge settings');
    }
  });


  // Mutation for saving resolution badge settings
  const resolutionMutation = useMutation({
    mutationFn: (settings: ResolutionBadgeSettings) => badgeSettingsApi.save(settings),
    onSuccess: (savedSettings) => {
      // Update cache with the saved settings
      queryClient.setQueryData(
        badgeSettingsKeys.byType(userId, 'resolution'),
        savedSettings
      );

      // Update the full cache
      queryClient.setQueryData(
        badgeSettingsKeys.byUser(userId),
        (oldData: UnifiedBadgeSettings[] | undefined) => {
          if (!oldData) return [savedSettings];

          return oldData.map(badge =>
            badge.badge_type === 'resolution' ? savedSettings : badge
          );
        }
      );

      // Reset unsaved changes flag
      setUnsavedChanges(prev => ({
        ...prev,
        resolution: false
      }));

      // Update last saved timestamp
      setLastSaved(new Date());
      // Show success toast
      toast.success('Resolution badge settings saved successfully');
    },
    onError: (error) => {
      console.error('Error saving resolution badge settings:', error);
      toast.error('Failed to save resolution badge settings');
    }
  });


  // Mutation for saving review badge settings
  const reviewMutation = useMutation({
    mutationFn: (settings: ReviewBadgeSettings) => badgeSettingsApi.save(settings),
    onSuccess: (savedSettings) => {
      // Update cache with the saved settings
      queryClient.setQueryData(
        badgeSettingsKeys.byType(userId, 'review'),
        savedSettings
      );

      // Update the full cache
      queryClient.setQueryData(
        badgeSettingsKeys.byUser(userId),
        (oldData: UnifiedBadgeSettings[] | undefined) => {
          if (!oldData) return [savedSettings];

          return oldData.map(badge =>
            badge.badge_type === 'review' ? savedSettings : badge
          );
        }
      );

      // Reset unsaved changes flag
      setUnsavedChanges(prev => ({
        ...prev,
        review: false
      }));

      // Update last saved timestamp
      setLastSaved(new Date());
      // Show success toast
      toast.success('Review badge settings saved successfully');
    },
    onError: (error) => {
      console.error('Error saving review badge settings:', error);
      toast.error('Failed to save review badge settings');
    }
  });


  // Mutation for saving all badge settings at once
  const allBadgesMutation = useMutation({
    mutationFn: (settings: UnifiedBadgeSettings[]) => badgeSettingsApi.saveAll(settings),
    onSuccess: (savedSettings) => {
      // Update the cache with all saved settings
      queryClient.setQueryData(
        badgeSettingsKeys.byUser(userId),
        savedSettings
      );

      // Update individual badge type caches
      savedSettings.forEach(badge => {
        queryClient.setQueryData(
          badgeSettingsKeys.byType(userId, badge.badge_type),
          badge
        );
      });

      // Reset all unsaved changes flags
      setUnsavedChanges({
        audio: false,
        resolution: false,
        review: false
      });

      // Update last saved timestamp
      setLastSaved(new Date());

      // Show success toast
      toast.success('All badge settings saved successfully');
    },
    onError: (error) => {
      console.error('Error saving all badge settings:', error);
      toast.error('Failed to save badge settings');
    }
  });


  // Combined loading and error states
  const isSaving = useMemo(() =>
    audioMutation.isPending ||
    resolutionMutation.isPending ||
    reviewMutation.isPending ||
    allBadgesMutation.isPending,
    [
      audioMutation.isPending,
      resolutionMutation.isPending,
      reviewMutation.isPending,
      allBadgesMutation.isPending
    ]
  );
  const error = useMemo(() =>
    fetchError ||
    audioMutation.error ||
    resolutionMutation.error || // <-- Corrected typo here
    reviewMutation.error ||
    allBadgesMutation.error,
    [
      fetchError,
      audioMutation.error,
      resolutionMutation.error, // <-- Corrected typo here
      reviewMutation.error,
      allBadgesMutation.error
    ]
  );

  // Derived state for badge settings with fallbacks to defaults
  const audioBadge = useMemo(() => {
    const resolvedBadge = localAudioBadge ||
                          (badgeSettings?.find(b => b.badge_type === 'audio') as AudioBadgeSettings) ||
                          { ...DEFAULT_AUDIO_BADGE_SETTINGS, user_id: userId };
    console.log("Derived audioBadge (from useMemo):", resolvedBadge); // Added debug log
    return resolvedBadge;
  }, [localAudioBadge, badgeSettings, userId]);

  const resolutionBadge = useMemo(() => {
    const resolvedBadge = localResolutionBadge ||
                          (badgeSettings?.find(b => b.badge_type === 'resolution') as ResolutionBadgeSettings) ||
                          { ...DEFAULT_RESOLUTION_BADGE_SETTINGS, user_id: userId };
    console.log("Derived resolutionBadge (from useMemo):", resolvedBadge); // Added debug log
    return resolvedBadge;
  }, [localResolutionBadge, badgeSettings, userId]);

  const reviewBadge = useMemo(() => {
    const resolvedBadge = localReviewBadge ||
                          (badgeSettings?.find(b => b.badge_type === 'review') as ReviewBadgeSettings) ||
                          { ...DEFAULT_REVIEW_BADGE_SETTINGS, user_id: userId };
    console.log("Derived reviewBadge (from useMemo):", resolvedBadge); // Added debug log
    return resolvedBadge;
  }, [localReviewBadge, badgeSettings, userId]);

  // Check if there are any unsaved changes
  const hasUnsavedChanges = useMemo(() =>
    unsavedChanges.audio || unsavedChanges.resolution || unsavedChanges.review,
    [unsavedChanges]
  );

  // Update functions that allow partial updates
  const updateAudioBadge = useCallback((settings: Partial<AudioBadgeSettings>) => {
    setLocalAudioBadge(prev => {
      if (!prev) {
        return {
          ...DEFAULT_AUDIO_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
      }

      return {
        ...prev,
        ...settings
      };
    });

    setUnsavedChanges(prev => ({
      ...prev,
      audio: true
    }));
  }, [userId]);

  const updateResolutionBadge = useCallback((settings: Partial<ResolutionBadgeSettings>) => {
    setLocalResolutionBadge(prev => {
      if (!prev) {
        return {
          ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
      }

      return {
        ...prev,
        ...settings
      };
    });

    setUnsavedChanges(prev => ({
      ...prev,
      resolution: true
    }));
  }, [userId]);

  const updateReviewBadge = useCallback((settings: Partial<ReviewBadgeSettings>) => {
    setLocalReviewBadge(prev => {
      if (!prev) {
        return {
          ...DEFAULT_REVIEW_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
      }

      return {
        ...prev,
        ...settings
      };
    });

    setUnsavedChanges(prev => ({
      ...prev,
      review: true
    }));
  }, [userId]);

  // Complete setter functions (for compatibility with existing code)
  const setAudioBadge = useCallback((settings: AudioBadgeSettings | null) => {
    if (settings) {
      setLocalAudioBadge({
        ...settings,
        user_id: userId,
        badge_type: 'audio'
      });

      setUnsavedChanges(prev => ({
        ...prev,
        audio: true
      }));
    } else {
      // If null is passed, reset to defaults
      setLocalAudioBadge({
        ...DEFAULT_AUDIO_BADGE_SETTINGS,
        user_id: userId
      });

      setUnsavedChanges(prev => ({
        ...prev,
        audio: true
      }));
    }
  }, [userId]);

  const setResolutionBadge = useCallback((settings: ResolutionBadgeSettings | null) => {
    if (settings) {
      setLocalResolutionBadge({
        ...settings,
        user_id: userId,
        badge_type: 'resolution'
      });

      setUnsavedChanges(prev => ({
        ...prev,
        resolution: true
      }));
    } else {
      // If null is passed, reset to defaults
      setLocalResolutionBadge({
        ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
        user_id: userId
      });

      setUnsavedChanges(prev => ({
        ...prev,
        resolution: true
      }));
    }
  }, [userId]);

  const setReviewBadge = useCallback((settings: ReviewBadgeSettings | null) => {
    if (settings) {
      setLocalReviewBadge({
        ...settings,
        user_id: userId,
        badge_type: 'review'
      });

      setUnsavedChanges(prev => ({
        ...prev,
        review: true
      }));
    } else {
      // If null is passed, reset to defaults
      setLocalReviewBadge({
        ...DEFAULT_REVIEW_BADGE_SETTINGS,
        user_id: userId
      });

      setUnsavedChanges(prev => ({
        ...prev,
        review: true
      }));
    }
  }, [userId]);

  // Save functions
  const saveAudioBadge = useCallback(async () => {
    if (!localAudioBadge) return;

    // Ensure badge_type is explicitly set to 'audio'
    await audioMutation.mutateAsync({
      ...localAudioBadge,
      badge_type: 'audio',
      user_id: userId
    });
  }, [localAudioBadge, audioMutation, userId]);

  const saveResolutionBadge = useCallback(async () => {
    if (!localResolutionBadge) return;

    // Ensure badge_type is explicitly set to 'resolution'
    await resolutionMutation.mutateAsync({
      ...localResolutionBadge,
      badge_type: 'resolution',
      user_id: userId
    });
  }, [localResolutionBadge, resolutionMutation, userId]);

  const saveReviewBadge = useCallback(async () => {
    if (!localReviewBadge) return;

    // Ensure badge_type is explicitly set to 'review'
    await reviewMutation.mutateAsync({
      ...localReviewBadge,
      badge_type: 'review',
      user_id: userId
    });
  }, [localReviewBadge, reviewMutation, userId]);

  const saveAllBadges = useCallback(async () => {
    try {
      // Instead of using batch save, let's try saving each badge individually
      const results = [];

      if (localAudioBadge || audioBadge) {
        const audioBadgeToSave: AudioBadgeSettings = {
          ...(localAudioBadge || audioBadge),
          badge_type: 'audio',
          user_id: userId.toString()
        };

        console.log('Saving audio badge individually:', audioBadgeToSave);
        const audioResult = await audioMutation.mutateAsync(audioBadgeToSave);
        results.push(audioResult);
      }

      if (localResolutionBadge || resolutionBadge) {
        const resolutionBadgeToSave: ResolutionBadgeSettings = {
          ...(localResolutionBadge || resolutionBadge),
          badge_type: 'resolution',
          user_id: userId.toString()
        };

        console.log('Saving resolution badge individually:', resolutionBadgeToSave);
        const resolutionResult = await resolutionMutation.mutateAsync(resolutionBadgeToSave);
        results.push(resolutionResult);
      }

      if (localReviewBadge || reviewBadge) {
        const reviewBadgeToSave: ReviewBadgeSettings = {
          ...(localReviewBadge || reviewBadge),
          badge_type: 'review',
          user_id: userId.toString()
        };
        console.log('Saving review badge individually:', reviewBadgeToSave);
        const reviewResult = await reviewMutation.mutateAsync(reviewBadgeToSave);
        results.push(reviewResult);
      }

      // Return the combined results
      return results;
      /* Original batch save logic
      const settingsToSave: UnifiedBadgeSettings[] = [];
      if (localAudioBadge) {
        // Create a fresh object with only the required properties
        const audioBadgeToSave: AudioBadgeSettings = {
          ...localAudioBadge,
          badge_type: 'audio',
          user_id: userId.toString()
        };
        settingsToSave.push(audioBadgeToSave);
      } else if (audioBadge) {
        const audioBadgeToSave: AudioBadgeSettings = {
          ...audioBadge,
          badge_type: 'audio',
          user_id: userId.toString()
        };
        settingsToSave.push(audioBadgeToSave);
      }

      if (localResolutionBadge) {
        // Create a fresh object with only the required properties
        const resolutionBadgeToSave: ResolutionBadgeSettings = {
          ...localResolutionBadge,
          badge_type: 'resolution',
          user_id: userId.toString()
        };
        settingsToSave.push(resolutionBadgeToSave);
      } else if (resolutionBadge) {
        const resolutionBadgeToSave: ResolutionBadgeSettings = {
          ...resolutionBadge,
          badge_type: 'resolution',
          user_id: userId.toString()
        };
        settingsToSave.push(resolutionBadgeToSave);
      }

      if (localReviewBadge) {
        // Create a fresh object with only the required properties
        const reviewBadgeToSave: ReviewBadgeSettings = {
          ...localReviewBadge,
          badge_type: 'review',
          user_id: userId.toString()
        };
        settingsToSave.push(reviewBadgeToSave);
      } else if (reviewBadge) {
        const reviewBadgeToSave: ReviewBadgeSettings = {
          ...reviewBadge,
          badge_type: 'review',
          user_id: userId.toString()
        };
        settingsToSave.push(reviewBadgeToSave);
      }

      // Log what we're about to save
      console.log('About to save badge settings:', JSON.stringify(settingsToSave));
      if (settingsToSave.length > 0) {
        await allBadgesMutation.mutateAsync(settingsToSave);
      }
      */
    } catch (error) {
      console.error('Error in saveAllBadges:', error);
      throw error;
    }
  }, [
    localAudioBadge,
    localResolutionBadge,
    localReviewBadge,
    audioBadge,
    resolutionBadge,
    reviewBadge,
    audioMutation,
    resolutionMutation,
    reviewMutation,
    userId
  ]);

  // Reset functions
  const resetAudioBadge = useCallback(() => {
    setLocalAudioBadge({
      ...DEFAULT_AUDIO_BADGE_SETTINGS,
      user_id: userId
    });

    setUnsavedChanges(prev => ({
      ...prev,
      audio: true
    }));
  }, [userId]);

  const resetResolutionBadge = useCallback(() => {
    setLocalResolutionBadge({
      ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
      user_id: userId
    });

    setUnsavedChanges(prev => ({
      ...prev,
      resolution: true
    }));
  }, [userId]);

  const resetReviewBadge = useCallback(() => {
    setLocalReviewBadge({
      ...DEFAULT_REVIEW_BADGE_SETTINGS,
      user_id: userId
    });

    setUnsavedChanges(prev => ({
      ...prev,
      review: true
    }));
  }, [userId]);

  const resetAllBadges = useCallback(() => {
    resetAudioBadge();
    resetResolutionBadge();
    resetReviewBadge();
  }, [resetAudioBadge, resetResolutionBadge, resetReviewBadge]);

  // Refetch badge settings
  const refetchBadgeSettings = useCallback(async () => {
    await refetch();
  }, [refetch]);

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !hasUnsavedChanges) return;

    // Clear any existing timer
    if (saveTimer) {
      clearTimeout(saveTimer);
    }

    // Set new timer
    const timer = setTimeout(() => {
      saveAllBadges();
    }, autoSaveDelay);

    setSaveTimer(timer);

    // Clean up on unmount
    return () => {
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
    };
  }, [
    autoSave,
    autoSaveDelay,
    hasUnsavedChanges,
    saveAllBadges,
    saveTimer
  ]);

  return {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    isLoading,
    isSaving,
    error,
    updateAudioBadge,
    updateResolutionBadge,
    updateReviewBadge,
    setAudioBadge,
    setResolutionBadge,
    setReviewBadge,
    saveAudioBadge,
    saveResolutionBadge,
    saveReviewBadge,
    saveAllBadges,
    resetAudioBadge,
    resetResolutionBadge,
    resetReviewBadge,
    resetAllBadges,
    hasUnsavedChanges,
    lastSaved,
    refetchBadgeSettings
  };
};


export default useUnifiedBadgeSettings;