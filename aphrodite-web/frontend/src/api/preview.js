import axios from 'axios';

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
const getBaseURL = () => {
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

const baseURL = getBaseURL();

// Create axios instance
const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
});

export default {
  // Generate a preview poster
  generatePreview: (data) => axiosInstance.post('/api/preview/generate', data),
  
  // Get available badge types
  getBadgeTypes: () => axiosInstance.get('/api/preview/badge-types'),
  
  // Get available poster types
  getPosterTypes: () => axiosInstance.get('/api/preview/poster-types')
};
