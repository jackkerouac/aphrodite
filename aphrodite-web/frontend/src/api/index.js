import axios from 'axios';
import configApi from './config';
import jobsApi from './jobs';

const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

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
  // Base API methods
  get: (url, config) => axiosInstance.get(url, config),
  post: (url, data, config) => axiosInstance.post(url, data, config),
  put: (url, data, config) => axiosInstance.put(url, data, config),
  delete: (url, config) => axiosInstance.delete(url, config),
  // Process API methods
  processSingleItem: (data) => axiosInstance.post('/api/process/item', data),
  processLibrary: (data) => axiosInstance.post('/api/process/library', data)
};
