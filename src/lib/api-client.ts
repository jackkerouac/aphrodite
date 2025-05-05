// src/lib/api-client.ts

// Base API URL - adjust based on your environment
// Make sure it points to the correct URL (including port if needed)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
console.log('📡 API_BASE_URL:', API_BASE_URL);

// For debugging, show the full environment variables
if (import.meta.env.DEV) {
  console.log('📡 Environment variables:', {
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    NODE_ENV: import.meta.env.NODE_ENV,
    DEV: import.meta.env.DEV,
    mode: import.meta.env.MODE,
  });
}

// Current user ID - in a real app, this would come from authentication
// For now, we'll use a hardcoded user ID for demo purposes
const DEFAULT_USER_ID = '1';

// Type definitions for the API responses
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// API error class
export class ApiError extends Error {
  status: number;
  
  constructor(message: string, status: number = 500) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// Generic fetch function with error handling
async function fetchApi<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  // Ensure the endpoint starts with '/api/'
  if (!endpoint.startsWith('/')) {
    endpoint = '/' + endpoint;
  }
  if (!endpoint.startsWith('/api/') && !endpoint.includes('/api/')) {
    endpoint = '/api' + endpoint;
  }
  
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`🔍 API REQUEST: ${options.method || 'GET'} ${url}`);
  
  // Log request body if present
  if (options.body) {
    try {
      const bodyObj = JSON.parse(options.body.toString());
      console.log(`📣 REQUEST BODY (parsed):`, bodyObj);
    } catch (e) {
      console.log(`📣 REQUEST BODY (raw):`, options.body);
    }
  }
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    console.log(`📥 API RESPONSE: ${response.status} ${response.statusText}`);
    
    // Parse the JSON response
    try {
      const data = await response.json();
      console.log('📦 API DATA:', data);
      
      // Check if the request was successful
      if (!response.ok) {
        // For test connection endpoints, extract more specific error message if available
        let errorMessage = data.error || data.message || `API error with status ${response.status}`;
        if (data.success === false) {
          errorMessage = data.error || data.message || errorMessage;
        }
        
        console.error('❌ API Error Details:', errorMessage);
        throw new ApiError(errorMessage, response.status);
      }
      
      // Return the data - note: API might return directly or wrapped in a data property
      return data.data || data as T;
    } catch (parseError) {
      console.error('❌ JSON Parse Error:', parseError);
      if (!response.ok) {
        throw new ApiError(`API error with status ${response.status}`, response.status);
      }
      throw new ApiError('Failed to parse server response', 500);
    }
  } catch (error) {
    console.error('❌ API ERROR:', error);
    if (error instanceof ApiError) {
      throw error;
    } else if (error instanceof Error) {
      throw new ApiError(error.message);
    } else {
      throw new ApiError('Unknown error');
    }
  }
}

