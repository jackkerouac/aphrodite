// src/lib/api.ts

import { fetchApi, ApiError } from './api-client';

// Simple API client for making requests
export const api = {
  get: async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
    return fetchApi<T>(endpoint, {
      method: 'GET',
      ...options,
    });
  },
  
  post: async <T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> => {
    return fetchApi<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    });
  },
  
  put: async <T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> => {
    return fetchApi<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options,
    });
  },
  
  delete: async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
    return fetchApi<T>(endpoint, {
      method: 'DELETE',
      ...options,
    });
  },
};

export { ApiError, fetchApi };
