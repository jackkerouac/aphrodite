// src/lib/api-client.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
console.log('📡 API_BASE_URL:', API_BASE_URL);

if (import.meta.env.DEV) {
  console.log('📡 Environment variables:', {
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    NODE_ENV: import.meta.env.NODE_ENV,
    DEV: import.meta.env.DEV,
    mode: import.meta.env.MODE,
  });
}

const DEFAULT_USER_ID = '1';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Export ApiError as a named export
export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number = 500) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// Export fetchApi as a named export
export async function fetchApi<T>(
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

// Import and re-export API endpoint modules
import { audioBadge } from './api/audio-badge';
import { resolutionBadge } from './api/resolution-badge';
import { logs } from './api/logs';
import { jellyfin } from './api/jellyfin';
import { omdb } from './api/omdb';
import { tmdb } from './api/tmdb';
import { anidb } from './api/anidb';

const apiClient = {
  audioBadge,
  resolutionBadge,
  logs,
  jellyfin,
  omdb,
  tmdb,
  anidb,
};

export default apiClient;

// Also export API_BASE_URL (though it might not be strictly needed for this specific error)
export { API_BASE_URL };