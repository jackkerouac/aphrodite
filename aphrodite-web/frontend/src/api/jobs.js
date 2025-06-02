import axios from 'axios'

// Get the base URL from the window object if available (injected by Flask),
// fallback to environment variable, or relative URL if neither is available
const getBaseURL = () => {
  console.log('DEBUG: Determining baseURL for jobs API');
  
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
console.log('DEBUG: Configuring jobs API client with baseURL:', baseURL);

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
  // Job related API methods
  getJobs: (page = 1, perPage = 20, jobType = null) => {
    let url = `/api/jobs/?page=${page}&per_page=${perPage}`;
    if (jobType) {
      url += `&type=${jobType}`;
    }
    return axiosInstance.get(url);
  },

  getJob: (jobId) => axiosInstance.get(`/api/jobs/${jobId}`),

  getJobItems: (jobId, page = 1, perPage = 20) => 
    axiosInstance.get(`/api/jobs/${jobId}/items?page=${page}&per_page=${perPage}`),

  deleteJob: (jobId) => axiosInstance.delete(`/api/jobs/${jobId}`),

  // Image related API methods
  getImages: (page = 1, perPage = 20) => 
    axiosInstance.get(`/api/images/list?page=${page}&per_page=${perPage}`),

  getImageUrl: (type, filename) => `${baseURL}/api/images/${type}/${filename}`,

  getImageBase64: (type, filename) => 
    axiosInstance.get(`/api/images/base64/${type}/${filename}`),

  getImagePath: (path) => `${baseURL}/api/images/serve?path=${encodeURIComponent(path)}`,

  downloadImage: (filename) => `${baseURL}/api/images/download/${filename}`
};
