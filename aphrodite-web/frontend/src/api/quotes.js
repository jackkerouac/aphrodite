/**
 * Quotes API service
 */
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

// Create axios instance for quotes API
const quotesAxios = axios.create({
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 5000
});

// Add request interceptor to set baseURL dynamically
quotesAxios.interceptors.request.use(config => {
  config.baseURL = getBaseURL();
  return config;
});

const quotesApi = {
  /**
   * Get a random quote
   */
  async getRandomQuote() {
    try {
      const response = await quotesAxios.get('/api/quotes/random');
      return response.data;
    } catch (error) {
      console.error('Error fetching random quote:', error);
      // Return fallback quote
      return {
        quote: 'Welcome to Aphrodite - enhancing your media experience!',
        error: error.message
      };
    }
  }
};

export default quotesApi;
