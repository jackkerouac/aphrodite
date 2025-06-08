import axios from 'axios';
import configApi from './config';
import jobsApi from './jobs';
import jobsExtendedApi from './jobs-extended';
import schedulesApi from './schedules';
import previewApi from './preview';
import changesApi from './changes';
import databaseApi from './database';
import * as databaseExtendedApi from './database-extended';

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
  // Base API methods
  get: (url, config) => axiosInstance.get(url, config),
  post: (url, data, config) => axiosInstance.post(url, data, config),
  put: (url, data, config) => axiosInstance.put(url, data, config),
  delete: (url, config) => axiosInstance.delete(url, config),
  // Process API methods
  processSingleItem: (data) => axiosInstance.post('/api/process/item', data),
  processLibrary: (data) => axiosInstance.post('/api/process/library', data)
};
