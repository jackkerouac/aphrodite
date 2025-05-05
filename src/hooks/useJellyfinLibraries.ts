import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';

interface Library {
  id: string;
  name: string;
  type: string;
  itemCount: number;
}

export function useJellyfinLibraries() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLibraries = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const librariesData = await apiClient.jellyfin.getLibraries();
        console.log('📚 [useJellyfinLibraries] Fetched libraries:', librariesData);
        setLibraries(librariesData);
      } catch (err) {
        console.error('❌ [useJellyfinLibraries] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch libraries');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLibraries();
  }, []);

  return { libraries, isLoading, error };
}

export default useJellyfinLibraries;
