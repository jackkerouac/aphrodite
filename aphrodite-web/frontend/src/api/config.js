import axios from 'axios'

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
const getBaseURL = () => {
  console.log('DEBUG: Determining baseURL');
  
  // Use the current window location as the base URL to avoid CORS issues
  const currentUrl = window.location.origin;
  console.log('DEBUG: Current window location:', currentUrl);
  
  if (currentUrl) {
    console.log('DEBUG: Using current window location as baseURL');
    return currentUrl;
  }
  
  if (window.APHRODITE_BASE_URL) {
    console.log('DEBUG: Using window.APHRODITE_BASE_URL:', window.APHRODITE_BASE_URL);
    return window.APHRODITE_BASE_URL;
  }
  if (process.env.VUE_APP_API_URL) {
    console.log('DEBUG: Using process.env.VUE_APP_API_URL:', process.env.VUE_APP_API_URL);
    return process.env.VUE_APP_API_URL;
  }
  // If neither is available, use a relative URL (empty string)
  console.log('DEBUG: No base URL found, using relative URL');
  return '';
};

const baseURL = getBaseURL();

// Function to normalize image URLs for all components
const normalizeImageURL = (imagePath) => {
  // If the path is already an absolute URL, return it
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Format path for URL usage
  const cleanPath = imagePath.replace(/\\/g, '/');
  
  // If path starts with 'images/', prepend the base URL and return
  if (cleanPath.startsWith('images/')) {
    return `${baseURL}/${cleanPath}`;
  }
  
  // Otherwise, assume it's an absolute path from the root
  return `${baseURL}${cleanPath.startsWith('/') ? '' : '/'}${cleanPath}`;
};

// Function to configure API client
const configureApiClient = () => {
  // Get the base URL from the window object or current location
  const baseURL = getBaseURL();
  console.log('DEBUG: Configuring API client with baseURL:', baseURL);
  
  // Create a new Axios instance
  const client = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    timeout: 10000
  });
  
  // Add interceptor to log all requests for debugging
  client.interceptors.request.use(config => {
    console.log('DEBUG: Making API request to:', config.url);
    return config;
  });
  
  return client;
};

// Create the API client
const apiClient = configureApiClient();

// Store the configuration function in window
window.configureApiClient = configureApiClient;
window.API_CLIENT_CONFIGURED = true;

export default {
  getConfigFiles() {
    return apiClient.get('/api/config/')
  },
  
  getConfig(fileName) {
    console.log('DEBUG: Fetching config for:', fileName);
    console.log('DEBUG: Using baseURL:', baseURL);
    
    return new Promise((resolve, reject) => {
      apiClient.get(`/api/config/${fileName}`)
        .then(response => {
          console.log('DEBUG: Raw API response:', JSON.stringify(response.data, null, 2));
          console.log('DEBUG: Response status:', response.status);
          resolve(response);
        })
        .catch(error => {
          console.error('DEBUG: API error:', error);
          console.error('DEBUG: Error response:', error.response?.data);
          console.error('DEBUG: Error status:', error.response?.status);
          console.error('DEBUG: Error headers:', error.response?.headers);
          reject(error);
        });
    });
  },
  
  updateConfig(fileName, config) {
    return apiClient.put(`/api/config/${fileName}`, { config })
  },
  
  testJellyfinConnection(credentials) {
    return apiClient.post('/api/check/', credentials)
  },
  
  testConnection(apiType, credentials) {
    return apiClient.post('/api/check/', { api_type: apiType, ...credentials })
  },
  
  // Review Sources API
  getReviewSources() {
    return apiClient.get('/api/review-sources')
  },
  
  updateReviewSource(sourceId, sourceData) {
    return apiClient.put(`/api/review-sources/${sourceId}`, sourceData)
  },
  
  reorderReviewSources(sources) {
    return apiClient.put('/api/review-sources/reorder', { sources })
  },
  
  getReviewSettings() {
    return apiClient.get('/api/review-settings')
  },
  
  updateReviewSettings(settings) {
    return apiClient.put('/api/review-settings', settings)
  },
  
  getEnabledReviewSources() {
    return apiClient.get('/api/review-sources/enabled')
  },
  
  // Helper function to get a normalized image URL
  getImageUrl(imagePath) {
    return normalizeImageURL(imagePath);
  },
  
  // Get available fonts from the fonts directory
  getFonts() {
    return apiClient.get('/api/config/fonts')
  }
}
