import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';

export interface BadgeDisplaySettings {
  showResolutionBadge: boolean;
  showAudioBadge: boolean;
  showReviewBadge: boolean;
}

export interface UseBadgePreviewSettingsReturn {
  displaySettings: BadgeDisplaySettings;
  resolutionBadgeSettings: any | null;
  audioBadgeSettings: any | null;
  reviewBadgeSettings: any | null;
  loading: boolean;
  error: Error | null;
  toggleBadge: (badge: keyof BadgeDisplaySettings) => void;
}

export const useBadgePreviewSettings = (): UseBadgePreviewSettingsReturn => {
  const [displaySettings, setDisplaySettings] = useState<BadgeDisplaySettings>({
    showResolutionBadge: true,
    showAudioBadge: true,
    showReviewBadge: true,
  });
  
  const [resolutionBadgeSettings, setResolutionBadgeSettings] = useState<any | null>(null);
  const [audioBadgeSettings, setAudioBadgeSettings] = useState<any | null>(null);
  const [reviewBadgeSettings, setReviewBadgeSettings] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const toggleBadge = (badge: keyof BadgeDisplaySettings) => {
    setDisplaySettings(prev => ({
      ...prev,
      [badge]: !prev[badge]
    }));
  };

  useEffect(() => {
    const fetchAllBadgeSettings = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch resolution badge settings
        try {
          const resolutionData = await apiClient.resolutionBadge.getSettings();
          setResolutionBadgeSettings(resolutionData);
        } catch (resolutionError) {
          console.error('Failed to fetch resolution badge settings:', resolutionError);
          // We continue even if one badge type fails
        }
        
        // Fetch audio badge settings
        try {
          const audioData = await apiClient.audioBadge.getSettings();
          setAudioBadgeSettings(audioData);
        } catch (audioError) {
          console.error('Failed to fetch audio badge settings:', audioError);
          // We continue even if one badge type fails
        }
        
        // Fetch review badge settings
        try {
          const reviewData = await apiClient.reviewBadge.getSettings();
          setReviewBadgeSettings(reviewData);
        } catch (reviewError) {
          console.error('Failed to fetch review badge settings:', reviewError);
          // We continue even if one badge type fails
        }
      } catch (err) {
        console.error('Error fetching badge settings:', err);
        setError(err instanceof Error ? err : new Error('Unknown error fetching badge settings'));
      } finally {
        setLoading(false);
      }
    };
    
    fetchAllBadgeSettings();
  }, []);

  return {
    displaySettings,
    resolutionBadgeSettings,
    audioBadgeSettings,
    reviewBadgeSettings,
    loading,
    error,
    toggleBadge
  };
};
