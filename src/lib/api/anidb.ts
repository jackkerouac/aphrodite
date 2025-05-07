import { fetchApi, ApiError } from '../api-client';

const DEFAULT_USER_ID = '1'; // Assuming this is still relevant here

export const anidb = {
  getSettings: async (): Promise<Record<string, string>> => {
    try {
      console.log('🔧 [apiClient] Fetching AniDB settings...');
      console.log(`🔧 Full URL: ${API_BASE_URL}/anidb-settings/${DEFAULT_USER_ID}`);
      const data = await fetchApi<any>(`/anidb-settings/${DEFAULT_USER_ID}`);
      console.log('🔧 [apiClient] Received AniDB data:', JSON.stringify({ ...data, anidb_password: '******' }, null, 2));
      const mappedData = {
        username: data.anidb_username || '',
        password: data.anidb_password || '',
        client: data.anidb_client || 'aphrodite',
        version: data.anidb_version || '1',
        language: data.anidb_language || 'en',
        cacheExpiration: data.anidb_cache_expiration || '60'
      };
      console.log('🔧 [apiClient] Mapped AniDB data:', { ...mappedData, password: '******' });
      return mappedData;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('❗ No AniDB settings found, using defaults');
        return {
          username: '',
          password: '',
          client: 'aphrodite',
          version: '1',
          language: 'en',
          cacheExpiration: '60'
        };
      }
      console.error('❌ [apiClient] AniDB settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: Record<string, string>): Promise<void> => {
    console.log('🔴 [apiClient] saveSettings received settings:', { ...settings, password: '******' });
    const payload = {
      anidb_username: settings.anidb_username || settings.username,
      anidb_password: settings.anidb_password || settings.password,
      anidb_client: settings.anidb_client || settings.client || 'aphrodite',
      anidb_version: settings.anidb_version || settings.version || '1',
      anidb_language: settings.anidb_language || settings.language || 'en',
      anidb_cache_expiration: settings.anidb_cache_expiration || settings.cacheExpiration || '60'
    };
    if (!payload.anidb_username || !payload.anidb_password) {
      console.error('⚠️ [apiClient] Missing required fields in payload:', { ...payload, anidb_password: '******' });
      throw new Error('Missing required fields for AniDB settings');
    }
    console.log('📤 [apiClient] Saving AniDB settings with payload:', { ...payload, anidb_password: '******' });
    return fetchApi<void>(`/anidb-settings/${DEFAULT_USER_ID}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  testConnection: async (settings: Record<string, string>): Promise<void> => {
    console.log('🔴 [apiClient] testConnection received settings:', { ...settings, password: '******' });
    const payload = {
      anidb_username: settings.anidb_username || settings.username,
      anidb_password: settings.anidb_password || settings.password,
      anidb_client: settings.anidb_client || settings.client || 'aphrodite',
      anidb_version: settings.anidb_version || settings.version || '1',
      anidb_language: settings.anidb_language || settings.language || 'en',
      anidb_cache_expiration: settings.anidb_cache_expiration || settings.cacheExpiration || '60'
    };
    if (!payload.anidb_username || !payload.anidb_password) {
      console.error('⚠️ [apiClient] Missing required fields in payload:', { ...payload, anidb_password: '******' });
      throw new Error('Missing required fields for AniDB connection test');
    }
    console.log('📤 [apiClient] Testing AniDB connection with payload:', { ...payload, anidb_password: '******' });
    return fetchApi<void>('/test-anidb-connection', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

// Import API_BASE_URL here since it's used in getSettings
import { API_BASE_URL } from '../api-client';