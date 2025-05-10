import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';
import { useUser } from '@/contexts/UserContext';

interface EnabledBadges {
  audio: boolean;
  resolution: boolean;
  review: boolean;
}

export function useEnabledBadges() {
  const { user } = useUser();
  const [enabledBadges, setEnabledBadges] = useState<EnabledBadges>({
    audio: false,
    resolution: false,
    review: false
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnabledBadges = async () => {
      if (!user) return;
      
      try {
        setIsLoading(true);
        setError(null);

        // Use API client methods with user ID from context
        const [audioEnabled, resolutionEnabled, reviewEnabled] = await Promise.all([
          apiClient.audioBadge.isEnabled(user.id),
          apiClient.resolutionBadge.isEnabled(user.id),
          apiClient.reviewBadge.isEnabled(user.id)
        ]);

        // Set the enabled state for each badge type
        setEnabledBadges({
          audio: audioEnabled,
          resolution: resolutionEnabled,
          review: reviewEnabled
        });
      } catch (err) {
        console.error('❌ [useEnabledBadges] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch badge settings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEnabledBadges();
  }, [user]);

  return { enabledBadges, isLoading, error };
}

export default useEnabledBadges;
