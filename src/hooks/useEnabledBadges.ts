import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';
import { useUser } from '@/contexts/UserContext';
import { useUnifiedBadgeSettings } from './useUnifiedBadgeSettings';

interface EnabledBadges {
  audio: boolean;
  resolution: boolean;
  review: boolean;
}

export function useEnabledBadges() {
  const { user } = useUser();
  const [enabledBadges, setEnabledBadges] = useState<EnabledBadges>({
    audio: true,
    resolution: true,
    review: true
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Use unified badge settings to determine which badges are available
  const { audioBadge, resolutionBadge, reviewBadge, isLoading: unifiedSettingsLoading } = useUnifiedBadgeSettings({ autoSave: false });

  useEffect(() => {
    const checkUnifiedBadgeSettings = async () => {
      if (!user || unifiedSettingsLoading) return;
      
      try {
        setIsLoading(true);
        setError(null);

        // All badges from unified settings are considered enabled
        // as long as they exist in the unified settings table
        setEnabledBadges({
          audio: !!audioBadge,
          resolution: !!resolutionBadge,
          review: !!reviewBadge
        });
        
        console.log('[useEnabledBadges] Using unified badge settings:', {
          audio: !!audioBadge,
          resolution: !!resolutionBadge,
          review: !!reviewBadge
        });
      } catch (err) {
        console.error('❌ [useEnabledBadges] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch badge settings');
      } finally {
        setIsLoading(false);
      }
    };

    checkUnifiedBadgeSettings();
  }, [user, audioBadge, resolutionBadge, reviewBadge, unifiedSettingsLoading]);

  return { enabledBadges, isLoading, error };
}

export default useEnabledBadges;
