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
    // Special handling for badge settings to ensure badge_type is properly set
    let processedData = data;
    
    // Check if this is a badge settings endpoint and contains an array of objects
    if (endpoint.includes('unified-badge-settings') && Array.isArray(data)) {
      // Process each item in the array
      processedData = data.map(item => {
        // Ensure badge_type is one of the valid types if present
        if (item && typeof item === 'object') {
          const validBadgeType = ['audio', 'resolution', 'review'].includes(item.badge_type) 
            ? item.badge_type 
            : null;
          
          // If badge_type is missing or invalid, try to determine it from properties
          if (!validBadgeType && item.properties) {
            if (item.properties.codec_type) {
              console.log('Setting badge_type to audio based on properties');
              return { ...item, badge_type: 'audio' };
            } else if (item.properties.resolution_type) {
              console.log('Setting badge_type to resolution based on properties');
              return { ...item, badge_type: 'resolution' };
            } else if (item.properties.review_sources) {
              console.log('Setting badge_type to review based on properties');
              return { ...item, badge_type: 'review' };
            }
          }
        }
        return item;
      });
      
      // Log what we're about to send after processing
      console.log('Processed badge data:', processedData);
    }
    
    return fetchApi<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(processedData),
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
