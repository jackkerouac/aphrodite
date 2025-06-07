import axios from 'axios';

// Create a function to get the base URL dynamically
const getBaseURL = () => {
  if (window.APHRODITE_BASE_URL) {
    return window.APHRODITE_BASE_URL;
  }
  if (process.env.VUE_APP_API_URL) {
    return process.env.VUE_APP_API_URL;
  }
  return '';
};

// Create axios instance for database API
const dbAxios = axios.create({
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
});

// Add request interceptor to set baseURL dynamically
dbAxios.interceptors.request.use(config => {
  config.baseURL = getBaseURL();
  return config;
});

const databaseApi = {
  /**
   * Get comprehensive database statistics for dashboard
   */
  getStats: () => {
    return dbAxios.get('/api/database/stats');
  },

  /**
   * Get recently processed items
   */
  getRecentItems: (limit = 10) => {
    return dbAxios.get('/api/database/recent-items', {
      params: { limit }
    });
  },

  /**
   * Get processing trends for the last 7 days
   */
  getProcessingTrends: () => {
    return dbAxios.get('/api/database/processing-trends');
  }
};

export default databaseApi;
