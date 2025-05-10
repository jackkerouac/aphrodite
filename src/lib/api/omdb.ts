import { fetchApi, ApiError } from '../api-client';

const DEFAULT_USER_ID = '1'; // Assuming this is still relevant here

export const omdb = {
  getSettings: async (userId: string): Promise<Record<string, string>> => {
    try {
      const data = await fetchApi<any>(`/omdb-settings/${userId}`);
      return {
        apiKey: data.api_key || '',
      };
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('No OMDB settings found, using defaults');
        return { apiKey: '' };
      }
      throw error;
    }
  },

  saveSettings: async (settings: Record<string, string>, userId: string): Promise<void> => {
    const payload = {
      api_key: settings.apiKey
    };
    return fetchApi<void>(`/omdb-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  testConnection: async (settings: Record<string, string>): Promise<void> => {
    const payload = {
      api_key: settings.apiKey
    };
    return fetchApi<void>('/test-omdb-connection', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};