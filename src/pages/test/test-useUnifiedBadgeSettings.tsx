import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { UnifiedBadgeSettings } from '../../types/unifiedBadgeSettings';
import { AxiosResponse } from 'axios';

const TestUseUnifiedBadgeSettings = () => {
  const userId = 1; // Example user ID

  const { data, isLoading, error } = useQuery<UnifiedBadgeSettings[], Error>({
    queryKey: ['unified-badge-settings', userId],
    queryFn: async (): Promise<UnifiedBadgeSettings[]> => {
      const response: AxiosResponse<{ success: boolean; data: UnifiedBadgeSettings[] }> = await api.get(`/api/v1/unified-badge-settings?user_id=${userId}`);
      console.log('API RESPONSE:', response);
      console.log('API DATA:', response.data.data);
      return response.data.data;
    },
    onSuccess: (data: UnifiedBadgeSettings[]) => {
      console.log('useQuery onSuccess data received:', data);
      // Temporarily remove all state setting logic
    },
    onError: (error: unknown) => {
      console.log('useQuery onError:', error);
    },
  } as const);

  return (
    <div>
      <h1>Test UseUnifiedBadgeSettings</h1>
      {isLoading && <p>Loading...</p>}
      {error && <p>Error: {JSON.stringify(error)}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
};

export default TestUseUnifiedBadgeSettings;