import axios from 'axios';
import configApi from './config';
import jobsApi from './jobs';
import jobsExtendedApi from './jobs-extended';
import schedulesApi from './schedules';
import previewApi from './preview';
import changesApi from './changes';
import databaseApi from './database';
import * as databaseExtendedApi from './database-extended';
import { databaseOperations } from './database-operations';

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
export const getApiBaseUrl = () => {
  if (window.APHRODITE_BASE_URL) {
    return window.APHRODITE_BASE_URL;
  }
  if (process.env.VUE_APP_API_URL) {
    return process.env.VUE_APP_API_URL;
  }
  // If neither is available, use a relative URL (empty string)
  // This works because axios will use the current host
  return '';
};

const baseURL = getApiBaseUrl();

// Create axios instance
const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
});

// Debug interceptor
axiosInstance.interceptors.request.use(request => {
  console.log('Starting Request', {
    url: request.url,
    method: request.method,
    data: request.data
  });
  return request;
});

axiosInstance.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
}, error => {
  console.error('API Error:', error.response || error);
  return Promise.reject(error);
});

/**
 * Calculate dynamic timeout based on item count for bulk operations
 * @param {number} itemCount - Number of items being processed
 * @returns {number} Timeout in milliseconds
 */
const calculateBulkTimeout = (itemCount) => {
  // Base timeout for small operations
  const baseTimeout = 10000; // 10 seconds
  
  // Additional time per item (1.5 seconds per item for safety)
  const timePerItem = 1500;
  
  // Calculate timeout with buffer
  const calculated = baseTimeout + (itemCount * timePerItem);
  
  // Minimum 10s, maximum 2 minutes for reasonable limits
  return Math.max(10000, Math.min(calculated, 120000));
};

// Export API methods
export default {
  config: configApi,
  jobs: jobsApi,
  jobsExtended: jobsExtendedApi,
  schedules: schedulesApi,
  preview: previewApi,
  changes: changesApi,
  database: databaseApi,
  databaseExtended: databaseExtendedApi,
  databaseOperations: databaseOperations,
  // Base API methods
  get: (url, config) => axiosInstance.get(url, config),
  post: (url, data, config) => axiosInstance.post(url, data, config),
  put: (url, data, config) => axiosInstance.put(url, data, config),
  delete: (url, config) => axiosInstance.delete(url, config),
  // Process API methods
  processSingleItem: (data) => axiosInstance.post('/api/process/item', data),
  processLibrary: (data) => axiosInstance.post('/api/process/library', data),
  // Bulk operations with dynamic timeout
  postBulkOperation: (url, data, itemCount = 1) => {
    const timeout = calculateBulkTimeout(itemCount);
    console.log(`Bulk operation for ${itemCount} items using timeout: ${timeout}ms (${timeout/1000}s)`);
    return axiosInstance.post(url, data, { timeout });
  }
};
