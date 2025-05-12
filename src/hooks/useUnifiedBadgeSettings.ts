import { useState, useEffect, useCallback } from 'react';
import {
  UnifiedBadgeSettings,
  AudioBadgeSettings,
  ResolutionBadgeSettings,
  ReviewBadgeSettings,
  DEFAULT_AUDIO_BADGE_SETTINGS,
  DEFAULT_RESOLUTION_BADGE_SETTINGS,
  DEFAULT_REVIEW_BADGE_SETTINGS
} from '@/types/unifiedBadgeSettings';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface UseBadgeSettingsOptions {
  userId?: string | number;
  autoSave?: boolean;
}

interface UseBadgeSettingsResult {
  audioBadge: AudioBadgeSettings | null;
  resolutionBadge: ResolutionBadgeSettings | null;
  reviewBadge: ReviewBadgeSettings | null;
  isLoading: boolean;
  isSaving: boolean;
  error: Error | null;
  setAudioBadge: (settings: AudioBadgeSettings | null) => void;
  setResolutionBadge: (settings: ResolutionBadgeSettings | null) => void;
  setReviewBadge: (settings: ReviewBadgeSettings | null) => void;
  saveSettings: () => Promise<void>;
  resetSettings: () => void;
  lastSaved: Date | null;
}

/**
 * Custom hook for managing badge settings
 */
export const useUnifiedBadgeSettings = (
  options: UseBadgeSettingsOptions = {}
): UseBadgeSettingsResult => {
  const { userId = '1', autoSave = false } = options;

  // Badge settings state
  const [audioBadge, setAudioBadgeState] = useState<AudioBadgeSettings | null>(null);
  const [resolutionBadge, setResolutionBadgeState] = useState<ResolutionBadgeSettings | null>(null);
  const [reviewBadge, setReviewBadgeState] = useState<ReviewBadgeSettings | null>(null);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save debounce timer
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);

  // Load settings from API
  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch all badge settings for the user
        const response = await api.get(`/api/v1/unified-badge-settings?user_id=${userId}`);
        const data: UnifiedBadgeSettings[] = response.data;
        
        // Process the settings by badge type
        let audioSettings: AudioBadgeSettings | null = null;
        let resolutionSettings: ResolutionBadgeSettings | null = null;
        let reviewSettings: ReviewBadgeSettings | null = null;
        
        data.forEach(badge => {
          switch (badge.badge_type) {
            case 'audio':
              audioSettings = badge as AudioBadgeSettings;
              break;
            case 'resolution':
              resolutionSettings = badge as ResolutionBadgeSettings;
              break;
            case 'review':
              reviewSettings = badge as ReviewBadgeSettings;
              break;
          }
        });
        
        // Set state for each badge type
        setAudioBadgeState(audioSettings);
        setResolutionBadgeState(resolutionSettings);
        setReviewBadgeState(reviewSettings);
      } catch (err) {
        console.error('Error fetching badge settings:', err);
        setError(err instanceof Error ? err : new Error('Failed to fetch badge settings'));
        
        // Use defaults in case of error
        setAudioBadgeState(null);
        setResolutionBadgeState(null);
        setReviewBadgeState(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSettings();
  }, [userId]);

  // Save settings to API
  const saveSettings = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    
    try {
      const badgesToSave: UnifiedBadgeSettings[] = [];
      
      // Include each badge in the save request if it's defined
      if (audioBadge) {
        badgesToSave.push(audioBadge);
      }
      
      if (resolutionBadge) {
        badgesToSave.push(resolutionBadge);
      }
      
      if (reviewBadge) {
        badgesToSave.push(reviewBadge);
      }
      
      // Save the settings
      await api.post('/api/v1/unified-badge-settings', badgesToSave);
      
      // Update last saved timestamp
      setLastSaved(new Date());
      
      // Show success toast
      toast.success('Badge settings saved successfully');
    } catch (err) {
      console.error('Error saving badge settings:', err);
      setError(err instanceof Error ? err : new Error('Failed to save badge settings'));
      
      // Show error toast
      toast.error('Failed to save badge settings');
      
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, [audioBadge, resolutionBadge, reviewBadge]);

  // Handle auto-saving with debounce
  useEffect(() => {
    // Clear any existing timer
    if (saveTimer) {
      clearTimeout(saveTimer);
    }
    
    // If auto-save is enabled and we have at least one badge, set a new timer
    if (autoSave && (audioBadge || resolutionBadge || reviewBadge)) {
      const timer = setTimeout(() => {
        saveSettings();
      }, 2000); // 2-second debounce
      
      setSaveTimer(timer);
    }
    
    // Clean up on unmount
    return () => {
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
    };
  }, [audioBadge, resolutionBadge, reviewBadge, autoSave, saveSettings]);

  // Update methods with proper user_id
  const setAudioBadge = useCallback((settings: AudioBadgeSettings | null) => {
    if (settings) {
      setAudioBadgeState({
        ...settings,
        user_id: userId,
        badge_type: 'audio'
      });
    } else {
      setAudioBadgeState(null);
    }
  }, [userId]);

  const setResolutionBadge = useCallback((settings: ResolutionBadgeSettings | null) => {
    if (settings) {
      setResolutionBadgeState({
        ...settings,
        user_id: userId,
        badge_type: 'resolution'
      });
    } else {
      setResolutionBadgeState(null);
    }
  }, [userId]);

  const setReviewBadge = useCallback((settings: ReviewBadgeSettings | null) => {
    if (settings) {
      setReviewBadgeState({
        ...settings,
        user_id: userId,
        badge_type: 'review'
      });
    } else {
      setReviewBadgeState(null);
    }
  }, [userId]);

  // Reset to defaults
  const resetSettings = useCallback(() => {
    setAudioBadgeState(DEFAULT_AUDIO_BADGE_SETTINGS);
    setResolutionBadgeState(DEFAULT_RESOLUTION_BADGE_SETTINGS);
    setReviewBadgeState(DEFAULT_REVIEW_BADGE_SETTINGS);
  }, []);

  return {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    isLoading,
    isSaving,
    error,
    setAudioBadge,
    setResolutionBadge,
    setReviewBadge,
    saveSettings,
    resetSettings,
    lastSaved
  };
};

export default useUnifiedBadgeSettings;
