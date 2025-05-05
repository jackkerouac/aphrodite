// src/lib/api-client.ts

// Base API URL - adjust based on your environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

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
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    // Parse the JSON response
    const data = await response.json();
    
    // Check if the request was successful
    if (!response.ok) {
      throw new ApiError(
        data.error || data.message || `API error with status ${response.status}`,
        response.status
      );
    }
    
    // Return the data - note: API might return directly or wrapped in a data property
    return data.data || data as T;
  } catch (error) {
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
        const data = await fetchApi<any>(`/jellyfin-settings/${DEFAULT_USER_ID}`);
        // Convert database field names to expected format
        return {
          url: data.jellyfin_url || '',
          apiKey: data.jellyfin_api_key || '',
          userId: data.jellyfin_user_id || '',
        };
      } catch (error) {
        // If 404 (not found), return empty values
        if (error instanceof ApiError && error.status === 404) {
          console.log('No Jellyfin settings found, using defaults');
          return { url: '', apiKey: '', userId: '' };
        }
        throw error;
      }
    },
    
    // Save Jellyfin settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        jellyfin_url: settings.url,
        jellyfin_api_key: settings.apiKey,
        jellyfin_user_id: settings.userId
      };
      
      return fetchApi<void>(`/jellyfin-settings/${DEFAULT_USER_ID}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    
    // Test Jellyfin connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        jellyfin_url: settings.url,
        jellyfin_api_key: settings.apiKey,
        jellyfin_user_id: settings.userId
      };
      
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
  
  // TVDB API endpoints
  tvdb: {
    // Get TVDB settings
    getSettings: async (): Promise<Record<string, string>> => {
      try {
        const data = await fetchApi<any>(`/tvdb-settings/${DEFAULT_USER_ID}`);
        // Convert database field names to expected format
        return {
          apiKey: data.api_key || '',
          pin: data.pin || '',
        };
      } catch (error) {
        // If 404 (not found), return empty values
        if (error instanceof ApiError && error.status === 404) {
          console.log('No TVDB settings found, using defaults');
          return { apiKey: '', pin: '' };
        }
        throw error;
      }
    },
    
    // Save TVDB settings
    saveSettings: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey,
        pin: settings.pin
      };
      
      return fetchApi<void>(`/tvdb-settings/${DEFAULT_USER_ID}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    
    // Test TVDB connection
    testConnection: async (settings: Record<string, string>): Promise<void> => {
      // Convert to the format expected by the backend
      const payload = {
        api_key: settings.apiKey,
        pin: settings.pin
      };
      
      return fetchApi<void>('/test-tvdb-connection', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  },
};

export default apiClient;
