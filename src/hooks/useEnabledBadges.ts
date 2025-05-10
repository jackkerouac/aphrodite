import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';

interface EnabledBadges {
  audio: boolean;
  resolution: boolean;
  review: boolean;
}

export function useEnabledBadges() {
  const [enabledBadges, setEnabledBadges] = useState<EnabledBadges>({
    audio: false,
    resolution: false,
    review: false
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnabledBadges = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch all badge settings
        const [audioSettings, resolutionSettings, reviewSettings] = await Promise.all([
          apiClient.badges.getAudioBadgeSettings(),
          apiClient.badges.getResolutionBadgeSettings(),
          apiClient.badges.getReviewBadgeSettings()
        ]);

        // Check if each badge type is enabled
        setEnabledBadges({
          audio: audioSettings?.display || false,
          resolution: resolutionSettings?.display || false,
          review: reviewSettings?.display || false
        });
      } catch (err) {
        console.error('❌ [useEnabledBadges] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch badge settings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEnabledBadges();
  }, []);

  return { enabledBadges, isLoading, error };
}

export default useEnabledBadges;
