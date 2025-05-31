import axios from 'axios'

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
const getBaseURL = () => {
  console.log('DEBUG: Determining baseURL for schedules API');
  
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

// Function to configure API client
const configureApiClient = (useProxy = false) => {
  // Get the base URL from the window object or current location
  const baseURL = getBaseURL();
  console.log('DEBUG: Configuring schedules API client with baseURL:', baseURL);
  console.log('DEBUG: Using proxy:', useProxy);
  
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
    // If using proxy, modify the URL to use the proxy endpoint
    if (useProxy && config.url && config.url.startsWith('/api/')) {
      config.url = config.url.replace('/api/', '/api-proxy/');
      console.log('DEBUG: Using proxy, modified URL:', config.url);
    }
    
    console.log('DEBUG: Making schedules API request to:', config.url);
    return config;
  });
  
  return client;
};

// Create the API client
const apiClient = configureApiClient(window.USE_API_PROXY || false);

export default {
  // Get all schedules
  getSchedules() {
    console.log('DEBUG: Fetching all schedules');
    return apiClient.get('/api/schedules/')
  },
  
  // Get specific schedule by ID
  getSchedule(id) {
    console.log('DEBUG: Fetching schedule:', id);
    return apiClient.get(`/api/schedules/${id}`)
  },
  
  // Create new schedule
  createSchedule(schedule) {
    console.log('DEBUG: Creating schedule:', schedule);
    return apiClient.post('/api/schedules/', schedule)
  },
  
  // Update existing schedule
  updateSchedule(id, schedule) {
    console.log('DEBUG: Updating schedule:', id, schedule);
    return apiClient.put(`/api/schedules/${id}`, schedule)
  },
  
  // Delete schedule
  deleteSchedule(id) {
    console.log('DEBUG: Deleting schedule:', id);
    return apiClient.delete(`/api/schedules/${id}`)
  },
  
  // Run schedule manually
  runSchedule(id) {
    console.log('DEBUG: Running schedule manually:', id);
    return apiClient.post(`/api/schedules/${id}/run`)
  },
  
  // Pause schedule
  pauseSchedule(id) {
    console.log('DEBUG: Pausing schedule:', id);
    return apiClient.post(`/api/schedules/${id}/pause`)
  },
  
  // Resume schedule
  resumeSchedule(id) {
    console.log('DEBUG: Resuming schedule:', id);
    return apiClient.post(`/api/schedules/${id}/resume`)
  },
  
  // Get scheduler status
  getSchedulerStatus() {
    console.log('DEBUG: Fetching scheduler status');
    return apiClient.get('/api/schedules/status')
  },
  
  // Get job execution history
  getJobHistory() {
    console.log('DEBUG: Fetching job execution history');
    return apiClient.get('/api/schedules/history')
  },
  
  // Get common cron patterns
  getCronPatterns() {
    console.log('DEBUG: Fetching cron patterns');
    return apiClient.get('/api/schedules/patterns')
  },
  
  // Validate cron expression
  validateCron(cronExpression) {
    console.log('DEBUG: Validating cron expression:', cronExpression);
    return apiClient.post('/api/schedules/validate-cron', { cron: cronExpression })
  },
  
  // Get Jellyfin libraries
  getJellyfinLibraries() {
    console.log('DEBUG: Fetching Jellyfin libraries');
    return apiClient.get('/api/schedules/jellyfin-libraries')
  }
}
