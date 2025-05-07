import { fetchApi, ApiError } from '../api-client';

const DEFAULT_USER_ID = '1'; // Assuming this is still relevant here

export const tmdb = {
  getSettings: async (): Promise<Record<string, string>> => {
    try {
      const data = await fetchApi<any>(`/tmdb-settings/${DEFAULT_USER_ID}`);
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

  saveSettings: async (settings: Record<string, string>): Promise<void> => {
    const payload = {
      api_key: settings.apiKey
    };
    return fetchApi<void>(`/tmdb-settings/${DEFAULT_USER_ID}`, {
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