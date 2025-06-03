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
  // Get all changes from the changes.yml file
  getChanges() {
    return axiosInstance.get('/api/changes/');
  }
};
