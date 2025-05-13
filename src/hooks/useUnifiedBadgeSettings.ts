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
    queryFn: async () => {
      console.log("Starting query function for badge settings");
      const result = await badgeSettingsApi.getAll(userId);
      console.log("Query function completed with result:", result);
      return result;
    },
    onSuccess: (data) => {
      console.log("useQuery onSuccess data received:", data);
      
      if (!data || !Array.isArray(data)) {
        console.error("Received invalid data in onSuccess", data);
        return;
      }

      try {
        // Find each badge type in the data and create clean copies to prevent reference issues
        const badgeData = data.filter(badge => badge && badge.badge_type);
        
        const audio = badgeData.find((badge) => badge.badge_type === 'audio');
        const resolution = badgeData.find((badge) => badge.badge_type === 'resolution');
        const review = badgeData.find((badge) => badge.badge_type === 'review');

        // Debug information
        console.log("Parsed badge data:", { 
          audio: audio ? {...audio, badge_size: audio.badge_size} : null,
          resolution: resolution ? {...resolution, badge_size: resolution.badge_size} : null, 
          review: review ? {...review, badge_size: review.badge_size} : null 
        });

        // Always set local state from fetched data on initial load or successful refetch
        // Create clean copies of the data to avoid reference issues
        if (audio) setLocalAudioBadge(JSON.parse(JSON.stringify(audio)));
        if (resolution) setLocalResolutionBadge(JSON.parse(JSON.stringify(resolution)));
        if (review) setLocalReviewBadge(JSON.parse(JSON.stringify(review)));

        // Reset unsaved changes to false after loading data
        setUnsavedChanges({
          audio: false,
          resolution: false,
          review: false
        });
        setLastSaved(new Date()); // Data is now up-to-date with "saved" data
      } catch (err) {
        console.error("Error processing badge data in onSuccess:", err);
      }
    },
    onError: (error) => { 
      console.error("useQuery onError:", error);
      toast.error(`Error fetching badge settings: ${error.message}`);
    }
  });


  // Mutation for saving audio badge settings
  const audioMutation = useMutation({
    mutationFn: (settings: AudioBadgeSettings) => badgeSettingsApi.save(settings),
    onSuccess: (savedSettings) => {
      try {
        // Create a clean copy of the saved settings to avoid reference issues
        // Handle both direct and wrapped API responses
        let cleanSavedSettings;
        
        if (savedSettings && typeof savedSettings === 'object') {
          // Check if this is a wrapper with success and data properties
          if (savedSettings.success && savedSettings.data) {
            cleanSavedSettings = savedSettings.data;
            console.log('Audio mutation extracted data from success wrapper');
          } else if (savedSettings.badge_type === 'audio') {
            cleanSavedSettings = savedSettings;
            console.log('Audio mutation received direct settings object');
          } else {
            // Fallback to using the local badge
            console.warn('Audio mutation received unexpected response format, using local badge');
            cleanSavedSettings = localAudioBadge || audioBadge;
          }
        } else {
          // Fallback to using the local badge
          console.warn('Audio mutation received non-object response, using local badge');
          cleanSavedSettings = localAudioBadge || audioBadge;
        }
        
        // Ensure we have a clean object
        cleanSavedSettings = JSON.parse(JSON.stringify(cleanSavedSettings));
        console.log('Audio mutation processed result:', cleanSavedSettings);
        
        // Update cache with the saved settings
        queryClient.setQueryData(
          badgeSettingsKeys.byType(userId, 'audio'),
          cleanSavedSettings
        );

        // Update the full cache
        queryClient.setQueryData(
          badgeSettingsKeys.byUser(userId),
          (oldData: UnifiedBadgeSettings[] | undefined) => {
            if (!oldData) return [cleanSavedSettings];

            return oldData.map(badge =>
              badge.badge_type === 'audio' ? cleanSavedSettings : badge
            );
          }
        );

        // Set local state to match saved settings
        setLocalAudioBadge(cleanSavedSettings);
        
        // Reset unsaved changes flag
        setUnsavedChanges(prev => ({
          ...prev,
          audio: false
        }));

        // Update last saved timestamp
        setLastSaved(new Date());
        // Show success toast
        toast.success('Audio badge settings saved successfully');
      } catch (err) {
        console.error('Error processing save response:', err);
        // Still mark as saved to avoid confusing the user
        setUnsavedChanges(prev => ({ ...prev, audio: false }));
        setLastSaved(new Date());
        // Show success toast with a note
        toast.success('Audio badge settings saved successfully (with response processing error)');
      }
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
      try {
        // Create a clean copy of the saved settings to avoid reference issues
        // Handle both direct and wrapped API responses
        let cleanSavedSettings;
        
        if (savedSettings && typeof savedSettings === 'object') {
          // Check if this is a wrapper with success and data properties
          if (savedSettings.success && savedSettings.data) {
            cleanSavedSettings = savedSettings.data;
            console.log('Resolution mutation extracted data from success wrapper');
          } else if (savedSettings.badge_type === 'resolution') {
            cleanSavedSettings = savedSettings;
            console.log('Resolution mutation received direct settings object');
          } else {
            // Fallback to using the local badge
            console.warn('Resolution mutation received unexpected response format, using local badge');
            cleanSavedSettings = localResolutionBadge || resolutionBadge;
          }
        } else {
          // Fallback to using the local badge
          console.warn('Resolution mutation received non-object response, using local badge');
          cleanSavedSettings = localResolutionBadge || resolutionBadge;
        }
        
        // Ensure we have a clean object
        cleanSavedSettings = JSON.parse(JSON.stringify(cleanSavedSettings));
        console.log('Resolution mutation processed result:', cleanSavedSettings);
        
        // Update cache with the saved settings
        queryClient.setQueryData(
          badgeSettingsKeys.byType(userId, 'resolution'),
          cleanSavedSettings
        );

        // Update the full cache
        queryClient.setQueryData(
          badgeSettingsKeys.byUser(userId),
          (oldData: UnifiedBadgeSettings[] | undefined) => {
            if (!oldData) return [cleanSavedSettings];

            return oldData.map(badge =>
              badge.badge_type === 'resolution' ? cleanSavedSettings : badge
            );
          }
        );
        
        // Set local state to match saved settings
        setLocalResolutionBadge(cleanSavedSettings);

        // Reset unsaved changes flag
        setUnsavedChanges(prev => ({
          ...prev,
          resolution: false
        }));

        // Update last saved timestamp
        setLastSaved(new Date());
        // Show success toast
        toast.success('Resolution badge settings saved successfully');
      } catch (err) {
        console.error('Error processing save response:', err);
        // Still mark as saved to avoid confusing the user
        setUnsavedChanges(prev => ({ ...prev, resolution: false }));
        setLastSaved(new Date());
        // Show success toast with a note
        toast.success('Resolution badge settings saved successfully (with response processing error)');
      }
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
      try {
        // Create a clean copy of the saved settings to avoid reference issues
        // Handle both direct and wrapped API responses
        let cleanSavedSettings;
        
        if (savedSettings && typeof savedSettings === 'object') {
          // Check if this is a wrapper with success and data properties
          if (savedSettings.success && savedSettings.data) {
            cleanSavedSettings = savedSettings.data;
            console.log('Review mutation extracted data from success wrapper');
          } else if (savedSettings.badge_type === 'review') {
            cleanSavedSettings = savedSettings;
            console.log('Review mutation received direct settings object');
          } else {
            // Fallback to using the local badge
            console.warn('Review mutation received unexpected response format, using local badge');
            cleanSavedSettings = localReviewBadge || reviewBadge;
          }
        } else {
          // Fallback to using the local badge
          console.warn('Review mutation received non-object response, using local badge');
          cleanSavedSettings = localReviewBadge || reviewBadge;
        }
        
        // Ensure we have a clean object
        cleanSavedSettings = JSON.parse(JSON.stringify(cleanSavedSettings));
        console.log('Review mutation processed result:', cleanSavedSettings);
        
        // Update cache with the saved settings
        queryClient.setQueryData(
          badgeSettingsKeys.byType(userId, 'review'),
          cleanSavedSettings
        );

        // Update the full cache
        queryClient.setQueryData(
          badgeSettingsKeys.byUser(userId),
          (oldData: UnifiedBadgeSettings[] | undefined) => {
            if (!oldData) return [cleanSavedSettings];

            return oldData.map(badge =>
              badge.badge_type === 'review' ? cleanSavedSettings : badge
            );
          }
        );
        
        // Set local state to match saved settings
        setLocalReviewBadge(cleanSavedSettings);

        // Reset unsaved changes flag
        setUnsavedChanges(prev => ({
          ...prev,
          review: false
        }));

        // Update last saved timestamp
        setLastSaved(new Date());
        // Show success toast
        toast.success('Review badge settings saved successfully');
      } catch (err) {
        console.error('Error processing save response:', err);
        // Still mark as saved to avoid confusing the user
        setUnsavedChanges(prev => ({ ...prev, review: false }));
        setLastSaved(new Date());
        // Show success toast with a note
        toast.success('Review badge settings saved successfully (with response processing error)');
      }
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
      try {
        // Create a clean copy of the saved settings to avoid reference issues
        // Handle both direct and wrapped API responses
        let cleanSavedSettings = [];
        
        if (savedSettings && Array.isArray(savedSettings)) {
          // Normal array response
          cleanSavedSettings = savedSettings;
          console.log('All badges mutation received direct array');
        } else if (savedSettings && typeof savedSettings === 'object' && savedSettings.success && Array.isArray(savedSettings.data)) {
          // Wrapped success response
          cleanSavedSettings = savedSettings.data;
          console.log('All badges mutation extracted data from success wrapper');
        } else {
          // Use local state as fallback
          console.warn('All badges mutation received unexpected response format, using local state');
          if (localAudioBadge) cleanSavedSettings.push(localAudioBadge);
          if (localResolutionBadge) cleanSavedSettings.push(localResolutionBadge);
          if (localReviewBadge) cleanSavedSettings.push(localReviewBadge);
        }
        
        // Ensure we have clean objects
        cleanSavedSettings = cleanSavedSettings.map(setting => 
          JSON.parse(JSON.stringify(setting)));
        console.log('All badges mutation processed results:', cleanSavedSettings);
        
        // Update the cache with all saved settings
        queryClient.setQueryData(
          badgeSettingsKeys.byUser(userId),
          cleanSavedSettings
        );

        // Update individual badge type caches and local state
        cleanSavedSettings.forEach(badge => {
          // Update query cache for this badge type
          queryClient.setQueryData(
            badgeSettingsKeys.byType(userId, badge.badge_type),
            badge
          );
          
          // Update local state based on badge type
          switch(badge.badge_type) {
            case 'audio':
              setLocalAudioBadge(badge as AudioBadgeSettings);
              break;
            case 'resolution':
              setLocalResolutionBadge(badge as ResolutionBadgeSettings);
              break;
            case 'review':
              setLocalReviewBadge(badge as ReviewBadgeSettings);
              break;
          }
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
      } catch (err) {
        console.error('Error processing save response:', err);
        // Still mark as saved to avoid confusing the user
        setUnsavedChanges({
          audio: false,
          resolution: false,
          review: false
        });
        setLastSaved(new Date());
        // Show success toast with a note
        toast.success('All badge settings saved successfully (with response processing error)');
      }
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
    // First try localAudioBadge, then try to find in badgeSettings, and finally use defaults
    let resolvedBadge;
    
    if (localAudioBadge) {
      resolvedBadge = localAudioBadge;
      console.log("Using localAudioBadge with size:", localAudioBadge.badge_size);
    } else if (badgeSettings && Array.isArray(badgeSettings)) {
      const fromSettings = badgeSettings.find(b => b && b.badge_type === 'audio');
      if (fromSettings) {
        resolvedBadge = fromSettings;
        console.log("Using badgeSettings cache for audio with size:", fromSettings.badge_size);
      } else {
        resolvedBadge = { ...DEFAULT_AUDIO_BADGE_SETTINGS, user_id: userId };
        console.log("Using DEFAULT_AUDIO_BADGE_SETTINGS");
      }
    } else {
      resolvedBadge = { ...DEFAULT_AUDIO_BADGE_SETTINGS, user_id: userId };
      console.log("Using DEFAULT_AUDIO_BADGE_SETTINGS (fallback)");
    }
    
    console.log("Final derived audioBadge size:", resolvedBadge.badge_size);
    return resolvedBadge;
  }, [localAudioBadge, badgeSettings, userId]);

  const resolutionBadge = useMemo(() => {
    // First try localResolutionBadge, then try to find in badgeSettings, and finally use defaults
    let resolvedBadge;
    
    if (localResolutionBadge) {
      resolvedBadge = localResolutionBadge;
      console.log("Using localResolutionBadge with size:", localResolutionBadge.badge_size);
    } else if (badgeSettings && Array.isArray(badgeSettings)) {
      const fromSettings = badgeSettings.find(b => b && b.badge_type === 'resolution');
      if (fromSettings) {
        resolvedBadge = fromSettings;
        console.log("Using badgeSettings cache for resolution with size:", fromSettings.badge_size);
      } else {
        resolvedBadge = { ...DEFAULT_RESOLUTION_BADGE_SETTINGS, user_id: userId };
        console.log("Using DEFAULT_RESOLUTION_BADGE_SETTINGS");
      }
    } else {
      resolvedBadge = { ...DEFAULT_RESOLUTION_BADGE_SETTINGS, user_id: userId };
      console.log("Using DEFAULT_RESOLUTION_BADGE_SETTINGS (fallback)");
    }
    
    console.log("Final derived resolutionBadge size:", resolvedBadge.badge_size);
    return resolvedBadge;
  }, [localResolutionBadge, badgeSettings, userId]);

  const reviewBadge = useMemo(() => {
    // First try localReviewBadge, then try to find in badgeSettings, and finally use defaults
    let resolvedBadge;
    
    if (localReviewBadge) {
      resolvedBadge = localReviewBadge;
      console.log("Using localReviewBadge with size:", localReviewBadge.badge_size);
    } else if (badgeSettings && Array.isArray(badgeSettings)) {
      const fromSettings = badgeSettings.find(b => b && b.badge_type === 'review');
      if (fromSettings) {
        resolvedBadge = fromSettings;
        console.log("Using badgeSettings cache for review with size:", fromSettings.badge_size);
      } else {
        resolvedBadge = { ...DEFAULT_REVIEW_BADGE_SETTINGS, user_id: userId };
        console.log("Using DEFAULT_REVIEW_BADGE_SETTINGS");
      }
    } else {
      resolvedBadge = { ...DEFAULT_REVIEW_BADGE_SETTINGS, user_id: userId };
      console.log("Using DEFAULT_REVIEW_BADGE_SETTINGS (fallback)");
    }
    
    console.log("Final derived reviewBadge size:", resolvedBadge.badge_size);
    return resolvedBadge;
  }, [localReviewBadge, badgeSettings, userId]);

  // Check if there are any unsaved changes
  const hasUnsavedChanges = useMemo(() =>
    unsavedChanges.audio || unsavedChanges.resolution || unsavedChanges.review,
    [unsavedChanges]
  );

  // Update functions that allow partial updates
  const updateAudioBadge = useCallback((settings: Partial<AudioBadgeSettings>) => {
    console.log('Updating audio badge, settings:', settings);
    
    setLocalAudioBadge(prev => {
      if (!prev) {
        const newBadge = {
          ...DEFAULT_AUDIO_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
        console.log('Created new audio badge with size:', newBadge.badge_size);
        return newBadge;
      }

      // Create the updated badge
      const updatedBadge = {
        ...prev,
        ...settings
      };
      console.log('Updated audio badge, final size:', updatedBadge.badge_size);
      return updatedBadge;
    });

    setUnsavedChanges(prev => ({
      ...prev,
      audio: true
    }));
  }, [userId]);

  const updateResolutionBadge = useCallback((settings: Partial<ResolutionBadgeSettings>) => {
    console.log('Updating resolution badge, settings:', settings);
    
    setLocalResolutionBadge(prev => {
      if (!prev) {
        const newBadge = {
          ...DEFAULT_RESOLUTION_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
        console.log('Created new resolution badge with size:', newBadge.badge_size);
        return newBadge;
      }

      // Create the updated badge
      const updatedBadge = {
        ...prev,
        ...settings
      };
      console.log('Updated resolution badge, final size:', updatedBadge.badge_size);
      return updatedBadge;
    });

    setUnsavedChanges(prev => ({
      ...prev,
      resolution: true
    }));
  }, [userId]);

  const updateReviewBadge = useCallback((settings: Partial<ReviewBadgeSettings>) => {
    console.log('Updating review badge, settings:', settings);
    
    setLocalReviewBadge(prev => {
      if (!prev) {
        const newBadge = {
          ...DEFAULT_REVIEW_BADGE_SETTINGS,
          user_id: userId,
          ...settings
        };
        console.log('Created new review badge with size:', newBadge.badge_size);
        return newBadge;
      }

      // Create the updated badge
      const updatedBadge = {
        ...prev,
        ...settings
      };
      console.log('Updated review badge, final size:', updatedBadge.badge_size);
      return updatedBadge;
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

    console.log('Saving audio badge with size:', localAudioBadge.badge_size);
    // Ensure badge_type is explicitly set to 'audio'
    await audioMutation.mutateAsync({
      ...localAudioBadge,
      badge_type: 'audio',
      user_id: userId
    });
  }, [localAudioBadge, audioMutation, userId]);

  const saveResolutionBadge = useCallback(async () => {
    if (!localResolutionBadge) return;

    console.log('Saving resolution badge with size:', localResolutionBadge.badge_size);
    // Ensure badge_type is explicitly set to 'resolution'
    await resolutionMutation.mutateAsync({
      ...localResolutionBadge,
      badge_type: 'resolution',
      user_id: userId
    });
  }, [localResolutionBadge, resolutionMutation, userId]);

  const saveReviewBadge = useCallback(async () => {
    if (!localReviewBadge) return;

    console.log('Saving review badge with size:', localReviewBadge.badge_size);
    // Ensure badge_type is explicitly set to 'review'
    await reviewMutation.mutateAsync({
      ...localReviewBadge,
      badge_type: 'review',
      user_id: userId
    });
  }, [localReviewBadge, reviewMutation, userId]);

  const saveAllBadges = useCallback(async () => {
    try {
      // Save each badge individually
      const results = [];
      console.log("Starting saveAllBadges with current badge sizes:", {
        audio: audioBadge?.badge_size,
        resolution: resolutionBadge?.badge_size,
        review: reviewBadge?.badge_size
      });

      if (localAudioBadge || audioBadge) {
        // Always use the local badge if it exists, otherwise use the computed badge
        const audioBadgeToSave = {
          ...(localAudioBadge || audioBadge),
          badge_type: 'audio',
          user_id: userId.toString()
        };

        // Clean the badge object to avoid passing any undefined or circular references
        const cleanAudioBadge = JSON.parse(JSON.stringify(audioBadgeToSave));
        console.log('Saving audio badge with size:', cleanAudioBadge.badge_size);
        const audioResult = await audioMutation.mutateAsync(cleanAudioBadge);
        results.push(audioResult);
      }

      if (localResolutionBadge || resolutionBadge) {
        // Always use the local badge if it exists, otherwise use the computed badge
        const resolutionBadgeToSave = {
          ...(localResolutionBadge || resolutionBadge),
          badge_type: 'resolution',
          user_id: userId.toString()
        };

        // Clean the badge object to avoid passing any undefined or circular references
        const cleanResolutionBadge = JSON.parse(JSON.stringify(resolutionBadgeToSave));
        console.log('Saving resolution badge with size:', cleanResolutionBadge.badge_size);
        const resolutionResult = await resolutionMutation.mutateAsync(cleanResolutionBadge);
        results.push(resolutionResult);
      }

      if (localReviewBadge || reviewBadge) {
        // Always use the local badge if it exists, otherwise use the computed badge
        const reviewBadgeToSave = {
          ...(localReviewBadge || reviewBadge),
          badge_type: 'review',
          user_id: userId.toString()
        };

        // Clean the badge object to avoid passing any undefined or circular references
        const cleanReviewBadge = JSON.parse(JSON.stringify(reviewBadgeToSave));
        console.log('Saving review badge with size:', cleanReviewBadge.badge_size);
        const reviewResult = await reviewMutation.mutateAsync(cleanReviewBadge);
        results.push(reviewResult);
      }

      // Reset unsaved changes flags after successful save
      setUnsavedChanges({
        audio: false,
        resolution: false,
        review: false
      });

      // Update last saved timestamp
      setLastSaved(new Date());

      // Return the combined results
      return results;
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
    console.log("Refetching badge settings");
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