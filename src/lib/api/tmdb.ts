import { fetchApi, ApiError } from '../api-client';

const DEFAULT_USER_ID = '1'; // Assuming this is still relevant here

export const tmdb = {
  getSettings: async (userId: string): Promise<Record<string, string>> => {
    try {
      const data = await fetchApi<any>(`/tmdb-settings/${userId}`);
      return {
        apiKey: data.api_key || '',
      };
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('No TMDB settings found, using defaults');
        return { apiKey: '' };
      }
      throw error;
    }
  },

  saveSettings: async (settings: Record<string, string>, userId: string): Promise<void> => {
    const payload = {
      api_key: settings.apiKey
    };
    return fetchApi<void>(`/tmdb-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  testConnection: async (settings: Record<string, string>): Promise<void> => {
    const payload = {
      api_key: settings.apiKey
    };
    return fetchApi<void>('/test-tmdb-connection', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};