// API service specific endpoints
export const apiClient = {
  // Jellyfin API endpoints
  jellyfin: {
    // Get Jellyfin settings
    getSettings: async (): Promise<Record<string, string>> => {
      try {
        console.log('🔧 [apiClient] Fetching Jellyfin settings...');
        
        // Log the full URL being requested
        console.log(`🔧 Full URL: ${API_BASE_URL}/jellyfin-settings/${DEFAULT_USER_ID}`);
        
        const data = await fetchApi<any>(`/jellyfin-settings/${DEFAULT_USER_ID}`);
        console.log('🔧 [apiClient] Received Jellyfin data:', JSON.stringify(data, null, 2));
        
        // Convert database field names to expected format
        const mappedData = {
          url: data.jellyfin_url || '',
          apiKey: data.jellyfin_api_key || '',
          userId: data.jellyfin_user_id || '',
        };
        
        console.log('🔧 [apiClient] Mapped Jellyfin data:', mappedData);
        return mappedData;
      } catch (error) {
        // If 404 (not found), return empty values
        if (error instanceof ApiError && error.status === 404) {
          console.log('❗ No Jellyfin settings found, using defaults');
          return { url: '', apiKey: '', userId: '' };
        }
        console.error('❌ [apiClient] Jellyfin settings error:', error);
        throw error;
      }
    },
    
    // Save Jellyfin settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Log the incoming settings
      console.log('🔴 [apiClient] saveSettings received settings:', settings);
      
      // Ensure we have proper format for backend API
      const payload = {
        jellyfin_url: settings.jellyfin_url || settings.url,
        jellyfin_api_key: settings.jellyfin_api_key || settings.apiKey,
        jellyfin_user_id: settings.jellyfin_user_id || settings.userId
      };
      
      // Validate required fields
      if (!payload.jellyfin_url || !payload.jellyfin_api_key || !payload.jellyfin_user_id) {
        console.error('⚠️ [apiClient] Missing required fields in payload:', payload);
        throw new Error('Missing required fields for Jellyfin settings');
      }
      
      console.log('📤 [apiClient] Saving Jellyfin settings with payload:', payload);
      
      return fetchApi<void>(`/jellyfin-settings/${DEFAULT_USER_ID}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    
    // Test Jellyfin connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Log the incoming settings
      console.log('🔴 [apiClient] testConnection received settings:', settings);
      
      // Ensure we have proper format for backend API
      const payload = {
        jellyfin_url: settings.jellyfin_url || settings.url,
        jellyfin_api_key: settings.jellyfin_api_key || settings.apiKey,
        jellyfin_user_id: settings.jellyfin_user_id || settings.userId
      };
      
      // Validate required fields
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
  },
  
  // OMDB API endpoints
  omdb: {
    // Get OMDB settings
    getSettings: async (): Promise<Record<string, string>> => {
      try {
        const data = await fetchApi<any>(`/omdb-settings/${DEFAULT_USER_ID}`);
        // Convert database field names to expected format
        return {
          apiKey: data.api_key || '',
        };
      } catch (error) {
        // If 404 (not found), return empty values
        if (error instanceof ApiError && error.status === 404) {
          console.log('No OMDB settings found, using defaults');
          return { apiKey: '' };
        }
        throw error;
      }
    },
    
    // Save OMDB settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey
      };
      
      return fetchApi<void>(`/omdb-settings/${DEFAULT_USER_ID}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    
    // Test OMDB connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey
      };
      
      return fetchApi<void>('/test-omdb-connection', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  },
  
  // TMDB API endpoints
  tmdb: {
    // Get TMDB settings
    getSettings: async (): Promise<Record<string, string>> => {
      try {
        const data = await fetchApi<any>(`/tmdb-settings/${DEFAULT_USER_ID}`);
        // Convert database field names to expected format
        return {
          apiKey: data.api_key || '',
        };
      } catch (error) {
        // If 404 (not found), return empty values
        if (error instanceof ApiError && error.status === 404) {
          console.log('No TMDB settings found, using defaults');
          return { apiKey: '' };
        }
        throw error;
      }
    },
    
    // Save TMDB settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey
      };
      
      return fetchApi<void>(`/tmdb-settings/${DEFAULT_USER_ID}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    
    // Test TMDB connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey
      };
      
      return fetchApi<void>('/test-tmdb-connection', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  },
  
  // AniDB API endpoints
  anidb: {
    // Get AniDB settings
    getSettings: async (): Promise<Record<string, string>> => {
      try {
        console.log('🔧 [apiClient] Fetching AniDB settings...');
        
        // Log the full URL being requested
        console.log(`🔧 Full URL: ${API_BASE_URL}/anidb-settings/${DEFAULT_USER_ID}`);
        
        const data = await fetchApi<any>(`/anidb-settings/${DEFAULT_USER_ID}`);
        console.log('🔧 [apiClient] Received AniDB data:', JSON.stringify({ ...data, anidb_password: '******' }, null, 2));
        
        // Convert database field names to expected format
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
        // If 404 (not found), return empty values with defaults
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
    
    // Save AniDB settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Log the incoming settings
      console.log('🔴 [apiClient] saveSettings received settings:', { ...settings, password: '******' });
      
      // Ensure we have proper format for backend API
      const payload = {
        anidb_username: settings.anidb_username || settings.username,
        anidb_password: settings.anidb_password || settings.password,
        anidb_client: settings.anidb_client || settings.client || 'aphrodite',
        anidb_version: settings.anidb_version || settings.version || '1',
        anidb_language: settings.anidb_language || settings.language || 'en',
        anidb_cache_expiration: settings.anidb_cache_expiration || settings.cacheExpiration || '60'
      };
      
      // Validate required fields
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
    
    // Test AniDB connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Log the incoming settings
      console.log('🔴 [apiClient] testConnection received settings:', { ...settings, password: '******' });
      
      // Ensure we have proper format for backend API
      const payload = {
        anidb_username: settings.anidb_username || settings.username,
        anidb_password: settings.anidb_password || settings.password,
        anidb_client: settings.anidb_client || settings.client || 'aphrodite',
        anidb_version: settings.anidb_version || settings.version || '1',
        anidb_language: settings.anidb_language || settings.language || 'en',
        anidb_cache_expiration: settings.anidb_cache_expiration || settings.cacheExpiration || '60'
      };
      
      // Validate required fields
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
  },
};

export default apiClient;
