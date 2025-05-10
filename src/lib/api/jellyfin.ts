import { fetchApi, ApiError } from '../api-client';

export const jellyfin = {
  getLibraries: async (userId: string): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Fetching Jellyfin libraries...');
      const data = await fetchApi<any>(`/jellyfin-libraries/${userId}`);
      console.log('🔧 [apiClient] Received libraries data:', data);
      return data.libraries || [];
    } catch (error) {
      console.error('❌ [apiClient] Error fetching Jellyfin libraries:', error);
      throw error;
    }
  },

  getSettings: async (userId: string): Promise<Record<string, string>> => {
    try {
      console.log('🔧 [apiClient] Fetching Jellyfin settings...');
      console.log(`🔧 Full URL: ${API_BASE_URL}/jellyfin-settings/${userId}`);
      const data = await fetchApi<any>(`/jellyfin-settings/${userId}`);
      console.log('🔧 [apiClient] Received Jellyfin data:', JSON.stringify(data, null, 2));
      const mappedData = {
        url: data.jellyfin_url || '',
        apiKey: data.jellyfin_api_key || '',
        userId: data.jellyfin_user_id || '',
      };
      console.log('🔧 [apiClient] Mapped Jellyfin data:', mappedData);
      return mappedData;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('❗ No Jellyfin settings found, using defaults');
        return { url: '', apiKey: '', userId: '' };
      }
      console.error('❌ [apiClient] Jellyfin settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: Record<string, string>, userId: string): Promise<void> => {
    console.log('🔴 [apiClient] saveSettings received settings:', settings);
    const payload = {
      jellyfin_url: settings.jellyfin_url || settings.url,
      jellyfin_api_key: settings.jellyfin_api_key || settings.apiKey,
      jellyfin_user_id: settings.jellyfin_user_id || settings.userId
    };
    if (!payload.jellyfin_url || !payload.jellyfin_api_key || !payload.jellyfin_user_id) {
      console.error('⚠️ [apiClient] Missing required fields in payload:', payload);
      throw new Error('Missing required fields for Jellyfin settings');
    }
    console.log('📤 [apiClient] Saving Jellyfin settings with payload:', payload);
    return fetchApi<void>(`/jellyfin-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  testConnection: async (settings: Record<string, string>): Promise<void> => {
    console.log('🔴 [apiClient] testConnection received settings:', settings);
    const payload = {
      jellyfin_url: settings.jellyfin_url || settings.url,
      jellyfin_api_key: settings.jellyfin_api_key || settings.apiKey,
      jellyfin_user_id: settings.jellyfin_user_id || settings.userId
    };
    if (!payload.jellyfin_url || !payload.jellyfin_api_key || !payload.jellyfin_user_id) {
      console.error('⚠️ [apiClient] Missing required fields in payload:', payload);
      throw new Error('Missing required fields for Jellyfin connection test');
    }
    console.log('📤 [apiClient] Testing Jellyfin connection with payload:', payload);
    return fetchApi<void>('/test-jellyfin-connection', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

// Import API_BASE_URL here since it's used in getSettings
import { API_BASE_URL } from '../api-client';