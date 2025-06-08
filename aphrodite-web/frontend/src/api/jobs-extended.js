import axios from 'axios'

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
const getBaseURL = () => {
  console.log('DEBUG: Determining baseURL for jobs-extended API');
  
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
console.log('DEBUG: Configuring jobs-extended API client with baseURL:', baseURL);

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
  // Get both active badge jobs and scheduled workflows
  getActiveJobsWithWorkflows: () => axiosInstance.get('/api/jobs/active-jobs-with-workflows'),
  
  // Get detailed information about a specific workflow
  getWorkflowDetails: (workflowId) => axiosInstance.get(`/api/jobs/workflow-details/${workflowId}`)
};
